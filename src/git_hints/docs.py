# `docs.py` -- The documentation table
# ====================================
#
# Every link to the official Git manual that a hint shows comes from this
# table, as "Documentation links" in the specification requires. The table is
# written by hand: an entry is added or changed together with the hint text in
# the specification, which stays authoritative. `tests/test_docs.py` checks
# that the two agree, and `scripts/check_doc_links.py` re-checks the anchors.
#
# Imports
# -------
#
# ### Standard library
from dataclasses import dataclass
from typing import Literal

# Entries
# -------
#
# The kind of passage an entry links to: a section anchor derived from the
# `.adoc` source, an option ID produced by the website's build, a text
# fragment, or a whole page.
Kind = Literal["section", "option", "text", "page"]


# One link and its verification record. A section anchor records the Git
# version it was verified against; an option ID or a text fragment records the
# date (`YYYY-MM-DD`) of its check against the live page; a whole page records
# why no passage fits. An anchor that will move also records its expected
# replacement.
@dataclass(frozen=True)
class Doc:
    url: str
    kind: Kind
    version: str | None = None
    checked: str | None = None
    reason: str | None = None
    replacement: str | None = None


# The table
# ---------
#
# There is one entry per page and passage, so hints that link to the same
# passage share its entry; the comment before each entry names the hints that
# use it. Entries are grouped by the part of Git they document. Section anchors
# were verified against Git 2.56.1, the release `git-scm.com` serves, and
# option IDs against the live pages.
#
# ### Creating a repository
#
# `not-a-repo` offers both ways to get a repository.
GIT_CLONE_DESCRIPTION = Doc(
    "https://git-scm.com/docs/git-clone#_description",
    "section",
    version="2.56.1",
)
GIT_INIT_DESCRIPTION = Doc(
    "https://git-scm.com/docs/git-init#_description",
    "section",
    version="2.56.1",
)

# ### Staging and committing
#
# `unstaged-changes`, `untracked-files`, and `no-commits` link to staging.
GIT_ADD_DESCRIPTION = Doc(
    "https://git-scm.com/docs/git-add#_description",
    "section",
    version="2.56.1",
)
# `staged-and-unstaged-changes`, `staged-changes`, `many-changed-files`, and
# `no-commits` link to committing.
GIT_COMMIT_DESCRIPTION = Doc(
    "https://git-scm.com/docs/git-commit#_description",
    "section",
    version="2.56.1",
)
# `staged-and-unstaged-changes` and `staged-changes` suggest reviewing the
# staged changes with `git diff --cached`. The page describes several modes,
# so the link goes to the option ID of the one the hints use.
GIT_DIFF_CACHED = Doc(
    "https://git-scm.com/docs/git-diff#Documentation/git-diff.txt"
    "-gitdiffoptions--cached--merge-basecommit--path",
    "option",
    checked="2026-11-17",
)

# ### Ignoring files
#
# `untracked-files` offers ignoring files that look generated or secret.
GITIGNORE_DESCRIPTION = Doc(
    "https://git-scm.com/docs/gitignore#_description",
    "section",
    version="2.56.1",
)
# `tracked-but-ignored` explains that ignore rules don't affect tracked files,
# which NOTES says, and how to stop tracking a file with `git rm --cached`.
GITIGNORE_NOTES = Doc(
    "https://git-scm.com/docs/gitignore#_notes",
    "section",
    version="2.56.1",
)
GIT_RM_CACHED = Doc(
    "https://git-scm.com/docs/git-rm#Documentation/git-rm.txt---cached",
    "option",
    checked="2026-11-17",
)

# ### Branches and HEAD
#
# `changes-on-default-branch` suggests making the changes on a new branch.
GIT_SWITCH_DESCRIPTION = Doc(
    "https://git-scm.com/docs/git-switch#_description",
    "section",
    version="2.56.1",
)
# `detached-head`. Git's development branch adds the explicit anchor
# `[[DETACHED_HEAD]]` before this section, which replaces the derived ID; the
# replacement is recorded so that the link is updated once that release is
# served.
GIT_CHECKOUT_DETACHED_HEAD = Doc(
    "https://git-scm.com/docs/git-checkout#_detached_head",
    "section",
    version="2.56.1",
    replacement="https://git-scm.com/docs/git-checkout#DETACHED_HEAD",
)
# `bisect-in-progress` explains that Git checks out commits for the user to
# test, which the section "Basic bisect commands: start, bad, good" shows step
# by step.
GIT_BISECT_BASIC_COMMANDS = Doc(
    "https://git-scm.com/docs/git-bisect#_basic_bisect_commands_start_bad_good",
    "section",
    version="2.56.1",
)

# ### Remotes
#
# `behind` and `diverged` suggest pulling.
GIT_PULL_DESCRIPTION = Doc(
    "https://git-scm.com/docs/git-pull#_description",
    "section",
    version="2.56.1",
)
# `rebase-after-repeated-integration-failures` suggests `git pull --rebase`.
GIT_PULL_REBASE = Doc(
    "https://git-scm.com/docs/git-pull"
    "#Documentation/git-pull.txt---rebasetruemergesfalseinteractive",
    "option",
    checked="2026-11-17",
)
# `push-ahead` suggests pushing.
GIT_PUSH_DESCRIPTION = Doc(
    "https://git-scm.com/docs/git-push#_description",
    "section",
    version="2.56.1",
)
# `diverged` and `push-rejected-non-fast-forward` explain why a push of
# diverged history is rejected.
GIT_PUSH_NOTE_ABOUT_FAST_FORWARDS = Doc(
    "https://git-scm.com/docs/git-push#_note_about_fast_forwards",
    "section",
    version="2.56.1",
)
# `no-upstream-branch` and `unpushed-branches` push a branch and record its
# upstream. The section is included from `urls-remotes.adoc` under the
# explicit anchor `[[UPSTREAM-BRANCHES]]`.
GIT_PUSH_UPSTREAM_BRANCHES = Doc(
    "https://git-scm.com/docs/git-push#UPSTREAM-BRANCHES",
    "section",
    version="2.56.1",
)
# `stale-fetch` suggests fetching. That hint is specified but not implemented
# yet, so no hint uses this entry; it is here because the specification's hint
# section names the link.
GIT_FETCH_DESCRIPTION = Doc(
    "https://git-scm.com/docs/git-fetch#_description",
    "section",
    version="2.56.1",
)

# ### Conflicts and paused operations
#
# `merge-conflicts`, in both hint modules. Git's development branch moves the
# explanation of conflict markers to the new `gitmergeconflicts` page, so the
# replacement is recorded until that release is served.
GIT_MERGE_HOW_CONFLICTS_ARE_PRESENTED = Doc(
    "https://git-scm.com/docs/git-merge#_how_conflicts_are_presented",
    "section",
    version="2.56.1",
    replacement="https://git-scm.com/docs/gitmergeconflicts#markers",
)
# `operation-in-progress`, while conflicts remain, asks the user to edit each
# conflicted file and stage it, as HOW TO RESOLVE CONFLICTS says. The section
# moves to `gitmergeconflicts` on Git's development branch, like the one
# above, so its replacement is recorded too.
GIT_MERGE_HOW_TO_RESOLVE_CONFLICTS = Doc(
    "https://git-scm.com/docs/git-merge#_how_to_resolve_conflicts",
    "section",
    version="2.56.1",
    replacement="https://git-scm.com/docs/gitmergeconflicts#resolve",
)
# `pull-blocked-local-changes`: PRE-MERGE CHECKS says that a merge, and so a
# pull, stops without doing anything when local changes overlap with the files
# it must update.
GIT_MERGE_PRE_MERGE_CHECKS = Doc(
    "https://git-scm.com/docs/git-merge#_pre_merge_checks",
    "section",
    version="2.56.1",
)
# `operation-in-progress` links to the page of the paused operation, whose
# entry the mapping `OPERATIONS` below selects. The rebase entry is also used
# by `rebase-after-repeated-integration-failures`. The DESCRIPTION of
# `git-revert` does not mention a paused revert, so its entry links to
# SEQUENCER SUBCOMMANDS, which describes `--continue` and `--abort`.
GIT_MERGE_DESCRIPTION = Doc(
    "https://git-scm.com/docs/git-merge#_description",
    "section",
    version="2.56.1",
)
GIT_REBASE_DESCRIPTION = Doc(
    "https://git-scm.com/docs/git-rebase#_description",
    "section",
    version="2.56.1",
)
GIT_CHERRY_PICK_DESCRIPTION = Doc(
    "https://git-scm.com/docs/git-cherry-pick#_description",
    "section",
    version="2.56.1",
)
GIT_REVERT_SEQUENCER_SUBCOMMANDS = Doc(
    "https://git-scm.com/docs/git-revert#_sequencer_subcommands",
    "section",
    version="2.56.1",
)

# The entry for each operation that `operation-in-progress` explains, keyed by
# the name `Operations.paused` reports.
OPERATIONS: dict[str, Doc] = {
    "merge": GIT_MERGE_DESCRIPTION,
    "rebase": GIT_REBASE_DESCRIPTION,
    "cherry-pick": GIT_CHERRY_PICK_DESCRIPTION,
    "revert": GIT_REVERT_SEQUENCER_SUBCOMMANDS,
}

# ### Stash
#
# `stash-entries` and `stash-local-changes` explain what a stash entry is.
GIT_STASH_DESCRIPTION = Doc(
    "https://git-scm.com/docs/git-stash#_description",
    "section",
    version="2.56.1",
)
# `stash-entries` asks whether to apply or drop the entries.
GIT_STASH_COMMANDS = Doc(
    "https://git-scm.com/docs/git-stash#_commands",
    "section",
    version="2.56.1",
)
# `pull-blocked-local-changes`: the example "Pulling into a dirty tree" shows
# stashing, pulling, and restoring the changes. Git's development branch adds
# the explicit anchor `[[EXAMPLES]]` before this section, which replaces the
# derived ID, so the replacement is recorded.
GIT_STASH_EXAMPLES = Doc(
    "https://git-scm.com/docs/git-stash#_examples",
    "section",
    version="2.56.1",
    replacement="https://git-scm.com/docs/git-stash#EXAMPLES",
)

# ### Configuration
#
# `commit-identity` links to `user.name`, whose entry also describes
# `user.email`.
GIT_CONFIG_USER_NAME = Doc(
    "https://git-scm.com/docs/git-config#Documentation/git-config.txt-username",
    "option",
    checked="2026-11-17",
)

# Every entry, in the order of definition.
TABLE: tuple[Doc, ...] = tuple(
    value for value in tuple(globals().values()) if isinstance(value, Doc)
)
