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

| Round | Findings | Main changes made |
| ----- | -------- | ----------------- |
| 1     | 2        | Changed the branch/tag test setup to clone the specified empty bare repository, and moved Trace2 output outside the working tree so the test does not introduce unrelated untracked files. |
| 2     | 0        | No further changes. |
| 3     | 0        | Confirmed that `unpushed-branches` implements branch discovery, upstream classification, suppression rules, command construction, ordering, truncation, and permanent last-fetch labeling. |
| 4     | 0        | No further changes; the complete targeted test and the full 64-test suite passed with Ruff and ty. |

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

(Team member's contributions)

#### Specification review rounds

(Table showing spec review rounds)

#### Last specification review

(LLM and prompt used)

(LLM output, possibly with strikethrough)

#### Implementation review rounds

(Table showing implementation review rounds)

#### Last implementation review

(LLM and prompt used)

(LLM output, possibly with strikethrough)

### Zhassulan Kainazarov

GitHub userid: Zhassulan1

#### Contributions

Zhassulan Kainazarov specified the `stash-entries`, `unpushed-branches`, and
`stale-fetch` hints, the Documentation links section, and the inspection rules,
revised them after the instructor's review, and implemented the documentation
table with its test, the link-check script, and the CodeChat markup, together
with fixes to push commands and ref-name inspection found on the way.

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
| 6     | 11       | Ref names that inspection compares or puts into commands are read without `--short`; the anchor rules cover HTML entities and trailing title anchors; all four moving anchors are listed; an empty root commit is a known limitation of `unpushed-branches`; 4 findings rejected because the specification already states the decision or the test checks what it requires |
| 7     | 10       | A branch with no upstream is skipped when the `origin` branch of the same name has diverged from it; the stale-fetch test case checks that a failed fetch empties `FETCH_HEAD`; the documentation-table test also checks that each entry's kind fits its URL and that no URL repeats; 4 findings rejected because they contradict decisions the specification records |

#### Last specification review

Prompting Claude Opus 5.5 in Claude Code with the following prompt produced the
round 7 output below; strikethrough indicates findings that I deemed incorrect
or irrelevant. Local paths are replaced by `<repo>` (the repository),
`<git-source>` (the Git source clone) and `<scratch>` (a scratch directory).

```text
Review only these parts of spec.md in <repo>: the hint sections "Keep track of stash entries?", "Push your other local branches?", and "Fetch to see the newest remote commits?"; the precedence list in Hint structure, item 5; the "Plain `git-hints`" bullet in "Language and libraries"; the "Documentation links" section; the paragraph in "Testing" that begins "Inspection must keep working"; and the introduction of "Development strategy", up to the "Implementation Strategy" heading. Check for technical inaccuracies, contradictions with the rest of spec.md or with the code in src/git_hints/, missing decisions, and ambiguous or untestable statements. Avoid stylistic suggestions. A clone of the Git source is at <git-source> (tag v2.56.0), and you may create scratch repositories under <scratch>/spec-review to check Git's behavior. Do not modify any file in the repository. Report the findings as a numbered list, each with the location, the problem, and why it matters, followed by the total number of findings.
```

I checked these claims against Git 2.56.0 and the Git source, and found them correct: `--decorate-refs` honored by `%D` only with `--decorate` before 2.35; the `grafted` decoration not being filtered; a root commit with an empty tree hidden by `--simplify-by-decoration`; per-worktree `FETCH_HEAD` paths; an empty `FETCH_HEAD` after a fetch from an empty remote (exit 0) and after a fetch from a missing directory (exit 128); `--dry-run` and `--no-write-fetch-head` writing no `FETCH_HEAD`; the push refusal when a tag has the branch's name; `git diff` taking `index.lock` whatever `GIT_OPTIONAL_LOCKS` says; and the anchors moving on origin/master. `scripts/check_doc_links.py` against v2.56.1 exits 0. The "Plain `git-hints`" bullet and the Testing paragraph produced no findings.

<del>1\. **Location:** "Push your other local branches?", the Command field (spec.md:1812-1813) and condition 5.2 (spec.md:1879-1881). **Problem:** When the upstream has a different name, the spec suggests `git push <remote> <branch>:<remote-branch>` and marks it safe. The most common way to get that state is `git switch -c feature origin/main`, which sets the upstream to `origin/main` automatically. In a scratch repository the tool then printed `feature (ahead of origin/main by 1 commit)` with `Command: git push origin feature:main`. That command fast-forwards the remote `main` with the feature commits. Plain `git push` refuses this under the default `push.default=simple` ("The upstream branch of your current branch does not match the name of your current branch"). The linked UPSTREAM BRANCHES section also says the upstream "must have the same name" by default. **Why it matters:** A hint labeled safe publishes feature work directly onto the shared default branch, bypassing the protection Git gives by default. The test case never covers a branch whose upstream has a different name. `push-ahead` (`HEAD:<upstream>`) has the same pattern.</del>

2. **Location:** "Push your other local branches?", condition 5.1 and the Command and Result (spec.md:1818-1819, 1869-1884).
   **Problem:** A branch without an upstream is always reported as `(no upstream)` with `git push -u origin <branch>`. No check is made for an existing `refs/remotes/origin/<branch>`. Reproduced: someone else pushed `topic`, and a local `topic` was created from `main` without tracking. The hint suggested `git push -u origin topic`, and Git rejected it as `(non-fast-forward)`.
   **Why it matters:** Condition 5.3 skips a diverged branch only when it has an upstream. The no-upstream case gets a command that fails, while the spec promises "Afterward, this hint no longer lists the branch."

3. **Location:** "Fetch to see the newest remote commits?", test case steps 6-7 (spec.md:2028-2040).
   **Problem:** Step 6 leaves `FETCH_HEAD` empty (the fetch from the empty remote) and only restores the URL. Step 7 therefore starts from an already empty file, so "the last fetch failed or fetched nothing" and "`path` is empty" hold whether or not the failed fetch emptied the file. Setting the age to two days has no effect on an empty file.
   **Why it matters:** The test never checks condition 4's claim that "a fetch that cannot reach its remote" leaves `FETCH_HEAD` empty. The claim is true in 2.56, but a regression in Git or in the implementation would pass. Running `git fetch` after restoring the URL in step 6 would fix this.

<del>4\. **Location:** "Push your other local branches?", condition 5.1 (spec.md:1870-1878). **Problem:** The skip for an upstream that maps to no remote-tracking branch is justified by "a push does not create that remote-tracking branch". It also hides every later commit on that branch. After `git push -u origin nf` in a single-branch clone, further commits on `nf` are never reported. This is not listed among the known limitations. **Why it matters:** This is a silent false negative for single-branch clones and for remotes whose fetch refspec does not cover the branch. The spec should either record it as a limitation or decide differently.</del>

5. **Location:** "Push your other local branches?", condition 3 (spec.md:1846-1847).
   **Problem:** "Ignore empty lines, which root and merge commits produce" is only half right. With `--simplify-by-decoration` and no pathspec, `rev_compare_tree` (revision.c:791-803 at v2.56.0) returns SAME for any undecorated commit, so merges are dropped. I tested a merge with one interesting parent and a `--no-ff` merge with two uninteresting parents, and neither printed a line. Only undecorated root commits with a non-empty tree produce empty lines (`rev_same_tree_as_empty`).
   **Why it matters:** Ignoring empty lines is harmless, but the stated reason is wrong. Someone writing a test from it would build a case that cannot happen.

<del>6\. **Location:** "Keep track of stash entries?", Command field (spec.md:1735-1737), compared with Hint structure item 6. **Problem:** Item 6 requires every `Warning:` command to "instruct the user to back up first". For `git stash pop 0` the spec only says to check the changes with `git stash show`. That inspects the changes but does not back them up, and it does not point to the safe alternative (apply now, drop later). **Why it matters:** This contradicts the safety-labeling rule for a command that deletes a stash entry.</del>

7. **Location:** "Fetch to see the newest remote commits?", conditions 1-4 (spec.md:1978-1998).
   **Problem:** Unlike `stash-entries` and `unpushed-branches`, this section gives no expected exit codes for `git for-each-ref --count=1 refs/remotes/` or the `git rev-parse` call. Nothing says what happens when stat'ing or reading `FETCH_HEAD` fails (permissions, a concurrent truncation). The failure-reporting rules in Language and libraries cover only failed commands.
   **Why it matters:** This hint is the first to read Git-internal files directly. An OS error has no defined outcome: it could be reported as an inspection failure, skipped, or crash the tool.

8. **Location:** Documentation links, test case checks 1-2 (spec.md:2753-2757).
   **Problem:** "Each URL in the table" means different things in the two checks. Each entry also holds a replacement URL; check 1 must include it, but check 2 must exclude it, since replacements never appear in hint sections. `tests/test_docs.py` makes that split on its own. The test also fails on bare manual URLs in hint sections, which the spec does not require.
   **Why it matters:** A check implemented exactly as written either fails on every moving anchor or does not match the existing test.

9. **Location:** Documentation links, introduction and the closing paragraph of "Choosing and deriving anchors" (spec.md:2659-2661, 2727).
   **Problem:** The spec describes the current links as "mostly whole pages" and says "no CodeChat Editor markup was added". Both are now false: `docs.py` holds section anchors, and fragment markers and gather headings exist. "In this phase" is not defined anywhere, and Development strategy defines no phases.
   **Why it matters:** The spec is declared the single source of truth. Stale statements about the current state, and a rule whose scope ("this phase") cannot be determined, make it unclear whether the re-selection of links is still required.

<del>10\. **Location:** Development strategy introduction (spec.md:3003-3006). **Problem:** The spec says "a decision recorded in it applies where it differs from those parts; its descriptions of the existing code do not limit the changes". It gives no way to tell a decision from a description. "One `ThreadPoolExecutor` worker per check" and "Operation-in-progress suppression is applied inside the checks" could be either. "Until then" has no end condition. **Why it matters:** The clause can override the rest of the specification, but no one can tell when it does, so it cannot be tested.</del>

Total findings: 10

I rejected finding 1 because the specification chooses this command for both
`push-ahead` and `unpushed-branches`, finding 4 because step 5.1 and test step
11 skip such a branch on purpose, finding 6 because the warning already names
what is lost and what to check first, and finding 10 because the clause is a
note about merging the remaining subsection, not a behavior.

#### Implementation review rounds

I wrote the implementation with Claude Opus 5.5 in Claude Code. Each round used
the same model with the prompt shown under Last implementation review; it
reviewed the implementation of the Documentation links section and the push
commands for branch names that start with `+`.

| Round | Findings | Main changes made |
| ----- | -------- | ----------------- |
| 1     | 3        | The list of moving anchors names all four, and a test comment no longer cites a removed example; 1 finding rejected because the specification does not require each hint's test to assert its link |
| 2     | 4        | `tests/test_docs.py` also checks that each entry's kind fits its URL and that no URL repeats; 3 findings rejected because they contradict what the specification chose for the test and the script |

#### Last implementation review

Prompting Claude Opus 5.5 in Claude Code with the following prompt produced the
round 2 output below; strikethrough indicates findings that I deemed incorrect
or irrelevant, and local paths are replaced as above.

```text
Review the implementation of these parts of spec.md in <repo>: the "Documentation links" section, which is implemented by src/git_hints/docs.py, the links in src/git_hints/proactive.py and src/git_hints/reactive.py, tests/test_docs.py, scripts/check_doc_links.py, and the CodeChat markup in the code and in spec.md; and the push commands of `unpushed-branches` and `no-upstream-branch` for branch names that start with `+`. Check that the code does what the specification says, that the tests can detect violations of it, and that the script's output and exit codes follow it; verify claims about Git's documentation against the Git source at <git-source> and the live pages on git-scm.com. Avoid stylistic suggestions. You may create scratch files under <scratch>/impl-review-2. Do not modify any file in the repository. Report the findings as a numbered list, each with the location, the problem, and why it matters, followed by the total number of findings.
```

I found 4 problems: one low-to-medium test gap and three low ones. Nothing else in the scope is wrong, and I changed no file in the repository.

**What checks out:**
- **Live links:** all 28 table URLs exist as `id=` on git-scm.com today (2026-11-17). The site serves 2.56.1; git-push says "2.55.1 → 2.56.1 no changes".
- **Source anchors:** every section anchor exists at v2.56.1. Exactly the four entries that record a replacement print `moves` at origin/master (e1ec09b23c), and all four replacements exist there.
- **Spec examples:** these all match the Git source and the live pages: `UPSTREAM-BRANCHES`, `_remotes` plus `REMOTES`, `_note_about_fast_forwards`, `_rebase_vs_pullmerge` (git-svn), `_internalssparse_checkout`, `git-tag#_configuration_2`, and `litdd=&#x2d;&#x2d;` (Makefile:227, meson.build:300).
- **Links in the hint modules:** every link URL and title in proactive.py and reactive.py equals its spec hint section. The only exception is the not-yet-implemented `stale-fetch`. `OPERATIONS` gives the four `operation-in-progress` entries.
- **Script:** `scripts/check_doc_links.py` exits 0 on runs with and without `--site`. It exits 2 for a missing tag, a missing origin/master, or missing arguments.
- **Tests:** 13 of my 16 mutations make `tests/test_docs.py` fail. That includes changed or dropped spec links, reference links, autolinks, HTML links, angle-bracket links, URLs in other modules, missing records and http URLs.
- **CodeChat markup:** I modelled the CodeChat Editor's pest Python lexer and its `following` handling from its source.
  - All 80 fragments end their comment and cover exactly their function.
  - IDs are `cc-` plus 10 characters from the editor's alphabet, and they are unique.
  - All 24 gather headings list fragments that exist, every fragment is gathered, and each heading reads "Implementation of" plus the section title.
- **`+` branches:** I checked with Git 2.56.0. `git push -u origin +plus` fails with "src refspec plus does not match any". `git push -u origin refs/heads/+plus` pushes and sets `branch.+plus.merge`. Both hints and both tests use the `refs/heads/` form.

**Findings**

<del>1\. **A link can bypass the table without any test failing (low-medium).** - Location: - `src/git_hints/docs.py:281-284`: `TABLE` is built from the module's global names. - `tests/test_docs.py:393-413`: check 3 skips docs.py entirely. - `spec.md:2759` and `spec.md:2764`. - Problem: `TABLE` only contains `Doc` objects bound to their own module-level name. Check 3 exempts all of docs.py. So a plain URL constant in docs.py, or a `Doc` written directly inside `OPERATIONS`, can be used in hint text without checks 1, 2 and 4 or the script ever seeing it. - Evidence: in a scratch copy I added `GIT_LOG_URL = "https://git-scm.com/docs/git-log#_bogus"` to docs.py and used it for the push-ahead link. `tests/test_docs.py` and `tests/test_remote.py` passed (12 passed). The same change to the `behind` link failed `test_behind`. - Why it matters: it breaks the spec's requirement that hint text refers to table entries. The spec's "so every link comes from the table" and "Check 2 can pass only when every link the code shows is in a hint section" are then untrue. No hint test asserts the links of push-ahead, no-upstream-branch, bisect-in-progress, unstaged-changes, stash-entries ("apply or drop") or operation-in-progress ("stage"), so a bypass there goes unnoticed.</del>

<del>2\. **The script reports `ok` offline for sections the live page leaves out, and the spec's "which `--site` confirms" is untrue (low).** - Location: `spec.md:2795-2796`; `scripts/check_doc_links.py:129-132` and `171-175`. - Evidence: I compared the script's IDs at v2.56.1 with the live headings of all 207 `git*` pages. - 204 match exactly. - The other 3 differ only by sections inside `ifdef::`/`ifndef::` blocks: - git-log: `_bisection_helpers` (`ifdef::git-rev-list[]`, `rev-list-options.adoc:826`). - git-replay: `_bisection_helpers` and `_commit_formatting` (`ifndef::git-shortlog,git-replay[]`, line 1120). - git-shortlog: `_commit_ordering`, `_bisection_helpers`, `_object_traversal` and `_commit_formatting`. - For an entry `git-log#_bisection_helpers` the script prints `ok` without `--site` and `missing-site` with it. - The deciding attributes are set in the page sources themselves (`git-log.adoc:18` `:git-log: 1`, `git-shortlog.adoc:117`, `git-replay.adoc:118`), so they could be evaluated offline. - Why it matters: a section-anchor entry records only a Git version and is verified offline; `--site` is optional. Such an entry would pass the documented procedure while broken on the site. No current entry is affected.</del>

<del>3\. **The section-title rule differs from Asciidoctor's (low, not triggered by any page at v2.56.1).** - Location: `spec.md:2785-2790`; `scripts/check_doc_links.py:258-278`, whose comment says "as in Asciidoctor". - Problem: in Asciidoctor 2.0.23, an underlined title must contain a letter or digit; an underscore does not count. A line starting with `.` (a block title) is never a section title. A title is only recognised at the start of a block: a paragraph runs until a blank line or a delimiter line. The script treats `.Example`, or the last line of a paragraph, as a section when a `----` delimiter within one character of its length follows. The listing's closing delimiter then opens a new block that runs to the next identical line or to the end of the file, hiding real sections. - Evidence: on a scratch page containing `.Block title`, a `------------` listing, then `AFTER` underlined with `-----`, `collect_ids` returns `['_block_title']` and no `_after`. The paragraph case ("…\nFor example:\n------------") behaves the same. - Why it matters: a real anchor below such a construct would print `missing` (exit 1), and an anchor that doesn't exist would print `ok`. No page at v2.56.1 has this pattern.</del>

4. **The entry's kind and the one-entry-per-passage rule are never checked (low).**
   - Location: `tests/test_docs.py:416-457`; `scripts/check_doc_links.py:480-496`; `spec.md:2711-2713` and `2732-2738`.
   - Problem: check 4 picks the required field from `kind` but never compares `kind` with the URL's fragment, and nothing checks for duplicate URLs. So:
     - A whole-page URL recorded as a section with a version passes check 4. The script then prints `whole-page <url>` with no reason and exits 0, although the spec requires a reason.
     - A section anchor recorded as an option with a date is never checked against the `.adoc` source. The script prints only `unchecked`, never `missing` or `moves`.
     - A second entry with the same URL passes every check.
   - Evidence: the duplicate-entry and kind-swap mutations pass `tests/test_docs.py`. The current table has 28 unique URLs, and each kind matches its URL form.
   - Why it matters: the spec relies on each record to know how its link was verified, and a wrong kind silently skips that verification.

Total: 4 findings.

Everything is in `<scratch>/impl-review-2/`:
- `frag.py`: fragment coverage model.
- `compare.py` and `compare-all.txt`: script IDs compared with live headings.
- `mutate.py` and `mut/`: the mutation runs.
- `pages/`: live HTML.
- `adoc/`: Asciidoctor 2.0.23 sources.
- `exp/`: the `+plus` push experiment.

I rejected finding 1 because check 3 exempts `docs.py` as the specification
says, finding 2 because the specification collects titles in `ifdef::` blocks
on purpose and leaves their confirmation to `--site`, and finding 3 because the
script follows the title rule that the specification defines.

### Aiym Takimbayeva

GitHub userid: Aiym-Takimbayeva

#### Contributions

Aiym Takimbayeva moved the Specification gaps subsection into the parts of the
spec it concerns (`commit-identity`, `detached-head`, a new `bisect-in-progress`
section, `not-a-repo`, `behind`, `diverged`, `tracked-but-ignored`, and
`explain`), drafting the edits with Claude Opus 5.5, and had GitHub Copilot
implement and review the matching code and tests.

#### Specification review rounds

Each round used GitHub Copilot in VS Code (Agent mode, automatically routed to
`mai-code-1.1-flash`). Round 1 asked it to review the latest commit; rounds 2
and 3 used the prompt shown under Last specification review.

| Round | Findings | Main changes made                                                                                                                                                                                    |
| ----- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1     | 0        | None; the prompt covered only the latest commit, so later rounds named the changed sections.                                                                                                         |
| 2     | 2        | `detached-head` says "not on any local branch" and "to return to a branch that already contains this commit", since the check covers only local branches and `git switch` keeps uncommitted changes. |
| 3     | 1        | None; the finding was rejected, as explained below.                                                                                                                                                  |

#### Last specification review

Prompting GitHub Copilot in VS Code (Agent mode, automatically routed to
`mai-code-1.1-flash`) with the following prompt produced the output below;
strikethrough indicates LLM output that I deemed incorrect or irrelevant. Hint
structure, item 7, requires the `error/blocked` hint only for an unresolved or
stopped operation, and its next sentence says a healthy bisect is explained by
`bisect-in-progress`, so the two statements do not contradict each other.

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
selection), which routed the implementation in round 1 to `gpt-6-luna` and the
reviews in rounds 2 and 3 to `mai-code-1.1-flash`. Every round ended with the
full test suite, Ruff, and ty passing.

| Round | Findings | Main changes made                                                                                                                                                                                                                                                              |
| ----- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1     | –        | Implementation: `detached-head` wording in `proactive.py`, a standard-output note in `reactive.py`, and tests for `not-a-repo`, `commit-identity`, the bisect files, `merge-conflicts`, and the suppression of `behind`, `diverged`, and `tracked-but-ignored`; 60 tests pass. |
| 2     | 0 (+1)   | The LLM found nothing; my own review found that two new assertions in `test_detached_head` matched hint wording, which Testing forbids, so they were removed.                                                                                                                  |
| 3     | 0        | None.                                                                                                                                                                                                                                                                          |

#### Last implementation review

Prompting GitHub Copilot in VS Code (Agent mode, automatically routed to
`mai-code-1.1-flash`) with the following prompt produced the output below.

```text
Review the code and test changes in the last two commits (git show HEAD~1 HEAD) against spec.md. Check that they implement the spec correctly and follow its Testing rules. Do not modify any files. Report findings as a numbered list, then the total number of findings.
```

1. No issues found in the reviewed changes. The detached-head wording
   adjustments match the spec, and the test change removes wording-based
   assertions in favor of ID-based checks, which is consistent with the spec's
   Testing rules.

Total findings: 0
