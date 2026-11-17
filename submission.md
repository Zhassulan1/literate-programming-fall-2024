Project 2 submission
====================

Team name: git-hints

The specification consists of the file [spec.md](spec.md). The section
"Development strategy" lists the team's changes to it.

Draft submission
----------------

The build and run test statements below summarize LLM output on each team
member's computer. The draft used the earlier prompt wording "Verify that you
can compile and run the project in the current git repo."

### Aknur Seidazym

GitHub userid: aknur-maga

#### Contributions

Wrote the "Implementation Strategy" section of `spec.md` and reviewed it with an
LLM over three rounds, which the table below summarizes. After the instructor's
pull-request review, changed the repository-inspection requirement from
descriptive "never" wording to normative "must not" wording, removed the
Architecture subsection that only summarized the existing implementation, and
reduced repeated command examples in the `stale-fetch` conditions, and merged
the reactive-error-handling requirement into the existing reactive-hints
section, then removed the redundant Git Command Execution summary after
confirming its requirements were already in Language and libraries.

#### Build and run test

OpenAI GPT-6.1-Sol (default effort), macOS, Python 3.14.6: the LLM built and
installed the `git-hints` wheel in a temporary virtual environment, ran
`git-hints --help`, `git-hints`, and `git-hints explain -- git status --short`
successfully, reported that Ruff and ty passed, and ran the test suite with all
58 tests passing.

#### Specification review rounds

All three rounds reviewed only the "Implementation Strategy" section with the
prompt shown under Last specification review below, using OpenAI Codex
(GPT-6.1-Sol). Later rounds 4–7 of the same section are in Madina Amangeldi's
block.

| Round | Findings | Main changes made                                                                                                                                                                   |
| ----- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1     | 3        | Clarified lossless filename decoding and invalid UTF-8 handling; added `GIT_OPTIONAL_LOCKS=0` for read-only inspection; specified stdin, stdout, and stderr handling for `explain`. |
| 2     | 1        | Specified real-time stderr streaming while retaining output for hint matching; added an interactive prompt test.                                                                    |
| 3     | 0        | No further changes.                                                                                                                                                                 |

Later reversed: before round 4, the decoding from round 1 was replaced (Git
output is decoded as UTF-8 with replacement instead of with `os.fsdecode()`),
and the streaming from round 2 was replaced (`explain` now prints captured
standard error after Git exits instead of streaming it).

#### Last specification review

Prompting OpenAI Codex (GPT-6.1-Sol, default reasoning effort) with the
following prompt produced the output below. Nothing in it is struck through,
because the review reported no findings.

```text
Review ONLY the "Implementation Strategy" section of spec.md. Check for technical inaccuracies, contradictions with existing requirements, missing implementation decisions, and ambiguous or untestable statements. Do not review other sections. Do not modify any files. Report only relevant, actionable findings in a numbered list, followed by the total number of findings. Avoid stylistic suggestions and unnecessary expansion.
```

```
I’ll recheck the current “Implementation Strategy” section only.

• Explored
  └ Read spec.md

Total findings: 0.
```

### Madina Amangeldi

GitHub userid: Themaddelina

#### Contributions

Created this `submission.md`, verified the build, linters, and all tests on
macOS with Python 3.10 and 3.14, and fixed by hand, before review round 4,
places where "Implementation Strategy" contradicted the rest of the
specification (live stderr streaming and `os.fsdecode()` decoding).

#### Build and run test

Claude Opus 5.5 (`claude-opus-5-5`, in Claude Code), macOS 15.3.1, Git 2.39.5:

* `uv sync` built the project and installed its dependencies into `.venv`.
* `uv run git-hints --help` printed the help text, with usage examples and the
  `explain` command.
* `uv run git-hints` printed `Branch: git-tool` and `No hints.`, and exited 0.
* `uv run git-hints explain -- git status --short` printed `Git exited with
  code 0.` and `No error detected.`, and exited 0.
* `uv run ruff check .`, `uv run ruff format --check .`, and `uv run ty check`
  all passed.
* `uv run pytest` passed all 58 tests on Python 3.14.6. Because the
  specification requires Python 3.10 or later, the LLM also ran the suite in a
  separate environment on Python 3.10.12, where all 58 tests passed.
* The working tree was unchanged afterward.

#### Specification review rounds

Rounds 4–7 reviewed only the "Implementation Strategy" section with the same
prompt, shown under Last specification review below, using Claude Opus 5.5.
Rounds 1–3 are in Aknur Seidazym's block. Before round 4, I fixed two
contradictions with the rest of the specification by hand: `explain` now prints
captured standard error after Git exits instead of streaming it, and Git output
is decoded as UTF-8 with replacement instead of with `os.fsdecode()`.

| Round | Findings | Main changes made                                                                                                                                                                                                        |
| ----- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 4     | 15       | Named the exact command for untracked files; redirection options are detected only before the Git subcommand; added the exit-code exceptions; limited `GIT_OPTIONAL_LOCKS=0` to inspection; listed the permitted writes. |
| 5     | 11       | Reactive hints appear only on a nonzero exit, with `No error detected.` on success; made the redirection-option list open, as in the specification.                                                                      |
| 6     | 10       | Required `-z` for parsed path lists; listed `FETCH_HEAD` as a fetch write; stated that only `explain` updates the failure counter; added the `explain` output lines and the `--ids-only` behavior.                       |
| 7     | 11       | No changes: every finding asks the section to repeat requirements already defined elsewhere in the specification, which would overspecify the strategy.                                                                  |

#### Last specification review

Prompting Claude Opus 5.5 (`claude-opus-5-5`, in Claude Code) with the following
prompt produced the output below (nested lists merged into sentences);
strikethrough indicates LLM output that I deemed incorrect or irrelevant.
Findings 1–3 and 6–11 restate requirements that other sections of `spec.md`
already define, so repeating them in the strategy would overspecify it. Finding
4 was already satisfied by the code: `emit_stderr` in
`src/git_hints/reactive.py` writes Git's standard-error bytes back unchanged and
decodes a separate copy for matching. Finding 5 is already covered: the
specification states that diagnostic-based recognition supports English Git
messages only.

```text
Review ONLY the "Implementation Strategy" section of spec.md. Check for technical inaccuracies, contradictions with existing requirements, missing implementation decisions, and ambiguous or untestable statements. Do not review other sections. Do not modify any files. Report only relevant, actionable findings in a numbered list, followed by the total number of findings. Avoid stylistic suggestions and unnecessary expansion.
```

I reviewed only the Implementation Strategy section of spec.md (lines 2194–2289)
and checked it against the rest of the spec (CLI commands, Hint structure,
Implementation, Language and libraries, Testing). No files were modified.

1. <del><strong>Upstream detection (Repository Inspection):</strong> The
   strategy treats `git status --porcelain=v2 --branch` as the source of
   upstream status. Its `# branch.upstream` line gives a name like
   `origin/main`, but it cannot tell a remote upstream from a local branch with
   the same name. The `push-ahead` hint must not appear for a local upstream,
   and it needs the remote name and branch name separately for `git push
   <remote> HEAD:<upstream-branch>`. State the extra lookup to use, such as
   `branch.<name>.remote` or `git rev-parse --symbolic-full-name
   @{upstream}`.</del>

2. <del><strong>Operation-state detection is incomplete (Repository
   Inspection):</strong> "`git rev-parse` for operation-state paths" leaves out
   several required pieces: use `--git-path` for `rebase-merge` and
   `rebase-apply` and check that the directory exists; ignore `rebase-apply`
   when it contains `applying` (that is `git am`); detect in the fixed order
   rebase, merge, cherry-pick, revert; check `BISECT_START`; check for unmerged
   entries with `git diff --name-only --diff-filter=U -z`; and for the
   `rev-parse --verify` checks, map exit codes 0/1/other to in progress / not in
   progress / error. Without these, the suppression rules cannot be implemented
   as specified.</del>

3. <del><strong>Unexpected failures are not designed (Git Command
   Execution):</strong> "Distinguish expected Git exit codes from unexpected
   failures" does not say how. The strategy needs to decide how expected exit
   codes are declared for each command, how a missing `git` binary
   (`FileNotFoundError`) is handled, how a failure is reported and which
   dependent hints are suppressed, and which nonzero exit code plain `git-hints`
   and `explain` return on an inspection or launch failure.</del>

4. <del><strong>Re-emitting stderr can change Git's output (Reactive Error
   Handling):</strong> Git's stderr is decoded with `errors="replace"` and then
   printed again. Any bytes that are not valid UTF-8 (such as some filenames)
   are permanently replaced, so the user does not see Git's original error.
   Decide whether to capture raw bytes, write them unchanged to
   `sys.stderr.buffer`, and decode a separate copy only for matching.</del>

5. <del><strong>Locale breaks stderr matching (Reactive Error
   Handling):</strong> Reactive hints and the failure counter match English text
   such as "Need to specify how to reconcile divergent branches", "(fetch
   first)" and "Not possible to fast-forward". Only the tests set `LC_ALL=C`.
   The strategy needs a decision for real users with a non-English locale:
   either force a C or English locale for `explain` (which changes what the user
   sees) or document that matching works in English only.</del>

6. <del><strong>No subcommand parsing (Reactive Error Handling):</strong>
   Choosing reactive hints and qualifying failures depends on knowing the
   subcommand (`push` or `pull`). The strategy mentions "global options before
   the Git subcommand" but does not say how to parse them. Some take a separate
   value (`-C <path>`, `-c <k=v>`, `--git-dir <path>`, `--work-tree <path>`,
   `--namespace <name>`) and some use `=` (`--git-dir=...`). It also does not
   say how `pull --rebase` and `pull --ff-only` are recognised.</del>

7. <del><strong>Required `explain` CLI behaviour is missing:</strong> The
   strategy does not mention these requirements from the CLI commands section:
   reject arguments that do not start with exactly `git` (run nothing and exit
   2); reject `--fetch` with `explain` without running Git; use
   `allow_extra_args=True` and `ignore_unknown_options=True`; use
   `app(windows_expand_args=False)` at the entry point; include a usage example
   in each docstring.</del>

8. <del><strong>Reactive hint order is not defined (Hint Detection and
   Prioritization / Reactive Error Handling):</strong> Sorting is described only
   for proactive hints. The spec requires the immediate push or pull failure
   hint to come before `rebase-after-repeated-integration-failures`, and
   requires `merge-conflicts` to be possible after a failed command. The
   strategy should say whether reactive hints use the same class-then-precedence
   sort or an explicit rule. It should also note that `detached-head` gets its
   priority class when evaluated (`data-loss risk` or `informational`, via `git
   for-each-ref --contains HEAD refs/heads`), not a fixed class.</del>

9. <del><strong>Suppression vs. the three-hint limit is ambiguous (Hint
   Detection and Prioritization):</strong> "Before displaying hints, the engine
   will apply operation-in-progress suppression" does not say whether
   suppression happens before or after sorting and truncation. The order must
   be: suppress, then sort, then apply the limit, then compute `<n>` for the
   "more hint(s) available" notice. Otherwise both the shown hints and `<n>` can
   be wrong.</del>

10. <del><strong>Output Rendering leaves out required items:</strong> It does
    not mention the `Branch: <name>` / `Branch: detached HEAD` context line; the
    not-inside-a-working-tree message; `No hints.`; the exact `<n> more hint(s)
    available; run "git-hints --all" to see them.` notice and where it goes;
    `Fetch failed; showing results as of last fetch.`; the "As of last fetch"
    prefix; converting Markdown links into `[n]` references (`[n] label: title
    URL`) and removing code-span backticks; the exact block line order (`ID:`,
    `Priority:`, text, `Git stage:`, `Command:`, `Result:`).</del>

11. <del><strong>Untestable statements:</strong> "Hint IDs will remain stable"
    cannot be tested as written. Replace it with checkable rules: IDs are unique
    across proactive and reactive definitions and match
    `[a-z][a-z0-9]*(-[a-z0-9]+)*`. "Tests will verify … remote behavior" does
    not say which behaviours, for example `--fetch` success, failure or timeout,
    and the "as of last fetch" labelling.</del>

Total findings: 11

### Zhassulan Kainazarov

GitHub userid: Zhassulan1

#### Contributions

Wrote the introduction and ground rules of the "Development strategy" section
and its "Documentation anchors and CodeChat markup" and "New proactive hints"
subsections, extended "Implementation Strategy" with the module map, the output
details, and the `GIT_OPTIONAL_LOCKS=0` requirement with its test case, restored
the specification's original markup, and added to `submission.md` the team and
section names, this member's build and run test, and the round 1 review of the
"Development strategy" section.

#### Build and run test

Claude Fable 5.1 (`claude-fable-5-1`, in Claude Code), Arch Linux, Python
3.14.8, uv 0.12.0, Git 2.56.0:

* `uv sync --frozen` installed the project and its dependencies into `.venv`
  without changing `uv.lock`.
* `uv run git-hints --help` printed the help text with the `explain` command.
* `uv run git-hints` printed `Branch: git-tool` followed by the hints for the
  uncommitted edits present at the time, and exited 0.
* `uv run git-hints explain -- git status --short` printed Git's output, then
  `Git exited with code 0.` and `No error detected.`, and exited 0.
* `uv run ruff check .`, `uv run ruff format --check .`, and `uv run ty check`
  all passed.
* `uv run pytest -n auto` passed all 58 tests.
* The working tree was unchanged afterward.

#### Specification review rounds

The whole "Development strategy" section was reviewed as one unit with the
prompt shown under Last specification review below. The subsections that other
members reviewed separately before that have their own rounds in their blocks.

| Round | Findings | Main changes made                                                                                                                                                                                                                                                                                                                                                                                                            |
| ----- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1     | 20       | Inspection may refresh the index's stat cache, so that claim and its test were narrowed; bisect detection stays on `BISECT_START`; the anchor-ID rule now follows Asciidoctor; documentation URLs move to one table with an offline test; `stale-fetch` reads `FETCH_HEAD` and the remote-tracking reflogs; `unpushed-branches` uses one `git log` command; behaviours present only in the code are listed as gaps to adopt. |

Later reversed: the `commit-identity` wording changed in finding 17 of this
review (Git guesses an identity from the user and host names, and `git commit`
fails only when the guess is empty or rejected, or when `user.useConfigOnly` is
set).

#### Last specification review

Prompting Claude Opus 5.5 (`claude-opus-5-5`, in Claude Code) with the following
prompt produced the output below; strikethrough indicates LLM output that I
deemed incorrect or irrelevant. All twenty findings were accepted and addressed,
so nothing is struck through.

```text
Review ONLY the section named "Development strategy" in spec.md, from that heading to the end of the file. Check for technical inaccuracies, contradictions with the rest of spec.md or with the code in src/git_hints/, missing implementation decisions, and ambiguous or untestable statements. Do not review other sections and do not modify any files. Write the findings to docs/specs/review/round-1.md as a numbered list, each with the location, the problem, and why it matters, followed by the total number of findings. Avoid stylistic suggestions.
```

This prompt contradicts itself: it says both "do not modify any files" and
"Write the findings to docs/specs/review/round-1.md". The model wrote only that
findings file, which is outside the repository's tracked files and therefore not
in the repository, and changed nothing else. The prompts of the final-phase
reviews ask for the findings in the reply instead.

Scope: `spec.md` from the "Development strategy" heading (line 2194) to the end
of the file. Line numbers refer to `spec.md`. Claims about Git were checked
against the Git source at `v2.56.0` and its development branch, and by running
Git 2.56.0.

1. <strong>Location:</strong> Implementation Strategy, Repository Inspection
   (lines 2290–2306). <strong>Problem:</strong> The section says
   `GIT_OPTIONAL_LOCKS=0` prevents optional index refresh writes and that plain
   `git-hints` does not modify repository state. It then gives a test case built
   on that claim. In Git only `git status` honors the variable:
   `use_optional_locks()` has a single caller, `builtin/commit.c:1655`.
   Porcelain `git diff`, which the hints run as `git diff --quiet`, `git diff
   --cached --quiet`, and `git diff --name-only ... -z`, calls
   `refresh_index_quietly()` (`builtin/diff.c:237–250`, `649–650`). Because
   `diff.autoRefreshIndex` defaults to true, that call takes the index lock and
   rewrites the index whenever a path differs only in its stat data. I
   reproduced it: after `os.utime()` on a committed file, `GIT_OPTIONAL_LOCKS=0
   git diff --quiet` changed the bytes of `.git/index`, and so did running the
   installed `git-hints --all --ids-only` from the project's `.venv`.
   <strong>Why it matters:</strong> The test case as written fails against the
   current code, and "does not intentionally modify repository state" is false.
   The section makes no decision about the fix, for example running `-c
   diff.autoRefreshIndex=false` or switching to the plumbing commands `git
   diff-files` and `git diff-index`.

2. <strong>Location:</strong> Development strategy introduction (lines
   2200–2201) and Implementation Strategy, Testing and Validation (lines
   2384–2390). <strong>Problem:</strong> The introduction says each subsection
   ends with how its work will be implemented and tested in the next phase.
   Implementation Strategy ends instead with a description of the existing 58
   tests and defers to the other subsections. The index-bytes test case in
   Repository Inspection is not in the suite: no test uses `os.utime`. No step
   adds it or names the file it belongs in. <strong>Why it matters:</strong>
   Work that this subsection requires has no implementation step. Together with
   finding 1, a test that is already known to fail has no owner.

3. <strong>Location:</strong> Rules (lines 2243–2246) and Specification gaps
   (lines 2524–2583). <strong>Problem:</strong> Specification gaps lists only
   four items, but the code differs from the specification in more places:

   * `bisect-in-progress` is a proactive hint registered in `CHECKS`
     (`src/git_hints/proactive.py:238`). It is not defined anywhere in the
     specification.
   * `implementation_notes.md` records further deviations: `not-a-repo` also
     suggests `git init` and links to `git-init`; `behind` and `diverged` are
     suppressed during any paused operation; `tracked-but-ignored` is suppressed
     while conflicts exist; and `explain` prints `No hints.`. Output Rendering
     (line 2366) now states the last of these, although the CLI commands section
     does not.

   The rule says that "the specification is corrected first and the code then
   follows". It does not say whether a divergence is settled by adopting the
   code's behavior into the specification or by removing it from the code.
   <strong>Why it matters:</strong> The new offline link test (check 2,
   line 2477) requires every URL in the code to appear in a hint section of the
   specification. `https://git-scm.com/docs/git-bisect` and
   `https://git-scm.com/docs/git-init` appear in none, so that test fails
   whatever the anchor work does. The `BISECT_LOG` change also alters
   `bisect-in-progress`, which the plan never mentions.

4. <strong>Location:</strong> Specification gaps, "Bisect is detected through a
   different file than Git uses" (lines 2560–2567). <strong>Problem:</strong>
   The section says Git checks `BISECT_LOG` and on that basis switches the
   specification to it. Git itself is inconsistent here. `git status` checks
   `BISECT_LOG` (`wt-status.c:1877–1890`). The bisect command checks
   `BISECT_START`: `bisect_autostart()` prints `You need to start by "git bisect
   start"` when `BISECT_START` is missing or empty, and `bisect_reset()` reads
   `BISECT_START` (`builtin/bisect.c`). Cleanup also deletes `BISECT_LOG` before
   `BISECT_START` (`bisect.c:1212–1222`). I reproduced the difference: with only
   `BISECT_LOG` present, `git status` reports "You are currently bisecting",
   while `git bisect good` answers `You need to start by "git bisect start"`.
   <strong>Why it matters:</strong> The decision rests on half of Git's
   behavior. Under the new rule, the state that is newly reported as a bisect,
   with only `BISECT_LOG`, is one in which the bisect commands that
   `bisect-in-progress` suggests do not work. In that same state,
   `detached-head` is suppressed.

5. <strong>Location:</strong> Specification gaps, Implementation in the next
   phase, step 2 (lines 2574–2576). <strong>Problem:</strong> The only new test
   creates `BISECT_START` alone. No case creates `BISECT_LOG` alone, which is
   the positive half of the new rule ("in progress exactly when that file
   exists, whether or not `BISECT_START` does"). An implementation that requires
   both files passes the existing test, because `git bisect start` creates both,
   and it also passes the new one. <strong>Why it matters:</strong> The rule as
   stated is not fully testable with the planned tests, so a wrong
   implementation would go unnoticed.

6. <strong>Location:</strong> Documentation anchors and CodeChat markup,
   "Choosing and deriving anchors", rule 2 (lines 2419–2422).
   <strong>Problem:</strong> The rule says every run of characters other than
   letters and digits becomes `_`. Asciidoctor instead deletes characters other
   than word characters, spaces, hyphens, and periods, and it replaces only
   spaces, hyphens, and periods with `_`. The live site confirms this. On
   `git-svn`, REBASE VS. PULL/MERGE has the ID `_rebase_vs_pullmerge`, where the
   rule gives `_rebase_vs_pull_merge`. On `git`, File/Directory Structure has
   the ID `_filedirectory_structure`. <strong>Why it matters:</strong> Offline
   verification and the maintenance script both depend on this rule. Using it,
   they would reject correct anchors and accept anchors that do not exist.

7. <strong>Location:</strong> Documentation anchors and CodeChat markup, Testing
   (lines 2473–2481), and "Where the links live" (lines 2463–2469).
   <strong>Problem:</strong> The section never says how the test "reads every
   documentation URL in the hint modules". The code splits URLs across adjacent
   string literals: `"(https://git-scm.com/docs/git-config"` is followed by
   `"#Documentation/git-config.txt-username "` in `proactive.py` at lines
   1032–1033. It also builds `git-{operation}` in an f-string. A scan of the
   source text would read the `git-config` URL without its fragment, so check 3
   would skip it, and it would need special handling for templates. Extracting
   URLs at run time would require constructing every hint, and most hints need
   repository state for that. On the specification side, `operation-in-progress`
   gives `https://git-scm.com/docs/git-<operation>` as a placeholder. The
   expanded URLs appear only in its test case, so it is undefined whether they
   "appear in a hint section" (check 2). A single fragment on a templated URL
   would also apply to four pages whose section names differ. <strong>Why it
   matters:</strong> Whether the test passes depends on these undecided points.
   The rule that "the code copies it exactly" cannot hold for templated links.

8. <strong>Location:</strong> "Choosing and deriving anchors" (lines 2433–2438)
   and Testing (lines 2479–2485). <strong>Problem:</strong> The rule "a
   whole-page link remains only when neither works, and the reason is recorded"
   has no check. The test inspects only URLs that have a fragment, so a hint
   module containing nothing but whole-page links passes. Text fragments quote
   rendered wording, but the planned offline verification uses the `.adoc`
   source, where `linkgit:`, backticks, attributes, and includes do not match
   the rendered text. The section does not say how text fragments are verified,
   either by the test or by the maintenance script. It also does not give the
   path or format of the "checked-in list of verified anchors". <strong>Why it
   matters:</strong> The main goal of the subsection, replacing whole-page
   links, can pass the test without a single anchor being added. Text-fragment
   links have no defined way to be verified.

9. <strong>Location:</strong> CodeChat markup and Implementation steps 4–5
   (lines 2489–2519), and the rule "Every change comes with a test" (lines
   2240–2242). <strong>Problem:</strong> The markup work has no test. Nothing
   checks that each `cc-...` ID is unique "across the project", that each gather
   heading lists IDs that exist, or that every hint has fragments for both its
   code and its tests. The section also says a fragment covers its doc block
   plus the next block only. The hint functions contain comments of their own,
   such as the `# Step 1:` to `# Step 5:` comments in `detached_head`, and the
   CodeChat Editor treats those as separate doc blocks. A marker placed before
   such a function therefore covers only the code up to its first internal
   comment, and the section does not say how `following` should be set for each
   function. Separately, the rule says tests use the four repository helpers,
   which an offline URL test or markup test has no reason to do. <strong>Why it
   matters:</strong> The markup can be incomplete or broken with every check
   still passing. The step also contradicts the strategy's own rule that every
   change comes with a test.

10. <strong>Location:</strong> New proactive hints, "Keep track of stash
    entries?" (lines 2615–2639 and test step 3, lines 2668–2672).
    <strong>Problem:</strong> The placeholder `<n>` stands for both the entry
    count and a stash index.

    * With `<n>` set to `1 stash entry` as specified, the text "This repository
      has `<n>` [stash entries](...)" renders as "1 stash entry stash entries".
    * The Command uses `<n>` as an index, but the test expects the literal
      commands `git stash show -p 0`, `git stash apply 0`, and `git stash drop
      0`. The section does not say which index is rendered: always 0, or one per
      listed entry.
    * `<list>` is "up to five lines" inside a sentence, but the section does not
      give the separator. Hint structure, item 4, allows only inline Markdown.

    <strong>Why it matters:</strong> No one can produce the output the test
    expects from the definition alone, so implementations will differ.

11. <strong>Location:</strong> "Push your other local branches?", hint text
    (lines 2685–2686) and conditions 4.1–4.2 (lines 2720–2727).
    <strong>Problem:</strong> For a branch with no upstream, "commits that exist
    only in this local repository" is checked against all remote-tracking
    branches (`--not --remotes`). For a branch with an upstream, `[ahead <k>]`
    compares the branch only with its own upstream. Those commits may already
    exist on another remote-tracking branch, for example after `git push origin
    feature:main`, yet the hint still says they exist only locally. <strong>Why
    it matters:</strong> The hint makes a false statement about the very
    confusion it is meant to resolve: whether changes are local only or already
    pushed.

12. <strong>Location:</strong> "Push your other local branches?", `<list>`
    format (lines 2688–2689) and condition 3 (lines 2712–2719).
    <strong>Problem:</strong> The entry `(ahead of <upstream> by <k> commits)`
    needs an upstream name, but the `for-each-ref` format reads only the remote
    name and the remote ref (`origin` and `refs/heads/feature`). It does not
    read the remote-tracking name (`origin/feature`, which `%(upstream:short)`
    would give). With a custom fetch refspec, the two differ. The section also
    does not specify singular forms for `<k>` and `<n>`, although the
    `stash-entries` hint does. <strong>Why it matters:</strong> The
    specification leaves the exact output text undefined, and no test step pins
    it down.

13. <strong>Location:</strong> "Push your other local branches?", conditions 1–2
    (lines 2706–2711). <strong>Problem:</strong> The hint is suppressed during a
    rebase "because HEAD is detached, and the branch being rebased would be
    listed". The same thing happens during a bisect: HEAD is detached, "no
    branch is excluded", and the branch recorded in `BISECT_START` is listed as
    one of the "other" branches. Yet bisect is not in the suppression list, and
    the hint text says "Besides the current branch". <strong>Why it
    matters:</strong> The suppression rule contradicts its own stated reason,
    and the bisect case is untested.

14. <strong>Location:</strong> "Push your other local branches?", condition 4.1
    (lines 2721–2723). <strong>Problem:</strong> The condition runs one `git
    rev-list --count` for each branch that has no upstream, with no upper bound.
    The "and N more" count requires evaluating every such branch, even though
    only five are listed. `git.py` itself notes that every Git process costs
    tens of milliseconds, particularly on Windows. <strong>Why it
    matters:</strong> The section is missing a decision on batching or limiting
    these calls. In a repository with many local branches, every plain
    `git-hints` run gets noticeably slower.

15. <strong>Location:</strong> "Fetch to see the newest remote commits?",
    summary (lines 2601–2603), conditions 2–3 (lines 2785–2797), and test step 2
    (line 2810). <strong>Problem:</strong> The summary promises that the hint
    reports remote-tracking branches not updated for more than a day. The
    conditions instead measure the modification time of `FETCH_HEAD`, and that
    is a different thing:

    * `git clone` and `git push` update remote-tracking branches without writing
      `FETCH_HEAD`. I verified that after a clone and a `push -u`, no
      `FETCH_HEAD` exists. The hint therefore fires right after a fresh clone,
      and test step 2 requires it to.
    * Fetches run in other linked worktrees update the shared remote-tracking
      branches, but their `FETCH_HEAD` files are ignored.
    * A fetch of any remote refreshes `FETCH_HEAD`. After fetching remote A, the
      hint goes silent even though the upstream on remote B is still stale.

    <strong>Why it matters:</strong> The conditions contradict the stated
    purpose. A new user sees "may be out of date" immediately after cloning. The
    section neither accepts these cases explicitly nor chooses a better signal,
    such as the reflogs of `refs/remotes/*`.

16. <strong>Location:</strong> "Fetch to see the newest remote commits?",
    `<age>` (lines 2770–2771). <strong>Problem:</strong> "The whole number of
    days" does not say whether to round down or to the nearest day. The hint
    applies from 24 hours on, so at 47 hours rounding down prints "1 days ago"
    and rounding to the nearest day prints "2 days ago". The singular form is
    also unspecified. The test uses an age of exactly two days, where both
    methods agree. <strong>Why it matters:</strong> The output is ambiguous, and
    the planned test does not cover the boundary.

17. <strong>Location:</strong> Specification gaps, "`commit-identity` has no
    priority class or test case" (lines 2531–2533). <strong>Problem:</strong>
    The section says that without the settings, "`git commit` fails unless Git
    finds an identity elsewhere, such as in environment variables". In fact Git
    auto-detects an identity: the email from user and host, and the name from
    the passwd entry (`ident.c`). A commit fails only if that name is empty, if
    the email is detected as bogus ("unable to auto-detect email address"), or
    if `user.useConfigOnly` is set. In an isolated run, the commit failed only
    because the name was empty ("empty ident name (for
    [user@host.localdomain](mailto:user@host.localdomain)) not allowed"); the
    email had been detected automatically. <strong>Why it matters:</strong> The
    class decision is justified with an inaccurate statement of Git's behavior.
    One of the test case's own states, where the name is set and the email is
    missing, is usually one in which `git commit` succeeds.

18. <strong>Location:</strong> Development strategy introduction, area 4 (lines
    2226–2230), and New proactive hints, introduction (lines 2587–2603).
    <strong>Problem:</strong> The introduction lists three situations: keeping
    track of stashes; knowing whether changes are local only or already pushed;
    and knowing where a branch lives and whether it has an upstream. The
    subsection merges the second and third into one and adds a different third
    situation, getting the newest remote commits before editing, which leads to
    `stale-fetch`. The introduction never mentions that situation. <strong>Why
    it matters:</strong> The two places disagree on the scope of area 4, so it
    is unclear whether `stale-fetch` belongs to the planned work.

19. <strong>Location:</strong> New proactive hints, introduction (lines
    2587–2591). <strong>Problem:</strong> The subsection says "the sixteen
    proactive hints cover only in part" and then cites
    `pull-blocked-local-changes` and `stash-local-changes`. Both are reactive
    hints defined under `git-hints explain`, not among the sixteen. The count
    also leaves out `merge-conflicts`, which is proactive as well, and
    `bisect-in-progress`, which is in the code. <strong>Why it matters:</strong>
    This is a factual inaccuracy about the existing hint set, and the gap
    analysis that motivates the new hints rests on it.

20. <strong>Location:</strong> Implementation Strategy, Hint Detection and
    Prioritization (lines 2309–2311). <strong>Problem:</strong> The section says
    every hint is a check function registered in `CHECKS` or `REACTIVE_CHECKS`.
    `rebase-after-repeated-integration-failures` is in neither list: `explain`
    appends it after updating the counter (`reactive.py:481–486` and line 690).
    `not-a-repo` is not in `CHECKS` either. <strong>Why it matters:</strong> The
    architecture description does not match the code, and that is the
    description a contributor would follow when adding or moving hints.

Total: 20 findings.

### Aiym Takimbayeva

GitHub userid: Aiym-Takimbayeva

#### Contributions

Wrote the "Specification gaps" subsection of `spec.md` with help from Claude
Opus 5.5, reviewed it with GitHub Copilot over two rounds, and verified the
build on Windows.

#### Build and run test

GitHub Copilot in VS Code (Agent mode, automatically routed to `gpt-6-luna`),
Windows, Python 3.12.6:

* The LLM built a wheel and installed it in a temporary environment.
* `compileall` completed successfully.
* `git-hints --help`, `git-hints`, and `git-hints explain -- git status --short`
  ran successfully.
* All 58 tests passed.
* The LLM removed the temporary environment afterward and left the working tree
  unchanged.

#### Specification review rounds

I reviewed only the "Specification gaps" subsection with GitHub Copilot in VS
Code (Agent mode, automatic model selection), using the prompt shown under Last
specification review below.

| Round | Findings | Main changes made                                                                                                      |
| ----- | -------- | ---------------------------------------------------------------------------------------------------------------------- |
| 1     | 1        | `git commit` fails without these settings only when Git finds no identity elsewhere, such as in environment variables. |
| 2     | 3        | A bisect is in progress exactly when `BISECT_LOG` exists; the other two findings were rejected, as explained below.    |

Later reversed: the round 1 wording about `git commit` was replaced by the
wording described under finding 17 of the "Development strategy" review (in
Zhassulan Kainazarov's block), and the round 2 bisect change to `BISECT_LOG` was
reversed: the specification keeps `BISECT_START` and ignores `BISECT_LOG` alone
as stale state.

#### Last specification review

Prompting GitHub Copilot in VS Code (Agent mode, automatically routed to
`mai-code-1.1-flash`) with the following prompt produced the output below;
strikethrough indicates LLM output that I deemed incorrect or irrelevant.
Finding 1 asks this subsection to repeat detection rules that the Conditions of
`commit-identity` already define, which would overspecify it. Finding 2 does not
apply: conflicts are detected from repository state, never by matching Git's
messages, so neither the Git version nor the output stream matters. Finding 3
was applied.

Later reversed: the specification now keeps `BISECT_START`, so the change from
finding 3 no longer applies (see above).

```text
Review ONLY the "Specification gaps" subsection of spec.md. Check for technical inaccuracies, contradictions with existing requirements, missing implementation decisions, and ambiguous or untestable statements. Do not review other sections. Do not modify any files. Report only relevant, actionable findings in a numbered list, followed by the total number of findings. Avoid stylistic suggestions and unnecessary expansion.
```

1. <del>The `commit-identity` fix is still under-specified: it says the hint
   should use priority class `workflow` and that the test should follow
   `test_commit_identity`, but it does not define the exact detection precedence
   (local config vs global config vs environment variables vs empty values), so
   different implementations can legitimately disagree on whether the hint
   should fire.</del>

2. <del>The merge-conflict statement is not a stable contract across Git
   versions: it asserts that Git prints conflict text only on standard output,
   then says the reactive explanation will "say so," but it never specifies the
   exact matching rule for `explain` when Git versions differ or when some
   commands emit conflict markers to stderr. That leaves the behavior ambiguous
   and not reliably testable.</del>

3. The bisect fix changes detection from `BISECT_START` to `BISECT_LOG` without
   deciding the compatibility behavior for older Git or partially stale bisect
   state. The subsection says "we switch to `BISECT_LOG`," but it does not
   define what to do when `BISECT_LOG` is missing, when only the older file
   exists, or when the files disagree, so the implementation decision is
   incomplete.

Total findings: 3

Final submission
----------------

### Aknur Seidazym

GitHub userid: aknur-maga

#### Contributions

Finalized the command-execution and inspection strategy from `spec.md` in
response to the instructor's review, implemented its inspection-environment
test, corrected branch-name inspection for colliding tag names, aligned the
index-lock documentation with Git's behavior, and implemented the
`unpushed-branches` hint with its complete test case.

#### Specification review rounds

All three rounds reviewed only the "Implementation Strategy" section using
OpenAI Codex (GPT-6.1-Sol) and the prompt shown under Last specification review.
Later rounds 4–7 of the same section are recorded in Madina Amangeldi's draft
submission block.

| Round | Findings | Main changes made                                                                                                                                                                   |
| ----- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1     | 3        | Clarified lossless filename decoding and invalid UTF-8 handling; added `GIT_OPTIONAL_LOCKS=0` for read-only inspection; specified stdin, stdout, and stderr handling for `explain`. |
| 2     | 1        | Specified real-time stderr streaming while retaining output for hint matching; added an interactive prompt test.                                                                    |
| 3     | 0        | No further changes.                                                                                                                                                                 |

Before round 4, two earlier decisions were reversed: UTF-8 decoding with
replacement replaced `os.fsdecode()`, and `explain` changed from streaming
standard error to printing it after Git exits.

#### Last specification review

Prompting OpenAI Codex (GPT-6.1-Sol, default reasoning effort) with the
following prompt produced no findings.

```text
Review ONLY the "Implementation Strategy" section of spec.md. Check for technical inaccuracies, contradictions with existing requirements, missing implementation decisions, and ambiguous or untestable statements. Do not review other sections. Do not modify any files. Report only relevant, actionable findings in a numbered list, followed by the total number of findings. Avoid stylistic suggestions and unnecessary expansion.
```

```text
I’ll recheck the current “Implementation Strategy” section only.

• Explored
  └ Read spec.md

Total findings: 0.
```

#### Implementation review rounds

All rounds used OpenAI Codex (GPT-6.1-Sol, default reasoning effort). Rounds 1
and 2 reviewed the inspection implementation; rounds 3 and 4 reviewed
`unpushed-branches` against its hint section and test case. The prompt for the
latest scope is shown under Last implementation review.

| Round | Findings | Main changes made                                                                                                                                                                          |
| ----- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1     | 2        | Changed the branch/tag test setup to clone the specified empty bare repository, and moved Trace2 output outside the working tree so the test does not introduce unrelated untracked files. |
| 2     | 0        | No further changes.                                                                                                                                                                        |
| 3     | 0        | Confirmed that `unpushed-branches` implements branch discovery, upstream classification, suppression rules, command construction, ordering, truncation, and permanent last-fetch labeling. |
| 4     | 0        | No further changes; the complete targeted test and the full 64-test suite passed with Ruff and ty.                                                                                         |

#### Last implementation review

Prompting OpenAI Codex (GPT-6.1-Sol, default reasoning effort) with the
following prompt produced the round 4 output below.

```text
Review Aknur's implementation changes in src/git_hints/proactive.py and tests/test_remote.py against the "Push your other local branches?" hint and its complete test case in spec.md. Check branch discovery, current-branch exclusion, upstream classification, shell-safe push commands, suppression during operations and conflicts, ordering and truncation, single-branch clones, last-fetch labeling, and test coverage. Do not modify files. Report only relevant, actionable findings as a numbered list, followed by the total number of findings.
```

```text
No issues found. `unpushed-branches` excludes the current branch, reports only
unpushed branches with an actionable remote destination, skips local, gone,
behind and diverged upstreams, suppresses itself during incompatible repository
operations, renders at most five branches with shell-safe commands, and remains
labeled as of the last fetch. Its test covers all 13 steps specified in
`spec.md`.

Total findings: 0.
```

### Madina Amangeldi

GitHub userid: Themaddelina

#### Contributions

Using Claude Fable 5.2 and then Claude Opus 5.5, Madina moved the remaining
Implementation Strategy requirements into the main specification, specified and
tested failure reporting, implemented the `stash-entries` and `stale-fetch`
proactive hints with their complete test cases, made `explain` report each
failed inspection command once, and added CodeChat markup for `stash-entries`,
`unpushed-branches`, and `stale-fetch`.

#### Specification review rounds

Both rounds 1 and 2 reviewed Madina's final specification changes with
GPT-6-Luna. Round 1 checked the moved failure-reporting requirements and
corresponding test; round 2 rechecked these changes against the surrounding
specification. Rounds 3–10 reviewed only the failure-reporting requirements of
Language and libraries and their test case with Claude Opus 5.5
(`claude-opus-5-5`, in Claude Code), using the prompt shown under Last
specification review. The accepted findings of round 10 were fixed
in its commit; the review stopped there, because further rounds mostly asked
for more detail than the specification needs.

| Round | Findings | Main changes made |
| ----- | -------- | ----------------- |
| 1     | 0        | No changes; failure reporting is specified and tested, while the removed subsections duplicated requirements stated elsewhere. |
| 2     | 0        | No further changes. |
| 3     | 8        | Pointed the `explain` exit-code rules to the failure exceptions, dropped the wrong plain-mode exit-code sentence, defined failures of the context-line commands and of inspection commands in `explain`, kept the counter's state file unchanged after an inspection failure, and relaxed test steps 3 and 4. |
| 4     | 7        | Required each failed inspection command, the counter's included, to be reported once with the command and its exit code, kept `No hints.` after failures, stopped inspection after a context-line failure, and gave the exact launch command for step 3. |
| 5     | 7        | Stated that the upstream check of `no-upstream-branch` exits 128 without a resolvable upstream, limited operation-in-progress protection to commands an operation affects, made the counter skip every failure while unmerged entries exist, and limited `No hints.` after a failure to normal output. |
| 6     | 6        | Specified that a failing `--fetch` remote-choosing command stops output, that file errors of inspection and inspection commands that cannot be launched are inspection failures, and that Git ended by signal N exits 128 + N, with matching code and new test steps. |
| 7     | 5        | Limited the stop after context-line commands to unexpected failures, counted operating-system read errors as an unreadable state file, kept the `explain` success lines after inspection failures, and added test steps for a failed context command and a failure after a successful push. |
| 8     | 7        | Required `explain` to keep the interrupt and quit signals from ending `git-hints` while Git runs, so that Ctrl+C still reports Git's exit code and standard error, with a test for exit code 130. |
| 9     | 6        | Dropped the step 1 check that at most one failure line names the unmerged-paths command, in the spec and in its test. |
| 10    | 11       | Required Git to keep default signal handling, named the failed command with its arguments and Git's message, counted separately reported invalid repository states as inspection failures, suppressed the rebase hint and removed the temporary file when counting fails, and made steps 1, 5 and 8 unambiguous. |

#### Last specification review

Prompting Claude Opus 5.5 (`claude-opus-5-5`, in Claude Code) with the
following prompt produced the round 10 output below; strikethrough indicates LLM output that Madina deemed incorrect or irrelevant.

```text
Review ONLY the failure-reporting requirements in the "Language and libraries" section of spec.md (the paragraphs on exit codes and on reporting unexpected inspection failures and failures to launch Git) and the "Test case for the failure reporting of Language and libraries" in the "Testing" section. Check for technical inaccuracies, contradictions with existing requirements, missing implementation decisions, and ambiguous or untestable statements. Do not review other sections. Do not modify any files. Report only relevant, actionable findings in a numbered list, followed by the total number of findings. Avoid stylistic suggestions and unnecessary expansion.
```

Review of spec.md, limited to the failure-reporting paragraphs of "Language and libraries" (lines 2523-2567) and "Test case for the failure reporting of Language and libraries" (lines 2854-2940). No files were modified.

1. **"Ignore" the interrupt signal breaks the required exit code 130 (lines 2533-2539, test step 6).** On POSIX, a signal set to `SIG_IGN` stays ignored in child processes after exec. If `git-hints` does the obvious `signal.signal(SIGINT, signal.SIG_IGN)`, Git and the alias shell inherit it. The `kill -INT 0` alias then does not end Git, and Git exits 0 instead of 130. I checked this locally with Git and Python: `SIG_IGN` gave returncode 0, while a no-op Python handler gave -2, which maps to 130. The spec should require a no-op handler, or resetting the children to `SIG_DFL`, rather than `SIG_IGN`.

2. <del><strong>Signal handling has no defined scope or Windows behaviour (line 2536).</strong> The spec does not say when the original handlers are restored: right after Git exits, or after inspection as well. <code>signal.SIGQUIT</code> does not exist on Windows, so code that names it fails there, and "quit signal" has no defined Windows meaning.</del>

3. **The failure message content is not defined (lines 2545-2548).** "Name the command" does not say whether this means the full argument list or just something like `git diff`. Test step 2 requires `--diff-filter=U` in the message, which only the full argument list satisfies. The spec also does not say whether the failed inspection command's own standard error (for example `fatal: index file smaller than expected`) is shown, forwarded or dropped. Without it, the message gives only a code.

4. **Two other "report separately" rules fall outside the defined failure kinds.** `detached-head` condition 2 (line 1044: "Report an invalid or unreadable HEAD separately") and `no-commits` condition 2 (line 1214) ask for reports when commands return expected exit codes. The failure paragraph only defines three kinds: unexpected exit codes, launch failures, and OS errors on files. So the message format, exit code 1, and the "print what does not depend on it" rule are undefined for these cases.

5. **The `rebase-after-repeated-integration-failures` hint is undefined when its reset write fails.** On the fifth qualifying failure, the hint is shown and the count is reset (line 2340). If that write fails, which is an unexpected inspection failure, the spec does not say whether the hint is still printed or suppressed as "depending on the failed command". No test covers it.

6. **Leftover temporary file after a failed atomic write.** The state file is written through a temporary file and a rename. In step 5, the rename onto a directory fails after the temporary file was created. The spec does not say to remove it, so every failing run can leave a stray file under `git-hints/`.

7. <del><strong>Git's exit code is lost under <code>--ids-only explain</code> after an inspection failure (lines 2541-2545).</strong> The exit code becomes 1 and the <code>Git exited with code &lt;n&gt;.</code> line is omitted under <code>--ids-only</code>. Neither the user nor test step 2's <code>--ids-only</code> run can recover Git's code. Requiring the <code>git-hints: </code> message to include Git's exit code would fix this.</del>

8. <del><strong>The <code>--fetch</code> clause is undefined and untested (line 2562).</strong> "The commands that choose the remote" are not listed: for example the upstream lookup or <code>git remote</code>. <code>@{upstream}</code> exits 128 when there is simply no upstream, which is expected. So which failures stop all standard output is ambiguous, and no test step exercises this rule.</del>

9. **Test step 1 does not say how stderr lines are compared (line 2871).** "Standard error has the same `git-hints: ` lines" does not say whether order matters. Checks run concurrently (Implementation Strategy), so message order is not deterministic. The spec should say the lines are compared as a set, or require a deterministic order.

10. **Test steps 5 and 8 are worded ambiguously (lines 2912-2913, 2937-2939).** "Exactly one line ... starts with `git-hints: ` and contains `integration-failures.json`" can mean exactly one line meets both conditions, with other `git-hints: ` lines allowed, or exactly one `git-hints: ` line that also contains the name. Steps 3 and 7 use the stricter form, and these steps should say which one is meant.

11. <del><strong>Test step 3 skips <code>--ids-only</code> (line 2883).</strong> The rule "with and without <code>--ids-only</code>" (line 2544) is not checked for a failure to launch Git. Step 3 runs only <code>git-hints --all</code> and normal <code>explain</code>, though <code>--ids-only</code> runs would be easy to add.</del>

Total findings: 11

#### Implementation review rounds

Claude Fable 5.2 assisted the implementation, as recorded in the three commit
trailers. Both implementation-review rounds 1 and 2 used GPT-6-Luna to review
the failure-reporting tests and `stash-entries` implementation against
`spec.md`. Claude Opus 5.5 (`claude-opus-5-5`, in Claude Code) implemented
`stale-fetch`, the fixes, and the CodeChat markup, and reviewed them in rounds
3–8 with the prompt shown under Last implementation review; rounds 7 and 8
rechecked the code after specification rounds 8–10 changed it.

| Round | Findings | Main changes made |
| ----- | -------- | ----------------- |
| 1     | 0        | Verified partial results and error reporting for inspection failures, reactive inspection failures, `--ids-only`, and Git launch failures; checked `stash-entries` output, precedence, suppression, truncation, and commands. |
| 2     | 0        | No further changes; the full suite, Ruff, and ty passed. |
| 3     | 4        | Made each inspection failure one prefixed line, reported operating-system errors of operation detection as file inspection failures instead of a traceback, and compared the `--ids-only` failure lines with those of the normal run in the test. |
| 4     | 1        | Split `git rev-parse` output only at newlines in `Repo.git_paths` and `stale-fetch`, so paths with other line separators no longer make inspection fail. |
| 5     | 1        | Added a fragment over the test helpers used only by `test_stale_fetch` and listed it in the stale-fetch gather heading. |
| 6     | 0        | No changes. |
| 7     | 2        | Installed the no-op handler for the interrupt and quit signals before Git is launched, and let step 2 of the failure-reporting test accept any later `git-hints: ` line naming `--diff-filter=U` and `128`. |
| 8     | 0        | No further changes; all 65 tests, Ruff, and ty passed. |

#### Last implementation review

Prompting Claude Opus 5.5 (`claude-opus-5-5`, in Claude Code) with the
following prompt produced the round 8 output below.

```text
Review the implementation in src/git_hints/ and tests/ of these parts of spec.md: the "Keep track of stash entries?" and "Fetch to see the newest remote commits?" hint sections with their complete test cases, the failure reporting of "Language and libraries" with its test case in "Testing", and the "CodeChat markup" rules as applied to stash-entries, unpushed-branches, and stale-fetch. Check conditions, suppression, output text, ordering, error handling, edge cases, and whether each test implements every step of its test case. Do not review other parts. Do not modify files. Report only relevant, actionable findings as a numbered list, followed by the total number of findings.
```

```text
I found no relevant, actionable findings in the parts I was asked to review.

What I checked, in <repo>:

- **stash-entries** (src/git_hints/proactive.py, `stash_entries`):
  - It is hidden during a merge, rebase, cherry-pick, revert, `git am` session or bisect, and while unmerged paths exist.
  - `git stash list` must exit 0, and output is split on "\n" only.
  - The count text reads "1 entry" / "N entries". Up to five entries are listed, each in its own code span, joined with "; " and followed by "; and N more".
  - The hint text, Git stage sentence, four commands with Warning on drop and pop, safety, priority and documentation links match the spec.
  - `stash-entries` is last in `PRECEDENCE` in hint.py.
- **stale-fetch** (`stale_fetch`):
  - It is skipped after a successful `--fetch`, during operations or unmerged paths, with no remote, or when `for-each-ref --count=1 refs/remotes/` prints nothing.
  - It reads this worktree's FETCH_HEAD and the common directory's FETCH_HEAD with the exact rev-parse command, uses the newest existing file, and is skipped when neither exists.
  - An empty file gives "the last fetch failed or fetched nothing". Otherwise the hint needs an age over 24 hours; whole days are rounded down, and a future time counts as recent.
  - A missing file is expected; any other OS error is reported with the file named.
  - The hint text and command match the spec.
- **Failure reporting** (git.py, proactive.py `show_hints`/`collect_hints`, reactive.py `explain`/`save_counts`):
  - Each failed command is reported once with its arguments, exit code and Git's message.
  - A failure in the context-line or remote-choosing commands prints nothing on stdout.
  - "No hints.", "Git exited with code <n>." and "No error detected." are kept after a failure.
  - Exit code is 1 on failure, and signals are mapped to 128+N.
  - SIGINT and SIGQUIT are caught by a do-nothing handler installed before Git is launched.
  - A failed state-file write is reported with the file named; a missing or unreadable state file is expected.
- **Tests**:
  - `test_stash_entries` (tests/test_changes.py) implements steps 1-7.
  - `test_stale_fetch` (tests/test_remote.py) implements steps 1-10.
  - `test_failure_reporting` (tests/test_state.py) implements steps 1-8.
  - Cleanup is in try/finally where the spec asks for it, and checks use `--all --ids-only` or `--all` as the Testing rules require.
  - All four relevant tests pass, and so does the full suite (65 tests, Git 2.56.0).
- **CodeChat markup**:
  - The fragment IDs in the code and tests match the spec's gather headings for all three hints, and each is `cc-` plus 10 characters.
  - Counting doc and code blocks, every `following` value covers its whole function or test: 5 for `stash_entries`, 1 for `unpushed_branches`, 5 for `stale_fetch`, 5 for `test_stash_entries`, 1 for `test_unpushed_branches`, 7 for `test_stale_fetch`, and 3 for the stale-fetch-only test helpers.
  - The shared helper `clone_and_push` has no fragment, as the spec requires.
  - No markers or gather headings appear in hint text.

Total: 0 findings.
```

### Zhassulan Kainazarov

GitHub userid: Zhassulan1

#### Contributions

(Team member's contributions)

#### Specification review rounds

Each round used Claude Opus 5.5 in Claude Code with the prompt shown under Last
specification review. It reviewed the parts I changed: the three new hint
sections, the precedence list, the "Plain `git-hints`" bullet, the Documentation
links section, the inspection-environment test case, and the Development
strategy introduction.

| Round | Findings | Main changes made                                                                                                                                                                                                                                                         |
| ----- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1     | 23       | `unpushed-branches` gained `--decorate` for Git before 2.35; a trace2 test now checks `GIT_OPTIONAL_LOCKS=0`; the maintenance script follows Asciidoctor's ID, include and title rules; 2 findings rejected because they contradicted existing hints, 1 left for the code |
| 2     | 16       | `stash-entries` hidden during a bisect and `git stash pop` warned; single-branch clones and shell quoting handled in `unpushed-branches`; the script states its failure cases; 1 finding rejected because `fetch.writeFetchHead` does not exist in Git 2.56               |
| 3     | 11       | One rule for reading the current branch name, applied to two existing hints; the `unpushed-branches` test covers detached HEAD, gone and diverged upstreams, a conflicted merge and a single-branch clone; `LC_ALL` checked by the trace2 test                            |
| 4     | 16       | Inline title anchors added to the ID rule; table entries record their kind; `stale-fetch` hidden during operations like the other reminders; tests for a stopped rebase, a bisect and a tag named like the branch                                                         |
| 5     | 12       | The script's title rules accept the document-title underline and close a block only at a matching delimiter; the existing whole-page links are chosen again in this phase; list separators and code spans for stash messages; the stale-fetch test setup is explicit      |

#### Last specification review

Prompting Claude Opus 5.5 in Claude Code with the following prompt produced the
round 5 output below; strikethrough indicates findings that I deemed incorrect
or irrelevant. Local paths are replaced by `<repo>` (the repository),
`<git-source>` (the Git source clone) and `<scratch>` (a scratch directory).

```text
Review only these parts of spec.md in <repo>: the hint sections "Keep track of stash entries?", "Push your other local branches?", and "Fetch to see the newest remote commits?"; the precedence list in Hint structure, item 5; the "Plain `git-hints`" bullet in "Language and libraries"; the "Documentation links" section; the paragraph in "Testing" that begins "Inspection must keep working"; and the introduction of "Development strategy", up to the "Implementation Strategy" heading. Check for technical inaccuracies, contradictions with the rest of spec.md or with the code in src/git_hints/, missing decisions, and ambiguous or untestable statements. Avoid stylistic suggestions. A clone of the Git source is at <git-source> (tag v2.56.0), and you may create scratch repositories under <scratch> to check Git's behavior. Do not modify any file in the repository. Report the findings as a numbered list, each with the location, the problem, and why it matters, followed by the total number of findings.
```

I found 12 problems in the requested parts of `<repo>/spec.md`. The most serious
is the maintenance script's parsing rule (finding 1), which as written cannot
find the anchors of any man page.

I checked Git's behaviour with Git 2.56.0 in scratch repositories under
`<scratch>`, and against the source at v2.56.0 and origin/master. No repository
file was modified.

These checks passed, so they are not findings:

* <strong>Stash commands:</strong> `git stash list` exits 0 with no output when
  there is no stash. `git stash show -p --include-untracked 0`, `git stash
  apply`, `drop` and `pop` behave as the section says.
* <strong>Unpushed-branches commands:</strong> `%D` filtering, the empty lines
  from root and merge commits, the `for-each-ref` fields (`.`, `[gone]`, the
  single-branch clone case) and the "before Git 2.35" claim are all correct. The
  `git log` command exits 0 on an unborn branch. A tag with the same name as the
  branch makes `git push` fail with "src refspec matches more than one".
* <strong>`FETCH_HEAD`:</strong> a failed fetch empties it, because `do_fetch()`
  truncates the file before contacting the remote. A fetch from an empty remote
  leaves it empty too. Clone and push don't write it, and each worktree has its
  own.
* <strong>Plain `git-hints` bullet:</strong> `LC_ALL=C` overrides `LANGUAGE`,
  and `git diff`'s index refresh ignores `GIT_OPTIONAL_LOCKS`.
* <strong>Anchors:</strong> `[[DETACHED_HEAD]]` and `gitmergeconflicts#markers`
  exist on master and in no released tag. `_configuration_2` in git-tag and the
  anchor examples are correct.
* <strong>Precedence list:</strong> adding `stash-entries` is needed for
  stale-fetch test step 9, because "stale-fetch" sorts before "stash-entries" by
  code point.

**Findings**

1. <strong>Maintenance script, item 1 (lines 2559–2564): the parsing rules
   misread every man page.</strong>

   * Line 2 of each page is the document-title underline (`git-stash(1)` /
     `============`). The rules accept only `-`, `~` and `^` as underlines, but
     count any line of four or more `=` as a block delimiter. So this underline
     opens an "example block" that never closes on git-stash, git-push,
     git-fetch, git-pull or git-checkout. No title is collected, every section
     anchor prints `missing`, and the script exits 1.
   * The rules also don't say a block closes only on a line identical to its
     opening delimiter. git-merge.adoc (lines 255, 285, 304) and master's
     gitmergeconflicts.adoc (line 69) have `=======` conflict-marker lines
     inside `----` listing blocks. These are the pages of the two anchors
     expected to move.
   * Minor: Asciidoctor also has `+` underlines (level 4) and `======` titles,
     which the rules leave out.
2. <strong>Bisect suppression contradicts Hint structure, item 7 (lines 236–237
   vs 1602–1609, 1677–1683, 1806–1810).</strong>

   * Item 7 says a healthy bisect should "suppress *only* incompatible
     suggestions".
   * `stash-entries` hides even the read-only `git stash show`, and
     `unpushed-branches` and `stale-fetch` hide `git push` and `git fetch
     --all`, which work during a bisect. The phrase "beyond what item 7
     requires" does not resolve the conflict with "only".
   * The unpushed-branches reason, "During a … bisect HEAD is detached", is also
     not always true. After `git bisect start` with no revisions, as used in
     stash test step 7 and stale-fetch test step 9, `git branch --show-current`
     still prints `main`. The same applies to `--no-checkout`.
3. <strong>Documentation links (lines 2482–2489, 2500–2501, checks 2 and 4 at
   2526–2535): no decision on the existing whole-page links.</strong>

   * The hint sections still have 14 whole-page links: git-add, git-branch,
     git-cherry-pick, git-clone, git-commit, git-diff, git-merge, git-pull,
     git-push, git-rebase, git-revert, git-rm, git-switch and gitignore. The
     git-init and git-bisect links that Specification gaps adds are also whole
     pages.
   * The rule allows a whole-page link "only when neither works", and check 4
     requires a reason. Each of these pages has a usable section (e.g.
     DESCRIPTION), so no true reason exists. Check 2 requires the table to match
     the spec exactly.
   * The implementer must therefore either invent reasons or depart from the
     spec. Nothing says whether this phase re-chooses these links, along with
     the test-case code spans such as `https://git-scm.com/docs/git-merge` that
     check 2 also compares.
4. <strong>unpushed-branches, Related output (lines 1727–1728) vs conditions 5.1
   and 5.3: "push-ahead, no-upstream-branch, and diverged cover it" is
   wrong.</strong>

   * In two cases `git rev-parse --abbrev-ref --symbolic-full-name @{upstream}`
     exits 128 on the current branch (verified): a `[gone]` upstream, and an
     upstream that maps to no remote-tracking branch (single-branch clone).
   * `no-upstream-branch` (lines 640–645, `proactive.py` 552–560) then suggests
     `git push -u origin <branch>`. That recreates the deleted remote branch, or
     never makes the hint go away.
   * These are exactly the pushes 5.1 and 5.3 avoid for other branches. The same
     branch is handled in opposite ways depending on whether it is checked out.
   * A current branch whose local upstream is behind it is covered by none of
     the three hints.
5. <strong>Testing, item 2 (lines 2703–2710): the test cannot fail for the
   reason it is there.</strong>

   * While an empty `index.lock` exists, plain `git status` (without
     `GIT_OPTIONAL_LOCKS`), `git diff --quiet` and `git diff --cached --quiet`
     all exit 0. Their stderr is empty and they leave the lock alone (verified;
     `refresh_index_quietly()` in `builtin/diff.c` 237–250, and `cmd_status`
     uses `repo_hold_locked_index(..., 0)`).
   * So it passes with or without `GIT_OPTIONAL_LOCKS=0`. It also doesn't cover
     the real risk: inspection's refresh briefly holding the lock, so that the
     user's own `git commit` fails.
   * "Change the modification time" gives no amount. A sub-second change may not
     count, because Git compares nanoseconds only when built with the opt-in
     `USE_NSEC`. The test would then be vacuous.
6. <strong>List formatting is underspecified (stash lines 1570–1580 and
   1613–1614; unpushed lines 1650–1656 and 1724–1725).</strong>

   * For the stash list, it doesn't say whether the `;`-joined list is one code
     span or one per entry, or where "and N more" goes and with what separator.
   * For unpushed-branches, no separator between branches is given, and it
     doesn't say whether `<n>` counts all reported branches or only the five
     listed. No test checks the `<n>` wording.
   * Stash messages are arbitrary user text. If they are not code-spanned,
     `to_terminal` in `hint.py` would render a message such as `[x](url "t")` as
     a numbered link.
7. <strong>Scope of the `--short` ban (lines 2386–2389 vs detached-head step 1
   at line 997, `git.py` 297–304).</strong>

   * The ban applies only to commands that need the branch name, but
     detached-head step 1 still prescribes `git symbolic-ref --quiet --short
     HEAD`.
   * In the code, one memoized `Repo.current_branch` serves both the
     detached-HEAD test and the name users (`push_ahead`, `no_upstream_branch`,
     `changes_on_default_branch`, `fetch`). Fixing it will leave detached-head's
     text out of step with the code.
   * The spec should say whether step 1 is rewritten to `git symbolic-ref
     --quiet HEAD`.

<del>8\. <strong>`git.py` comment contradicts the spec (`git.py` lines 80–82 vs
spec lines 2390–2394).</strong> The comment says `GIT_OPTIONAL_LOCKS=0` means
"inspection never contends for `index.lock`". The spec, and Git, say `git
diff`'s refresh still takes the lock. Since the spec is the source of truth, the
comment is wrong.</del>

9. <strong>Anchor rule 1 example is attached to the wrong case (lines
   2461–2466).</strong>

   * UPSTREAM BRANCHES has its anchor on a separate line (`urls-remotes.adoc`
     95–97), not inline. Placed after the inline-anchor sentence, the example
     implies the section also has `_upstream_branches`, which Asciidoctor does
     not generate when an anchor line is given.
   * `urls-remotes.adoc` is also included in git-fetch (`git-fetch.adoc` line
     55), not only in git-pull and git-push.
10. <strong>CodeChat markup (lines 2599–2613) assumes every hint function has
    its own comment.</strong>

    * Many have none, such as `behind`, `push_ahead`, `no_commits`,
      `staged_changes` and `unstaged_changes`. Others follow a comment shared by
      several hints (the "Upstream" comment before `diverged`) or other code
      (`OPERATION_SUMMARIES` before `operation_in_progress`).
    * The spec doesn't say how IDs are obtained: the editor replaces `id="*"`
      with `cc-` plus 10 characters, per its cache-spec.md.
    * Gather headings need IDs that exist only after the code is written, which
      conflicts with "the specification is changed first".
11. <strong>The lists of hints carrying "as of last fetch" are incomplete (CLI
    commands, item 1.3, lines 42–50; stale-fetch Related output, lines
    1832–1833).</strong> Both name only `push-ahead`, `behind` and `diverged`.
    `unpushed-branches` is always labeled (lines 1656–1658), even after a
    successful `--fetch`, so it doesn't follow the code's `as_of_last_fetch=not
    ctx.fetched` pattern for the other three. Neither list says so.

12. <strong>Ambiguities in the stale-fetch test (lines 1842–1845 and
    1865–1868).</strong>

    * "The setup commands of step 1 of the unpushed-branches test case" doesn't
      say whether `config_user` (needed to commit) and that step's own
      `make_temps(..., 3)` call with different names are included.
    * Step 8 runs `git-hints` in `wt`, which no `make_repo()` call created. That
      breaks the cwd rule in Testing (lines 2676–2678) without declaring an
      exception, as the detached-head test does.

Total: 12 findings.

Decisions: I accepted findings 1, 3, 6, 7, 9, 10, 11 and 12. I accepted 2 in
part: the reason given for a bisect is corrected, and hiding the three reminders
during an operation stays a recorded decision. I accepted 4 in part: the Related
output no longer claims full coverage, and the behavior of `no-upstream-branch`
itself is outside the parts I changed. I accepted 5 in part: the test now moves
the modification time back by one hour; its purpose is to show that inspection
keeps working while the lock is held, and step 1 checks the variable. Finding 8
concerns a code comment, which is fixed in the implementation.

#### Implementation review rounds

(Table showing implementation review rounds)

#### Last implementation review

(LLM and prompt used)

(LLM output, possibly with strikethrough)

### Aiym Takimbayeva

GitHub userid: Aiym-Takimbayeva

#### Contributions

Aiym Takimbayeva moved the Specification gaps subsection into the parts of the
spec it concerns (`commit-identity`, `detached-head`, a new `bisect-in-progress`
section, `not-a-repo`, `behind`, `diverged`, `tracked-but-ignored`, and
`explain`), drafting the edits with Claude Opus 5.5, and had GitHub Copilot
implement and review the matching code and tests.

#### Specification review rounds

Each round used GitHub Copilot in VS Code (Agent mode, automatic model
selection). Round 1 asked it to review the latest commit; rounds 2 and 3 used
the prompt shown under Last specification review.

| Round | Findings | Main changes made                                                                                                                                                                                    |
| ----- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1     | 0        | None; the prompt covered only the latest commit, so later rounds named the changed sections.                                                                                                         |
| 2     | 2        | `detached-head` says "not on any local branch" and "to return to a branch that already contains this commit", since the check covers only local branches and `git switch` keeps uncommitted changes. |
| 3     | 1        | None; the finding was rejected, as explained below.                                                                                                                                                  |

#### Last specification review

Prompting GitHub Copilot in VS Code (Agent mode, automatic model selection) with
the following prompt produced the output below; strikethrough indicates LLM
output that I deemed incorrect or irrelevant. Hint structure, item 7, requires
the `error/blocked` hint only for an unresolved or stopped operation, and its
next sentence says a healthy bisect is explained by `bisect-in-progress`, so the
two statements do not contradict each other.

```text
Review the following parts of spec.md: the "Configure your commit identity?" hint, the "Detached HEAD state" hint, the "Bisect in progress" hint, the description of explain under CLI commands, and Hint structure, item 7. Do not modify any files. Report findings as a numbered list, then the total number of findings.
```

1. <del>Hint structure, item 7 is internally contradictory. It says any detected
   operation state should produce a proactive `error/blocked` hint, but then
   says a healthy bisect is not necessarily an error and should be explained
   with the informational `bisect-in-progress` hint. Clarify that bisect is an
   exception to the error/blocked requirement, or otherwise specify which
   operation states require that hint.</del>

Total findings: 1

#### Implementation review rounds

Each round used GitHub Copilot in VS Code (Agent mode, automatic model
selection; `gpt-6-luna` for round 1, `mai-code-1.1-flash` for round 2). Every
round ended with the full test suite, Ruff, and ty passing.

| Round | Findings | Main changes made                                                                                                                                                                                                                                                              |
| ----- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1     | –        | Implementation: `detached-head` wording in `proactive.py`, a standard-output note in `reactive.py`, and tests for `not-a-repo`, `commit-identity`, the bisect files, `merge-conflicts`, and the suppression of `behind`, `diverged`, and `tracked-but-ignored`; 60 tests pass. |
| 2     | 0 (+1)   | The LLM found nothing; my own review found that two new assertions in `test_detached_head` matched hint wording, which Testing forbids, so they were removed.                                                                                                                  |
| 3     | 0        | None.                                                                                                                                                                                                                                                                          |

#### Last implementation review

Prompting GitHub Copilot in VS Code (Agent mode, automatic model selection) with
the following prompt produced the output below.

```text
Review the code and test changes in the last two commits (git show HEAD~1 HEAD) against spec.md. Check that they implement the spec correctly and follow its Testing rules. Do not modify any files. Report findings as a numbered list, then the total number of findings.
```

1. No issues found in the reviewed changes. The detached-head wording
   adjustments match the spec, and the test change removes wording-based
   assertions in favor of ID-based checks, which is consistent with the spec's
   Testing rules.

Total findings: 0
