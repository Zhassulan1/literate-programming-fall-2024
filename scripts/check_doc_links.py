# `check_doc_links.py` -- Re-check the documentation table
# ========================================================
#
# This script re-checks every entry of the documentation table in
# `src/git_hints/docs.py`, as "Maintenance script" in the specification
# defines. It is run by hand, not by the test suite:
#
#     uv run python scripts/check_doc_links.py <git-checkout> <tag> [--site]
#
# where `<git-checkout>` is a clone of the Git source and `<tag>` is the
# release that `git-scm.com` serves. The script changes no file and does not
# fetch, so the caller runs `git -C <git-checkout> fetch origin` first; the
# result then also tells which anchors Git's development branch,
# `origin/master`, is about to move.
#
# The website renders each page from `Documentation/<page>.adoc`, so a section
# anchor can be checked offline by finding the section titles and anchors in
# that source and deriving IDs as the website's renderer, Asciidoctor, does.
# Option IDs come from the website's own build, and a text fragment quotes the
# rendered page, so both are checked only against the live pages, with
# `--site`.
#
# Imports
# -------
#
# ### Standard library
import argparse
import datetime
import http.client
import posixpath
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path

# ### Local
from git_hints.docs import TABLE, Doc

# Constants
# ---------
#
# Every URL in the table starts with this prefix, followed by the page name.
SITE = "https://git-scm.com/docs/"

# Git's development branch; an anchor that is missing there will move.
MASTER = "origin/master"

# A generic client name, so that a request identifies no user or project.
USER_AGENT = "Mozilla/5.0 (compatible; doc-link-check)"

# Seconds to wait for the website before reporting a page as unreachable.
TIMEOUT = 30

# An output line that starts with one of these makes the script exit 1; this
# includes `missing-site`.
FAILURES = ("missing", "unreachable", "replacement-missing")

# Exit codes: every check passed, a check failed, or nothing could be checked.
EXIT_OK = 0
EXIT_FAILED = 1
EXIT_USAGE = 2

PROG = "check_doc_links.py"


# Output
# ------
#
# Print one result line and remember whether any line reports a failure.
# Lines are flushed at once, so that progress shows while `--site` waits for
# the website.
class Report:
    def __init__(self) -> None:
        self.failed = False

    def line(self, status: str, *fields: str) -> None:
        print(" ".join((status, *fields)), flush=True)
        if status.startswith(FAILURES):
            self.failed = True


# Running Git
# -----------
#
# Git could not be started, so nothing can be checked.
class GitLaunchError(Exception):
    pass


# Run Git in the checkout and return its standard output, or `None` when Git
# exits nonzero. The documentation is UTF-8, so output is decoded as UTF-8
# whatever the locale, replacing invalid bytes rather than failing.
def git(checkout: Path, *args: str) -> str | None:
    try:
        completed = subprocess.run(
            ["git", "-C", str(checkout), *args],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            check=False,
        )
    except OSError as error:
        raise GitLaunchError(f"could not launch Git: {error}") from error
    if completed.returncode != 0:
        return None
    return completed.stdout.decode("utf-8", errors="replace")


# Whether `ref` names a commit in the checkout.
def has_commit(checkout: Path, ref: str) -> bool:
    found = git(
        checkout, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"
    )
    return found is not None


# Reading a page
# --------------
#
# Asciidoctor's include directive: a target without surrounding whitespace,
# then attributes in brackets. A leading backslash escapes the directive, which
# is then shown as text.
INCLUDE = re.compile(r"(\\?)include::([^\s\[](?:[^\[]*[^\s\[])?)\[(.*)\]")

# Asciidoctor's conditional directives. The script collects titles whatever
# the condition, so these lines are dropped and the lines between them kept.
# The single-line form `ifdef::<attribute>[<text>]` keeps its text.
CONDITIONAL = re.compile(r"(\\?)(ifdef|ifndef|ifeval|endif)::(\S*?)\[(.*)\]")


# Read the pages of one checkout. Each page is read once per ref, and each
# unresolved include is reported once per ref, however many pages include it.
class Source:
    def __init__(self, checkout: Path, report: Report) -> None:
        self.checkout = checkout
        self.report = report
        self.pages: dict[tuple[str, str], frozenset[str]] = {}
        self.unresolved: set[tuple[str, str]] = set()

    # The IDs of `page` at `ref`; none when the page does not exist there.
    def ids(self, ref: str, page: str) -> frozenset[str]:
        key = (ref, page)
        if key not in self.pages:
            path = f"Documentation/{page}.adoc"
            text = self.show(ref, path)
            lines = [] if text is None else list(self.lines(ref, path, text))
            self.pages[key] = frozenset(collect_ids(lines))
        return self.pages[key]

    # One file at `ref`, or `None` when it does not exist there.
    def show(self, ref: str, path: str) -> str | None:
        return git(self.checkout, "show", f"{ref}:{path}")

    # The lines of the file at `path`, whose content is `text`, with each
    # include replaced by the lines of the included file. Trailing whitespace
    # is removed, as Asciidoctor does before parsing. `stack` holds the files
    # being included, so that an include cycle ends.
    def lines(
        self, ref: str, path: str, text: str, stack: Sequence[str] = ()
    ) -> Iterator[str]:
        for raw in text.removesuffix("\n").split("\n"):
            line = raw.rstrip()
            include = INCLUDE.fullmatch(line)
            if include and not include[1]:
                yield from self.include(ref, path, include[2], (*stack, path))
                continue
            conditional = CONDITIONAL.fullmatch(line)
            if conditional and not conditional[1]:
                if conditional[2] in ("ifdef", "ifndef") and conditional[4]:
                    yield conditional[4]
                continue
            yield line[1:] if include or conditional else line

    # The lines of the file that `target` names, relative to the directory of
    # the including file `path`. A target that names an attribute, such as
    # `{build_dir}`, is a file of the website's build, not of the source, so
    # it is reported as written; a missing file, or one that is already being
    # included, is reported by its path in the checkout. Either is skipped.
    def include(
        self, ref: str, path: str, target: str, stack: Sequence[str]
    ) -> Iterator[str]:
        text = None
        if "{" in target:
            name = target
        else:
            name = posixpath.normpath(
                posixpath.join(posixpath.dirname(path), target)
            )
            if name not in stack:
                text = self.show(ref, name)
        if text is None:
            if (ref, name) not in self.unresolved:
                self.unresolved.add((ref, name))
                self.report.line("unresolved", ref, name)
            return
        yield from self.lines(ref, name, text, stack)


# Finding titles and anchors
# --------------------------
#
# A title in the `==` to `======` style, with optional closing markers.
ATX_TITLE = re.compile(r"(={2,6})[ \t]+(.+?)(?:[ \t]+\1)?")

# The characters that underline a section title; `=` underlines only the
# document title.
UNDERLINE = "-~^+"

# The characters whose runs of four or more delimit a block.
DELIMITER = "-.=*+/"

# A table delimiter.
TABLE_DELIMITER = re.compile(r"\|={3,}")

# An anchor line `[[ID]]` or `[[ID,reftext]]`, which gives its ID to the block
# or section after it.
BLOCK_ANCHOR = re.compile(r"\[\[((?:[^\W\d]|:)[\w:.-]*)(?:,.*)?\]\]")

# An inline anchor `[[ID]]` anywhere in a line; a backslash escapes it.
INLINE_ANCHOR = re.compile(r"(?<!\\)\[\[((?:[^\W\d]|:)[\w:.-]*)(?:,.*?)?\]\]")

# An anchor that ends a title after a space, as in `TITLE [[ID]]`; as in
# Asciidoctor, it gives the section its ID the way an anchor line does.
TRAILING_ANCHOR = re.compile(r" \[\[((?:[^\W\d]|:)[\w:.-]*)(?:, *.+)?\]\]$")

# A block attribute line such as `[synopsis]`, which belongs to the block after
# it.
ATTRIBUTE_LINE = re.compile(r"\[(?:|[\w.#%{,\"'].*)\]")

# A passthrough, `+++<text>+++` or `pass:[<text>]`, whose text Asciidoctor
# outputs as written, so that `+++[[dco]]+++` in `MyFirstContribution` is no
# anchor.
PASSTHROUGH = re.compile(r"\+\+\+.*?\+\+\+|pass:[a-z,]*\[.*?\]")


# The explicit anchors in `text`, outside passthroughs.
def inline_anchors(text: str) -> list[str]:
    return INLINE_ANCHOR.findall(PASSTHROUGH.sub("", text))


# Whether `line` consists of one character repeated.
def uniform(line: str) -> bool:
    return line != "" and line == line[0] * len(line)


# Whether `underline` underlines `title` with `chars`: its length differs from
# the title's by at most one.
def underlines(underline: str, title: str, chars: str) -> bool:
    return (
        uniform(underline)
        and underline[0] in chars
        and abs(len(underline) - len(title)) <= 1
    )


# Whether `line` opens a delimited block, which ends at the next identical
# line.
def opens_block(line: str) -> bool:
    if len(line) >= 4 and uniform(line) and line[0] in DELIMITER:
        return True
    return TABLE_DELIMITER.fullmatch(line) is not None


# Whether `line` can be the text of an underlined title: as in Asciidoctor, it
# contains a letter, digit, or underscore. Without this rule, the list
# continuation `+` followed by the `--` that opens an open block, which Git's
# option lists use throughout, would be a title.
def can_be_title(line: str) -> bool:
    return re.search(r"\w", line) is not None


# The text of the section title that starts at `lines[i]` and the number of
# lines it takes, or `None` when no title starts there.
def section_title(lines: Sequence[str], i: int) -> tuple[str, int] | None:
    atx = ATX_TITLE.fullmatch(lines[i])
    if atx:
        return atx[2], 1
    if (
        i + 1 < len(lines)
        and can_be_title(lines[i])
        and underlines(lines[i + 1], lines[i], UNDERLINE)
    ):
        return lines[i], 2
    return None


# The renderer substitutes a title before deriving its ID from it. These
# substitutions all produce punctuation or an HTML entity, which the
# derivation deletes, so deleting what they replace gives the same ID; the
# derivation alone would instead keep the name of an attribute and turn the
# spaces and hyphens of an em dash into separators. Asciidoctor replaces:
#
# * a reference to one of its character attributes, such as `{caret}` in
#   `gitrevisions`, with that character, and Git's `{litdd}` with the entities
#   for `--`; `{sp}` is a space. A reference to another attribute is left as
#   written;
# * ` -- ` with an em dash between thin spaces, which takes the place of both
#   spaces, as in `INTERNALS -- SPARSE CHECKOUT` (`_internalssparse_checkout`)
#   of `git-sparse-checkout`, and `--` between word characters with an em
#   dash;
# * `...` with an ellipsis, `(C)`, `(R)`, and `(TM)` with symbols, and `->`,
#   `=>`, `<-`, and `<=` with arrows.
#
# Before these, a link macro, a URL or a target after `link:` or `mailto:`
# followed by `[<text>]`, is replaced by its text, or by the target when the
# text is empty, since the link element's tags are deleted from the rendered
# title; `MyFirstContribution` has `https://discord.gg/GRFVkzgxRd[#discord] on
# Discord` (`_discord_on_discord`).
LINK_MACRO = re.compile(
    r"(?P<prefix>link:|mailto:)?"
    r"(?P<target>(?(prefix)|(?:https?|ftp|irc)://)[^\s\[\]]+)"
    r"\[(?P<text>[^\]]*)\]"
)
CHARACTER_ATTRIBUTE = re.compile(
    r"\{(?:amp|apos|asterisk|backslash|backtick|blank|brvbar|caret|deg|empty"
    r"|endsb|gt|ldquo|litdd|lsquo|lt|nbsp|plus|pp|quot|rdquo|rsquo|startsb"
    r"|tilde|two-colons|two-semicolons|vbar|wj|zwsp)\}"
)
REPLACEMENT = re.compile(
    r"(?:^| )--(?: |$)|(?<=\w)--(?=\w)|\.\.\.|\((?:C|R|TM)\)|->|=>|<-|<="
)


def render_title(title: str) -> str:
    title = LINK_MACRO.sub(lambda link: link["text"] or link["target"], title)
    title = CHARACTER_ATTRIBUTE.sub("", title.replace("{sp}", " "))
    return REPLACEMENT.sub("", title)


# Derive a section ID from its rendered title, as "Choosing and deriving
# anchors" in the specification describes. The prefix `_` is added before runs
# of separators are joined, so a title starting with a separator gets one `_`,
# not two, as in Asciidoctor.
def derive_id(title: str) -> str:
    kept = re.sub(r"[^\w \-.]", "", title.lower())
    return re.sub(r"[ _.-]+", "_", "_" + kept).rstrip("_")


# Every ID of a page, in the order of the lines, from its lines with includes
# resolved: each explicit anchor, and the ID of each section title without an
# explicit anchor line before it or an anchor at its end. A derived ID that
# already occurs gets the suffix `_2`, `_3`, and so on.
def collect_ids(lines: Sequence[str]) -> list[str]:
    # The IDs found so far; a dictionary keeps their order.
    ids: dict[str, None] = {}
    # Whether an explicit anchor line gives the next title its ID. As in
    # Asciidoctor, attribute lines, comments, and blank lines may come
    # between them; `user-manual` has `[[todo]]`, then `[appendix]`, then the
    # title.
    anchored = False
    # The document title on the first line is not a section.
    i = 2 if len(lines) > 1 and underlines(lines[1], lines[0], "=") else 0
    while i < len(lines):
        line = lines[i]
        # An anchor line is never a title, even above a block delimiter of
        # the same length.
        anchor = BLOCK_ANCHOR.fullmatch(line)
        title = None if anchor else section_title(lines, i)
        if anchor:
            ids[anchor[1]] = None
            anchored = True
            i += 1
        elif title is not None:
            text, size = title
            # Each anchor in the title adds its ID; a trailing one takes the
            # place of the derived ID.
            anchors = inline_anchors(text)
            if not anchored and TRAILING_ANCHOR.search(text) is None:
                base = derive_id(render_title(INLINE_ANCHOR.sub("", text)))
                derived, count = base, 2
                while derived in ids:
                    derived, count = f"{base}_{count}", count + 1
                ids[derived] = None
            ids.update(dict.fromkeys(anchors))
            anchored = False
            i += size
        elif opens_block(line):
            # A block contains no titles; skip to its closing line, or to the
            # end when it is not closed.
            close = i + 1
            while close < len(lines) and lines[close] != line:
                close += 1
            anchored = False
            i = close + 1
        else:
            ids.update(dict.fromkeys(inline_anchors(line)))
            anchored = anchored and (
                line == ""
                or line.startswith("//")
                or ATTRIBUTE_LINE.fullmatch(line) is not None
            )
            i += 1
    return list(ids)


# Checking the website
# --------------------
#
# The text and the `id` attributes of one live page. The contents of `script`
# and `style` elements are not text a reader sees, so they are left out.
class PageParser(HTMLParser):
    HIDDEN = ("script", "style")

    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.parts: list[str] = []
        self.hidden = 0

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self.ids.update(
            value for name, value in attrs if name == "id" and value
        )
        if tag in self.HIDDEN:
            self.hidden += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in self.HIDDEN and self.hidden:
            self.hidden -= 1

    def handle_data(self, data: str) -> None:
        if not self.hidden:
            self.parts.append(data)


@dataclass(frozen=True)
class LivePage:
    ids: frozenset[str]
    # The page's text, with HTML tags removed, entities decoded, each run of
    # whitespace collapsed to one space, and lowercased.
    text: str


# Collapse each run of whitespace to one space and lowercase, so that a phrase
# matches the page text ignoring case and line breaks.
def normalize(text: str) -> str:
    return " ".join(text.split()).lower()


# Download each page once; a page that cannot be downloaded is `None`, and
# the reason is shown on standard error.
class Site:
    def __init__(self) -> None:
        self.pages: dict[str, LivePage | None] = {}

    def page(self, url: str) -> LivePage | None:
        if url not in self.pages:
            self.pages[url] = self.download(url)
        return self.pages[url]

    def download(self, url: str) -> LivePage | None:
        request = urllib.request.Request(
            url, headers={"User-Agent": USER_AGENT}
        )
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                charset = response.headers.get_content_charset() or "utf-8"
                body = response.read().decode(charset, errors="replace")
        except (OSError, http.client.HTTPException, LookupError) as error:
            print(f"{PROG}: cannot download {url}: {error}", file=sys.stderr)
            return None
        parser = PageParser()
        parser.feed(body)
        parser.close()
        return LivePage(frozenset(parser.ids), normalize("".join(parser.parts)))


# The number of occurrences of `phrase` in `text`, overlapping ones included,
# since a text fragment must match exactly one place.
def occurrences(text: str, phrase: str) -> int:
    count, start = 0, text.find(phrase)
    while start != -1:
        count, start = count + 1, text.find(phrase, start + 1)
    return count


# Checking entries
# ----------------
#
# A URL split into the page URL, the page name, and the fragment, which is
# percent-decoded as a browser decodes it before matching.
def split_url(url: str) -> tuple[str, str, str]:
    page_url, _, fragment = url.partition("#")
    return page_url, page_url.removeprefix(SITE), urllib.parse.unquote(fragment)


# Check one entry: its section anchor in the source, and, with `site`, its
# anchor, option ID, or text fragment on the live page.
def check(
    entry: Doc,
    tag: str,
    source: Source,
    site: Site | None,
    report: Report,
) -> None:
    page_url, page, fragment = split_url(entry.url)
    if not fragment:
        report.line("whole-page", entry.url, *filter(None, [entry.reason]))
    elif entry.kind in ("option", "text"):
        if site is None:
            report.line("unchecked", entry.checked or "-", entry.url)
    else:
        if fragment not in source.ids(tag, page):
            report.line("missing", entry.url)
        elif fragment not in source.ids(MASTER, page):
            report.line("moves", entry.url)
        else:
            report.line("ok", entry.url)
        if entry.replacement is not None:
            _, new_page, new_fragment = split_url(entry.replacement)
            if new_fragment not in source.ids(MASTER, new_page):
                report.line("replacement-missing", entry.url)
    if site is None:
        return
    # A whole page is only checked to be reachable.
    live = site.page(page_url)
    if live is None:
        report.line("unreachable", entry.url)
    elif fragment and entry.kind == "text":
        phrase = normalize(fragment.removeprefix(":~:text="))
        found = occurrences(live.text, phrase) == 1
        site_status(report, found, entry.url)
    elif fragment:
        site_status(report, fragment in live.ids, entry.url)


# Report a site check, with the date to copy into the entry's record.
def site_status(report: Report, found: bool, url: str) -> None:
    if found:
        report.line("ok", datetime.date.today().isoformat(), url)
    else:
        report.line("missing-site", url)


# Main
# ----
def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog=PROG,
        description="Re-check the documentation table of git-hints.",
    )
    parser.add_argument(
        "checkout", metavar="git-checkout", type=Path, help="a clone of Git"
    )
    parser.add_argument("tag", help="the release that git-scm.com serves")
    parser.add_argument(
        "--site",
        action="store_true",
        help="also check each page on git-scm.com",
    )
    args = parser.parse_args(argv)
    report = Report()
    try:
        for ref in (args.tag, MASTER):
            if not has_commit(args.checkout, ref):
                print(
                    f"{PROG}: {ref} is not in {args.checkout}", file=sys.stderr
                )
                return EXIT_USAGE
        source = Source(args.checkout, report)
        site = Site() if args.site else None
        for entry in TABLE:
            check(entry, args.tag, source, site, report)
    except GitLaunchError as error:
        print(f"{PROG}: {error}", file=sys.stderr)
        return EXIT_USAGE
    return EXIT_FAILED if report.failed else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
