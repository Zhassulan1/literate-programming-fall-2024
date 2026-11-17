# `test_docs.py` -- Tests for the documentation table
# ===================================================
#
# Each test follows one check of the test case in "Documentation table",
# under "Documentation links" in the specification: the table in
# `src/git_hints/docs.py` and the hint sections of `spec.md` name the same
# links, every link a hint shows comes from the table, and each passage has
# one entry, whose kind fits its URL and whose verification record is the one
# that kind requires. The tests read only files of this repository and never
# use the network; whether the anchors exist on the Git website is checked by
# hand with `scripts/check_doc_links.py`.
import re
import string
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Literal

from git_hints.docs import TABLE, Kind

# The repository root is the parent of this file's directory, so the tests
# find `spec.md` and the package sources whatever the working directory is.
ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "spec.md"
PACKAGE = ROOT / "src" / "git_hints"

# Every link points into the official Git manual.
PREFIX = "https://git-scm.com/docs/"

# The hint sections, by their titles as rendered, without code-span backticks:
# proactive hints under `git-hints` and reactive hints under `git-hints
# explain`.
HINT_SECTIONS = (
    "git-hints",
    "git-hints explain -- git <command> [<args>...]",
)


# Indent one offending item per line under an assertion message.
def listing(items: list[str]) -> str:
    return "".join(f"\n  {item}" for item in items)


# Reading the specification
# -------------------------
#
# The tests need a small part of CommonMark, enough for `spec.md`: the block
# structure, to find the hint sections and their paragraphs, and inline
# parsing, to find links and code spans. A Markdown library would be a new
# dependency for a single test.
#
# ### Fenced code blocks
#
# Lines inside a fenced code block are neither headings nor Markdown text, so
# they are replaced by blank lines before anything else is read. A fence may
# be indented by any amount, since list items indent their content. Three or
# more backticks with another backtick later on the line open a code span, not
# a fenced code block.
_FENCE = re.compile(r"[ \t]*(`{3,}|~{3,})")


def unfence(lines: list[str]) -> list[str]:
    out: list[str] = []
    fence = ""
    for line in lines:
        match = _FENCE.match(line)
        if fence:
            # The closing fence uses the same character, is at least as long
            # as the opening one, and has nothing after it.
            if (
                match
                and match[1][0] == fence[0]
                and len(match[1]) >= len(fence)
                and not line[match.end() :].strip()
            ):
                fence = ""
            out.append("")
        elif match and not (match[1][0] == "`" and "`" in line[match.end() :]):
            fence = match[1]
            out.append("")
        else:
            out.append(line)
    return out


# ### Sections
#
# A level-1 or level-2 heading is written in setext style, as a title line
# underlined with `=` or `-`, or in ATX style, with `#` or `##` before the
# title; `spec.md` uses the setext style for both levels, with each title on
# one line. A title line is not indented as code and does not start a list
# item, after which a line of hyphens would be a thematic break or a list
# item's own heading. A section is a level-2 heading and its body, up to the
# next level-1 or level-2 heading.
_UNDERLINE = re.compile(r" {0,3}(=+|-+)[ \t]*")
_ATX = re.compile(r" {0,3}(#{1,6})(?:[ \t]+(.*?))?(?:[ \t]+#+)?[ \t]*")
_LIST_ITEM = re.compile(r"[ \t]*(?:[-+*]|[0-9]{1,9}[.)])(?:[ \t]|$)")


@dataclass(frozen=True)
class Section:
    title: str
    # The line number in `spec.md` of the first body line.
    first: int
    body: tuple[str, ...]


def sections(lines: list[str]) -> Iterator[Section]:
    # Each level-1 or level-2 heading as (level, title, index of its first
    # line, index of its first body line).
    headings: list[tuple[int, str, int, int]] = []
    for index, line in enumerate(lines):
        atx = _ATX.fullmatch(line)
        if atx:
            if len(atx[1]) <= 2:
                headings.append((len(atx[1]), atx[2] or "", index, index + 1))
            continue
        if (
            index + 1 < len(lines)
            and line.strip()
            and not line.startswith(("    ", "\t"))
            and not _LIST_ITEM.match(line)
            and not _UNDERLINE.fullmatch(line)
        ):
            underline = _UNDERLINE.fullmatch(lines[index + 1])
            if underline:
                level = 1 if underline[1][0] == "=" else 2
                headings.append((level, line, index, index + 2))
    for number, (level, title, _, body) in enumerate(headings):
        end = (
            headings[number + 1][2]
            if number + 1 < len(headings)
            else len(lines)
        )
        if level == 2:
            yield Section(
                title.replace("`", "").strip(), body + 1, tuple(lines[body:end])
            )


# ### Paragraphs
#
# Inline constructs never cross a paragraph boundary, so a body is read one
# paragraph at a time: the lines between blank lines, where a list item or an
# ATX heading also starts a new one. Each line loses its indentation, as
# CommonMark strips it from paragraph lines. Within a paragraph, a code span
# or a link may wrap onto the next lines, so a wrapped code span is read as
# one string.
def paragraphs(lines: tuple[str, ...], first: int) -> Iterator[tuple[int, str]]:
    chunk: list[str] = []
    start = first
    for number, line in enumerate(lines, first):
        if not line.strip() or _LIST_ITEM.match(line) or _ATX.fullmatch(line):
            if chunk:
                yield start, "\n".join(chunk)
            chunk = []
            if _ATX.fullmatch(line):
                yield number, line.lstrip()
                continue
            if not line.strip():
                continue
        if not chunk:
            start = number
        chunk.append(line.lstrip())
    if chunk:
        yield start, "\n".join(chunk)


# ### Links and code spans
#
# A paragraph is read from left to right, as CommonMark reads it:
#
# * A backslash escapes the ASCII punctuation character after it.
# * A run of backticks opens a code span, closed by the next run of the same
#   length; a run without one is literal text. Inside a code span, line
#   endings become spaces, and one space is removed from each end when both
#   ends have one. A link inside a code span is code, not a link.
# * An inline link is `[label](destination "title")`. Its label may contain
#   code spans and balanced brackets, which are read as well; its destination
#   may be enclosed in angle brackets or contain balanced parentheses; its
#   title may be delimited by `"`, `'`, or parentheses, contain parentheses
#   inside quotes, as in "(repo)", and wrap.
#
# The hint sections use no other kind of link, such as reference links or
# autolinks. So that a link this reader misses can't pass unchecked, a manual
# URL outside every link destination and code span is reported as bare, and
# the test fails on it.
_BACKTICKS = re.compile("`+")
_ESCAPE = re.compile(rf"\\([{re.escape(string.punctuation)}])")
_LINK_TAIL = re.compile(
    r"\]\(\s*"
    r"(?P<destination><(?:[^<>\n\\]|\\.)*>"
    r"|(?:[^\s()\\]|\\.|\((?:[^\s()\\]|\\.)*\))+)"
    r"(?:\s+(?:\"(?:[^\"\\]|\\.)*\"|'(?:[^'\\]|\\.)*'|\((?:[^()\\]|\\.)*\)))?"
    r"\s*\)"
)
_BARE = re.compile(re.escape(PREFIX) + r"[^\s()<>\"'`\]]*")

Construct = Literal["link", "code", "bare"]


# A link destination, a code span's content, or a bare URL, and the line of
# `spec.md` it starts on.
@dataclass(frozen=True)
class Reference:
    kind: Construct
    value: str
    line: int


def escaped(text: str, index: int, stop: int) -> bool:
    return (
        text[index] == "\\"
        and index + 1 < stop
        and text[index + 1] in string.punctuation
    )


# Read the backtick run at `index`: return the index where reading goes on
# and the code span's content, or `None` when the run is literal text.
def code_span(text: str, index: int, stop: int) -> tuple[int, str | None]:
    opening = _BACKTICKS.match(text, index, stop)
    assert opening
    closing = re.compile(rf"(?<!`){opening[0]}(?!`)").search(
        text, opening.end(), stop
    )
    if closing is None:
        return opening.end(), None
    content = text[opening.end() : closing.start()].replace("\n", " ")
    if (
        len(content) >= 2
        and content[0] == content[-1] == " "
        and content.strip()
    ):
        content = content[1:-1]
    return closing.end(), content


# Return the index of the `]` that closes the label opened at `index`, or
# `None`.
def label_end(text: str, index: int, stop: int) -> int | None:
    depth = 0
    position = index
    while position < stop:
        char = text[position]
        if escaped(text, position, stop):
            position += 2
            continue
        if char == "`":
            position, _ = code_span(text, position, stop)
            continue
        if char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                return position
        position += 1
    return None


# Yield each link and code span in `text[start:stop]` as (kind, value, start,
# end), where start and end delimit the destination of a link and the whole
# of a code span.
def inline(
    text: str, start: int, stop: int
) -> Iterator[tuple[Construct, str, int, int]]:
    index = start
    while index < stop:
        char = text[index]
        if escaped(text, index, stop):
            index += 2
        elif char == "`":
            end, content = code_span(text, index, stop)
            if content is not None:
                yield "code", content, index, end
            index = end
        elif char == "[":
            label = label_end(text, index, stop)
            tail = (
                None if label is None else _LINK_TAIL.match(text, label, stop)
            )
            if label is None or tail is None:
                index += 1
                continue
            yield from inline(text, index + 1, label)
            destination = tail["destination"]
            if destination.startswith("<"):
                destination = destination[1:-1]
            yield (
                "link",
                _ESCAPE.sub(r"\1", destination),
                tail.start("destination"),
                tail.end("destination"),
            )
            index = tail.end()
        else:
            index += 1


# Every link destination, code span, and bare manual URL in the hint sections
# of `spec`, the text of `spec.md`.
def hint_references(spec: str) -> list[Reference]:
    found = [
        section
        for section in sections(unfence(spec.splitlines()))
        if section.title in HINT_SECTIONS
    ]
    titles = sorted(section.title for section in found)
    assert titles == sorted(HINT_SECTIONS), (
        f"spec.md should have one level-2 section for each of "
        f"{HINT_SECTIONS}; found {titles}"
    )
    references: list[Reference] = []
    for section in found:
        for first, text in paragraphs(section.body, section.first):
            covered: list[tuple[int, int]] = []
            for kind, value, start, end in inline(text, 0, len(text)):
                line = first + text.count("\n", 0, start)
                references.append(Reference(kind, value, line))
                covered.append((start, end))
            for bare in _BARE.finditer(text):
                if not any(a <= bare.start() < b for a, b in covered):
                    line = first + text.count("\n", 0, bare.start())
                    references.append(Reference("bare", bare[0], line))
    return references


# Check 1: the table's URLs
# -------------------------
#
# Besides the URL a hint shows, an anchor that will move records its expected
# replacement; both are URLs of the table and point into the Git manual.
def test_table_urls_point_to_manual() -> None:
    assert TABLE, "The documentation table is empty."
    urls = [entry.url for entry in TABLE] + [
        entry.replacement for entry in TABLE if entry.replacement
    ]
    wrong = [url for url in urls if not url.startswith(PREFIX)]
    assert not wrong, (
        f"These URLs in the documentation table don't start with {PREFIX}:"
        + listing(wrong)
    )


# Check 2: the table and the specification agree
# ----------------------------------------------
#
# Every URL a hint shows appears in a hint section, as a link destination or
# as a code span that names it, such as the URL a test case expects. Every
# manual link in the hint sections is in the table. Both directions compare
# whole strings, so `git-push` doesn't match `git-push#_description`. A
# replacement isn't served yet, so it isn't expected in the hint sections. Code
# spans count only in the first direction: the second compares link
# destinations with the table, so a code span may name a URL outside it.
def test_table_matches_spec() -> None:
    references = hint_references(SPEC.read_text(encoding="utf-8"))
    shown = {ref.value for ref in references if ref.kind != "bare"}
    table = {entry.url for entry in TABLE}
    problems: list[str] = []
    bare = [
        f"spec.md:{ref.line}: {ref.value}"
        for ref in references
        if ref.kind == "bare"
    ]
    if bare:
        problems.append(
            "These URLs in the hint sections of spec.md are neither a link "
            "destination nor a code span, so they can't be checked:"
            + listing(bare)
        )
    missing = [entry.url for entry in TABLE if entry.url not in shown]
    if missing:
        problems.append(
            "These URLs of the documentation table aren't in the hint "
            "sections of spec.md:" + listing(missing)
        )
    unlisted = [
        f"spec.md:{ref.line}: {ref.value}"
        for ref in references
        if ref.kind == "link"
        and ref.value.startswith(PREFIX)
        and ref.value not in table
    ]
    if unlisted:
        problems.append(
            "These links in the hint sections of spec.md aren't in the "
            "documentation table:" + listing(unlisted)
        )
    assert not problems, "\n".join(problems)


# Check 3: links come only from the table
# ---------------------------------------
#
# A manual URL anywhere in the package except `docs.py`, in hint text or
# elsewhere, would be a link that bypasses the table.
def test_only_docs_module_has_urls() -> None:
    modules = sorted(PACKAGE.rglob("*.py"))
    assert PACKAGE / "docs.py" in modules, f"No docs.py in {PACKAGE}"
    offenders = [
        f"{module.relative_to(ROOT).as_posix()}:{number}: {line.strip()}"
        for module in modules
        if module != PACKAGE / "docs.py"
        for number, line in enumerate(
            module.read_text(encoding="utf-8").splitlines(), 1
        )
        if PREFIX in line
    ]
    assert not offenders, (
        f"Only src/git_hints/docs.py may contain {PREFIX}; found:"
        + listing(offenders)
    )


# Check 4: verification records
# -----------------------------
#
# The kind decides how an entry is verified, so it must fit the URL: a whole
# page has no fragment, a text fragment starts with `:~:text=`, an option ID
# is the website's `Documentation/<page>.txt-<option>`, and any other
# fragment is a section anchor.
def kind_of(url: str) -> Kind:
    _, hash_mark, fragment = url.partition("#")
    if not hash_mark:
        return "page"
    if fragment.startswith(":~:text="):
        return "text"
    if fragment.startswith("Documentation/"):
        return "option"
    return "section"


# A section anchor records the Git version it was verified against, an option
# ID or a text fragment records the date of its check against the live page,
# and a whole page records why no passage fits.
REQUIRED = {
    "section": "version",
    "option": "checked",
    "text": "checked",
    "page": "reason",
}


def is_date(text: str) -> bool:
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", text):
        return False
    try:
        date.fromisoformat(text)
    except ValueError:
        return False
    return True


def test_records_have_required_fields() -> None:
    problems: list[str] = []
    for entry in TABLE:
        field = REQUIRED.get(entry.kind)
        if field is None:
            problems.append(f"{entry.url}: unknown kind {entry.kind!r}")
            continue
        if kind_of(entry.url) != entry.kind:
            problems.append(
                f"{entry.url}: kind {entry.kind!r} doesn't fit the URL, "
                f"whose form is {kind_of(entry.url)!r}"
            )
        value = getattr(entry, field)
        if not isinstance(value, str) or not value.strip():
            problems.append(f"{entry.url}: kind {entry.kind!r} needs {field}")
        elif field == "checked" and not is_date(value):
            problems.append(
                f"{entry.url}: checked {value!r} isn't a YYYY-MM-DD date"
            )
    assert not problems, (
        "These entries of the documentation table don't have the kind or "
        "the record their URL requires:" + listing(problems)
    )


# Check 5: one entry per passage
# ------------------------------
#
# Hints that link to the same passage share its entry, so a URL that occurs
# twice is a second record of one link, which could disagree with the first.
def test_entries_are_unique() -> None:
    urls = [entry.url for entry in TABLE]
    repeated = sorted({url for url in urls if urls.count(url) > 1})
    assert not repeated, (
        "These URLs have more than one entry in the documentation table:"
        + listing(repeated)
    )
