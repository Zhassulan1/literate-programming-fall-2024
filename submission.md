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
specification. Rounds 3–12 reviewed only the failure-reporting requirements of
Language and libraries and their test case with Claude Opus 5.5
(`claude-opus-5-5`, in Claude Code), using the prompt shown under Last
specification review. Rounds 11 and 12 confirmed the section on the final
state, after the other team members' later changes; round 12 found only repeats
and requests for more detail than the specification needs, so it changed
nothing.

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
| 11    | 6        | Required the signal handler to be installed before Git is launched, required each failure report to be one line, and added the `No hints.` check to step 2 of the failure-reporting test. |
| 12    | 6        | No changes; every finding repeated a settled decision or asked for more detail than the specification needs. |

#### Last specification review

Prompting Claude Opus 5.5 (`claude-opus-5-5`, in Claude Code) with the
following prompt produced the round 12 output below; strikethrough indicates
LLM output that Madina deemed incorrect or irrelevant.

```text
Review ONLY the failure-reporting requirements in the "Language and libraries" section of spec.md (the paragraphs on exit codes and on reporting unexpected inspection failures and failures to launch Git) and the "Test case for the failure reporting of Language and libraries" in the "Testing" section. Check for technical inaccuracies, contradictions with existing requirements, missing implementation decisions, and ambiguous or untestable statements. Do not review other sections. Do not modify any files. Report only relevant, actionable findings in a numbered list, followed by the total number of findings. Avoid stylistic suggestions and unnecessary expansion.
```

Confirmation review of the failure-reporting requirements in spec.md (Language and libraries, lines ~2678-2725) and the test case "Test case for the failure reporting of Language and libraries" (lines ~3035-3123).

Before writing these findings I checked the test's assumptions against Git 2.56.0 in a scratch repository, and they all hold. With the index replaced by `garbage`: `git status`, `git diff --diff-filter=U` and the other index-reading commands exit 128; `git branch --show-current` and `git stash list` exit 0; `git push` is still rejected as non-fast-forward with exit 1. Setting `core.repositoryformatversion 2` makes `rev-parse --is-inside-work-tree` exit 128 with "Expected git repo version <= 1", not "not a git repository". The `die` alias ends Git with returncode -15 (143). The `kill -INT 0` alias in a new session ends Git with -2 (130), prints `stopped`, and leaves a parent with no-op handlers alive.

1. <del>Multi-line error messages versus the "one line" rule (line 2695ff). The failure must be reported as one line that includes "the command's error message, if any". Git's stderr can span several lines, for example <code>error: bad signature ...</code> followed by <code>fatal: index file corrupt</code> for a larger corrupt index, and paths can contain newlines. The spec does not say how to fold these into one line (join them, keep only the last <code>fatal:</code> line, or escape them). It also does not say what the launch-failure message must contain, such as the command and the OS error text. Tests only check the <code>git-hints: </code> prefix, so implementations may differ. State the folding rule and the minimum content of the launch-failure message.</del>

2. <del><code>explain</code> outside a working tree is not covered. For plain <code>git-hints</code>, exit 128 with "not a git repository" is defined as expected (<code>not-a-repo</code>), and so is output <code>false</code> (Hint structure, item 1). For the inspection that <code>explain</code> runs after the command, neither case is stated. This inspection includes the working-tree check of <code>merge-conflicts</code> ("In a working tree, run ...") and "Skip failure counting outside a working tree". Take <code>git-hints explain -- git status</code> run in a non-repository directory. Read literally, the 128 from the inspection's <code>rev-parse</code> could count as an unexpected inspection failure, so <code>git-hints</code> would exit 1 instead of Git's 128. State that these results are expected in <code>explain</code> and that the state-dependent reactive hints are then skipped.</del>

3. <del>Plain <code>git-hints</code> when Git cannot be launched in the middle of a run. "When Git cannot be launched, report it once, stop, and print nothing on standard output" is clarified only for <code>explain</code>, where a later launch failure is an ordinary inspection failure. For plain <code>git-hints</code>, a launch failure after the context-line commands have succeeded fits two rules: "stop, print nothing" and "still print the output that does not depend on the failed commands". Say which rule applies, for example the same rule as for <code>explain</code>.</del>

4. <del>With <code>--ids-only</code>, Git's exit status is lost. When an inspection failure replaces Git's exit code with 1, <code>--ids-only</code> also suppresses <code>Git exited with code &lt;n&gt;.</code>. Nothing then shows whether the user's Git command succeeded. In the step 8 scenario under <code>--ids-only</code>, a successful <code>git push --force</code> looks the same as a failed push: exit 1 and empty stdout. Decide whether the <code>git-hints: </code> line, or some other output, must still carry Git's exit code in this case.</del>

5. <del>The invalid or unreadable repository state rule has no test. The rule that output showing an invalid or unreadable repository state is an unexpected inspection failure, with the problem described in the message, has no test in this test case. This covers <code>detached-head</code> condition 2 and <code>no-commits</code> condition 2. It can be reproduced: write a well-formed 40-hex ID of a nonexistent object into HEAD. <code>rev-parse --is-inside-work-tree</code> still succeeds and <code>HEAD^{commit}</code> fails. The rule that under <code>--fetch</code> a failure of the remote-choosing commands stops all output is also untested. Add steps for both (exit 1, one <code>git-hints: </code> line, and the expected stdout).</del>

6. <del>Signal names are not defined for Windows (line 2685ff). "Ignore the interrupt and quit signals" names no platform behaviour, and <code>signal.SIGQUIT</code> does not exist on Windows (Ctrl+Break arrives as <code>SIGBREAK</code>). Name the signals to catch on each platform, for example <code>SIGINT</code> plus <code>SIGQUIT</code> where it exists, so the Windows implementation does not crash or miss Ctrl+Break.</del>

Total: 6

#### Implementation review rounds

Claude Fable 5.2 assisted the implementation, as recorded in the three commit
trailers. Both implementation-review rounds 1 and 2 used GPT-6-Luna to review
the failure-reporting tests and `stash-entries` implementation against
`spec.md`. Claude Opus 5.5 (`claude-opus-5-5`, in Claude Code) implemented
`stale-fetch`, the fixes, and the CodeChat markup, and reviewed them in rounds
3–11 with the prompt shown under Last implementation review; rounds 7 and 8
rechecked the code after specification rounds 8–10 changed it, and rounds 9–11
confirmed the final state after specification rounds 11 and 12 and the other
team members' changes to `stale-fetch`. Round 11 found only two test-setup
refinements, which were left as trivial.

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
| 9     | 0        | No changes. |
| 10    | 2        | Made `stale-fetch` examine both `FETCH_HEAD` files and report each failing one while still suppressing the hint, and moved the remaining clone and init setup of the remote tests to `make_repo()`. |
| 11    | 2        | No changes; both findings are trivial test-setup refinements that do not change what the tests check. |

#### Last implementation review

Prompting Claude Opus 5.5 (`claude-opus-5-5`, in Claude Code) with the
following prompt produced the round 11 output below.

```text
Review the implementation in src/git_hints/ and tests/ of these parts of spec.md: the "Keep track of stash entries?" and "Fetch to see the newest remote commits?" hint sections with their complete test cases, the failure reporting of "Language and libraries" with its test case in "Testing", and the "CodeChat markup" rules as applied to stash-entries, unpushed-branches, and stale-fetch. Check conditions, suppression, output text, ordering, error handling, edge cases, and whether each test implements every step of its test case. Do not review other parts. Do not modify files. Report only relevant, actionable findings as a numbered list, followed by the total number of findings.
```

```text
Review scope: spec.md "Keep track of stash entries?" and "Fetch to see the newest remote commits?" (hint text, conditions, suppression, ordering, test cases), the failure reporting of "Language and libraries" with its test case, and CodeChat markup for stash-entries, unpushed-branches and stale-fetch. I checked src/git_hints/proactive.py (stash_entries, unpushed_branches markup, stale_fetch, collect_hints, show_hints, fetch), git.py (InspectionError, FileInspectionError, file_status, Repo), reactive.py (explain, record_integration_outcome, save_counts/load_counts, signals_caught) and hint.py (PRECEDENCE, rendering), plus tests/test_changes.py::test_stash_entries, tests/test_remote.py (stale-fetch tests and helpers) and tests/test_state.py::test_failure_reporting.

The code and tests match the spec in almost every respect. The relevant tests pass with Git 2.56.0.
- **Conditions and suppression:** match the spec, including am/bisect/unmerged and successful `--fetch`.
- **Output text and links:** match.
- **Ordering:** stash-entries is in PRECEDENCE and sorts before stale-fetch.
- **FETCH_HEAD handling:** the two FETCH_HEAD files, the newest-mtime choice, the empty-file case, the >24h rule, rounding down and future times are all correct.
- **Failure reporting:** one `git-hints:` line per failed command or file, removal of duplicates, exit 1, context-line failures print nothing on stdout, launch failures, signal exit codes 128+N, and state-file read vs. write failures all work as the spec says.
- **Tests:** every step of all three test cases is implemented.
- **CodeChat markup:** every `following` count covers the whole function or test, the gather headings list the right fragments in order, the IDs are unique and in the right format, and no markers appear in hint text.

Findings:

1. tests/test_remote.py:605-606 (test_stale_fetch, step 9) and tests/test_remote.py:631 (test_stale_fetch_inspection_failure): setup steps don't go through `make_repo`. They call `append(...)()` directly and run `git stash push` through `git()`. Testing says to "use make_repo() to set up repositories", and file-operation lambdas are meant to be passed to `make_repo`. test_stash_entries does it the right way, e.g. `make_repo(repo, [append(...), ["git", "stash", "push"]])`. Fix: use `make_repo(local, [append(local / "foo.txt", "more\n"), ["git", "stash", "push"]])` and `make_repo(wt, [append(wt / "foo.txt", "more\n")])`.

2. tests/test_remote.py:517 copies `reported_failures` from tests/test_state.py:201, and the copy sits inside the stale-fetch helper fragment `cc-p96xv0fgyp` (following="5"). So the gather heading for "Fetch to see the newest remote commits?" shows a general failure-parsing helper as if it were stale-fetch code. CodeChat markup says helpers shared by several hints get no fragment. Fix: move `reported_failures` into tests/git_test_tools.py, import it in both test files, and lower the fragment's `following` from 5 to 3.

Total: 2 findings.
```

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
| 8     | 9        | `no-upstream-branch` stays silent when an upstream is configured but does not resolve; inspection runs `git diff` with `diff.autoRefreshIndex=true`; file errors on `FETCH_HEAD` are unexpected inspection failures, with a test step; the stash-apply result and the `git am` suppression are stated; 4 findings rejected because the specification records the decision or the step checks what it claims |
| 9     | 7        | `no-upstream-branch` skips a push that would be rejected; `detached-head` and `changes-on-default-branch` are hidden while `git switch` would fail; the partial `git stash apply` outcome and the shell quoting policy are stated; the Development strategy list records these changes |
| 10    | 8        | None; this was the confirming round, 2 findings rejected as contradicting recorded decisions, and the others recorded below without changes |

#### Last specification review

Prompting Claude Opus 5.5 in Claude Code with the following prompt produced the
round 10 output below; strikethrough indicates findings that I deemed incorrect
or irrelevant. Local paths are replaced by `<repo>` (the repository),
`<git-source>` (the Git source clone) and `<scratch>` (a scratch directory).

```text
Review only these parts of spec.md in <repo>: the hint sections "Keep track of stash entries?", "Push your other local branches?", and "Fetch to see the newest remote commits?"; the precedence list in Hint structure, item 5; the "Plain `git-hints`" bullet in "Language and libraries"; the "Documentation links" section; the paragraph in "Testing" that begins "Inspection must keep working"; and the introduction of "Development strategy", up to the "Implementation Strategy" heading. Check for technical inaccuracies, contradictions with the rest of spec.md or with the code in src/git_hints/, missing decisions, and ambiguous or untestable statements. Avoid stylistic suggestions. A clone of the Git source is at <git-source> (tag v2.56.0), and you may create scratch repositories under <scratch>/spec-review to check Git's behavior. Do not modify any file in the repository. Report the findings as a numbered list, each with the location, the problem, and why it matters, followed by the total number of findings.
```

Scope notes: spec.md has no "Implementation Strategy" heading any more (commit 517fcb5 removed it), so I reviewed the whole "Development strategy" section, lines 3177-3222. For Git source I used `git show v2.56.0:...`, because the clone's HEAD is v2.56.0-398. The installed git is 2.56.0. I tested behavior in repositories under `<scratch>/spec-review`. I modified no repository file.

The following were checked and hold, so they are not listed below:
- The `git log --branches --not --remotes --simplify-by-decoration ... %D` claims: HEAD and tags are excluded, `log.excludeDecoration` is overridden, an empty-tree root is hidden, other roots give empty lines, and the pre-2.35 `--decorate` note is right (commits 14b9c2b3e3 and be73860793).
- The `for-each-ref` field layout, the `[gone]` case and the case where an upstream is set but its remote-tracking branch is missing.
- The ordering in the push-command quoting test.
- `FETCH_HEAD` is truncated before Git contacts the remote (2.34 and 2.56), so a failed fetch or one that fetches nothing leaves it empty. The path from `rev-parse --git-path FETCH_HEAD --git-common-dir` is right in a linked worktree.
- `refresh_index_quietly` takes the index lock whatever `GIT_OPTIONAL_LOCKS` says, and `git commit -a` holds `index.lock` while its editor is open.
- The anchor-derivation examples, the anchors that move on master (`DETACHED_HEAD`, `EXAMPLES`, `gitmergeconflicts#markers` and `#resolve`), and the `PRECEDENCE` list in hint.py, which matches item 5.

Findings:

1. "Keep track of stash entries?", Command field, `git stash apply 0` result (spec.md lines 1781-1786; the same text is in proactive.py lines 1131-1138).
   - Problem: two of the claimed outcomes are wrong on Git 2.56.0. In builtin/stash.c (`goto restore_untracked`), when an untracked file the entry saved already exists, Git applies the tracked changes and also restores every other untracked file. It skips only the existing one ("u1.txt already exists, no checkout"). The spec says it applies "only the tracked changes". When Git refuses the tracked changes ("Your local changes ... would be overwritten ... Aborting"), it still restores the untracked files. I reproduced both: u2.txt was restored in the first case, and u1.txt and u2.txt in the second.
   - On Git 2.34, the supported minimum, behavior differs again. Before commit 71cade5a0b (v2.35.0), Git returns early on a conflict or refusal and restores no untracked files.
   - Why it matters: the Result field promises how Git behaves. A user told that Git "refused" will not expect new untracked files. A retry then fails on the files that were already restored. The test only checks the phrase `could not restore the untracked files`, so it cannot catch this.

2. "Development strategy", the list of changes (lines 3185-3207).
   - Problem 1: the list leaves out a new behavior. Since f7bb1a1/aa463a5 (spec) and 8246bee (code), `git-hints explain` ignores SIGINT and SIGQUIT while Git runs, and reports a Git process ended by a signal as 128+N. It has its own test, failure-reporting step 6. The code at df09bce, which the section treats as the existing implementation, has neither. It is not an "unexpected failure", so the bullet about failure reporting does not cover it.
   - Problem 2: the list misclassifies `GIT_OPTIONAL_LOCKS=0` and `LC_ALL=C`. The df09bce code already set both (git.py lines 80-88), yet they are listed as changes instead of under "Behavior that the code already had". The same applies to the basic `git-hints:` exit-1 reporting.
   - Why it matters: this section is the team's record of what changed. It also backs the rule that every behavior change comes with a test, which cannot be checked against an inaccurate list.

3. "Development strategy", bullet on `detached-head` and `changes-on-default-branch` (lines 3196-3201).
   - Problem: the reason "because their `git switch` commands would fail" is wrong for one case: unmerged paths with no operation in progress, for example after a conflicting `git stash pop`. There `git switch -c <name>`, the main command of `detached-head`, succeeds. Only `git switch <branch>` fails ("you need to resolve your current index first"). I reproduced this in the `um` scratch repository.
   - The `detached-head` section's own wording (step 4) is accurate. But it hides the whole hint, including its `data-loss risk` warning, for a reason that applies only to the optional second command.
   - Why it matters: the stated reason does not justify the decision. Either suppress only the `git switch <branch>` line while unmerged paths exist, or give the real reason.

4. Testing, the step beginning "Inspection must keep working" (lines 3070-3078).
   - Problem: the setup says moving the modification time makes "`git diff` try to refresh the index", but nothing checks this. Other steps state such things as checked preconditions. Step 4, for example, checks that `diff.autoRefreshIndex=false` lists the files. Nothing checks either that the stat-only file stays unreported while the refresh cannot be saved (`unstaged-changes` absent).
   - Why it matters: the step passes even if the setup stops triggering a refresh. It only shows that nothing crashed, not that the refresh-under-lock path ran or was harmless.

5. "Keep track of stash entries?", Command field, `Warning: git stash pop 0` (lines 1789-1791).
   - Problem: Hint structure item 6 requires a `Warning:` command to "instruct the user to back up first". The pop text only says to view the changes with `git stash show`. Viewing is not a backup. The drop text at least asks the user to confirm the changes are applied or committed.
   - Why it matters: this contradicts a rule the spec sets for every `Warning:` command.

<del>6\. Hint structure, item 5, precedence list (lines 214-221). - Problem: the stated criterion is "specifically important state hints ahead of routine suggestions". `stash-entries` is a reminder, and its own Related output says so. Its place in the list only puts it ahead of `stale-fetch`, another reminder, since `bisect-in-progress` and `not-a-repo` never appear together with it. `unpushed-branches` and `stale-fetch` are left out without a reason. - Why it matters: "Future IDs that require special precedence must be added" has no rule a maintainer can apply. It matters because the order decides what the three-hint limit cuts off.</del>

<del>7\. Documentation links, Maintenance script, items 2 and 4 (lines 2933-2950). - Problem: `moves <url>` is printed both for an entry with a recorded replacement (expected) and for one without (an unrecorded move that needs action). Both exit 0, and the spec does not say whether the second case should fail or be marked differently. - Why it matters: the section asks that each expected replacement be recorded, but the script's exit code does not enforce it. A newly found move can pass unnoticed.</del>

8. Documentation links, Maintenance script (line 2908) compared with src/git_hints/docs.py line 47 and the `version=` fields.
   - Problem: the spec gives `v2.56.0` as the example of "the release that `git-scm.com` serves". The table says its section anchors "were verified against Git 2.56.1, the release `git-scm.com` serves", and v2.56.1 (2026-10-23) exists in the clone.
   - Why it matters: a maintainer following the spec checks an older release than the one the table records. The pages linked are the same at both tags, so this is low severity.

Total: 8 findings.

I rejected finding 6 because the precedence list is a deterministic rule that
places `stash-entries` on purpose, and finding 7 because the specification
defines `moves` as an early warning that does not fail the run. Round 10
confirmed the fixes of round 9. I recorded its other findings without acting on
them: findings 1 and 2 are minor (the outcome of `git stash apply` when untracked
files already exist, and two behaviors the Development strategy list does not
name), and findings 3 to 5 and 8 are wording or test-strength points. Another
round of fixes would again need a confirming review, and the assignment warns
that LLM-driven changes produce an overspecified result.

#### Implementation review rounds

I wrote the implementation with Claude Opus 5.5 in Claude Code. Each round used
the same model with the prompt shown under Last implementation review; it
reviewed the implementation of the Documentation links section and the push
commands for branch names that start with `+`. From round 4 on, the prompt also
covers the later changes to `unpushed-branches`, `no-upstream-branch`,
`detached-head`, `changes-on-default-branch`, and the inspection `git diff`.

| Round | Findings | Main changes made |
| ----- | -------- | ----------------- |
| 1     | 3        | The list of moving anchors names all four, and a test comment no longer cites a removed example; 1 finding rejected because the specification does not require each hint's test to assert its link |
| 2     | 4        | `tests/test_docs.py` also checks that each entry's kind fits its URL and that no URL repeats; 3 findings rejected because they contradict what the specification chose for the test and the script |
| 3     | 8        | The link checks also catch URLs in fenced blocks and link titles, the script renders link macros in titles, and the hint tests assert their remaining documentation links; 3 findings rejected because they contradict what the specification chose for the checks and the script |
| 4     | 3        | Both refusals of `git switch` (an `am` session and a merge) now hide `changes-on-default-branch`; 2 trivial findings recorded without changes |
| 5     | 6        | None; this was the confirming round, 1 finding rejected as contradicting the specification, and the others recorded below without changes |

#### Last implementation review

Prompting Claude Opus 5.5 in Claude Code with the following prompt produced the
round 5 output below; strikethrough indicates findings that I deemed incorrect
or irrelevant, and local paths are replaced as above.

```text
Review the implementation of these parts of spec.md in <repo>: the "Documentation links" section, which is implemented by src/git_hints/docs.py, the links in src/git_hints/proactive.py and src/git_hints/reactive.py, tests/test_docs.py, scripts/check_doc_links.py, and the CodeChat markup in the code and in spec.md; the push commands of `unpushed-branches` and `no-upstream-branch` for branch names that start with `+`; and the later changes to `unpushed-branches`, `no-upstream-branch`, `detached-head`, `changes-on-default-branch`, and the inspection `git diff` (`diff.autoRefreshIndex`) in src/git_hints/proactive.py and src/git_hints/git.py, with their tests. Check that the code does what the specification says, that the tests can detect violations of it, and that the script's output and exit codes follow it; verify claims about Git's documentation against the Git source at <git-source> and the live pages on git-scm.com. Avoid stylistic suggestions. You may create scratch files under <scratch>/impl-review-5. Do not modify any file in the repository. Report the findings as a numbered list, each with the location, the problem, and why it matters, followed by the total number of findings.
```

**Review of `<repo>:` 6 findings, none in the documentation-link machinery**

**Checked with no findings:**
- **Full suite:** 74 tests pass.
- **Links in the code:** every link in `proactive.py` and `reactive.py` matches the spec's hint text and comes from `docs.py`.
- **`test_docs.py`:** checks 1–5 are implemented as specified, and its reader finds all 56 manual URLs in the hint sections.
- **`check_doc_links.py`:**
  - Against v2.56.1 offline it prints ok/moves/unchecked and exits 0. With `--site` it exits 0. Against `origin/master` it prints `missing` and exits 1. A bad tag or checkout exits 2 before any check.
  - Its derived IDs match the `id=` attributes on about 130 live git-scm.com pages. The only extra IDs are ones inside `ifdef`/`ifndef` blocks (`git-log`, `git-replay`, `git-shortlog`), which the spec allows. The only missing ones are footnotes.
- **Spec claims checked against the Git source and live pages, all correct:**
  - `UPSTREAM-BRANCHES`, `REMOTES`, `_remotes` and `_configuration_2`.
  - `_internalssparse_checkout`, `_rebase_vs_pullmerge` and `todo`.
  - `{litdd}`.
  - The 4 anchors that move on master (`origin/master` matches `ls-remote`, the new `gitmergeconflicts` page is in no release and returns 404 on the site), and the 2.56.1 release that git-scm.com serves.
  - The 4 option-ID dates.
  - `git switch` refusing during operations (`builtin/checkout.c:1624-1655`).
  - The forced index refresh: `diff.autoRefreshIndex` sets `skip_stat_unmatch`, and `refresh_index_quietly` takes the lock without checking `GIT_OPTIONAL_LOCKS`.
- **CodeChat:** in a simulation of CodeChat's Python block splitter, every `following` value covers exactly its function. All IDs are `cc-` plus 10 characters, unique, gathered, and none clash with the `<h4>` IDs.
- **Push commands:** names starting with `+` are written as `refs/heads/<branch>` in both hints.

**Findings**

1. **No test catches reversed arguments in the new `no-upstream-branch` ancestry check.**
   - **Where:** `tests/test_remote.py:320-325`, spec.md test case step 12 (lines 735-739), code at `src/git_hints/proactive.py:612-615`.
   - **Problem:** Step 12 only tests a remote branch equal to HEAD and a diverged one. I swapped the arguments to `merge-base --is-ancestor HEAD refs/remotes/origin/<branch>` in a scratch copy and the whole suite still passed (74 passed).
   - **Why it matters:** with the arguments swapped, the hint disappears in its most common case: the branch was pushed without `-u` and then got new local commits. The `unpushed-branches` test (step 8) has an "ahead" step; this test case needs one too, such as a commit after `git push origin side`.

<del>2\. **`detached-head` in its `data-loss risk` variant is hidden while unmerged paths exist, although its only command works.** - **Where:** spec.md 1117-1120 and the Development strategy bullet at 3196-3201; `src/git_hints/proactive.py:309`. - **Problem:** the stated reason is that the hint's `git switch` commands would fail. But `git switch -c <name>` with no start point skips `merge_working_tree` (`only_merge_on_switching_branches`, `builtin/checkout.c:1199-1207`), so it does not refuse unmerged paths. Only `git switch <branch>` does (line 887). The data-loss variant shows only `git switch -c`. - **Reproduced:** two commits on no branch, then a conflicting `git stash pop`. `git-hints --all` shows only `merge-conflicts`, and `git switch -c rescue` exits 0. - **Why it matters:** the one hint that warns those commits can be lost disappears without the reason the spec gives.</del>

3. **The new suppressions miss a cherry-pick or revert sequence in which Git still refuses `git switch`.**
   - **Where:** spec.md 1408-1417 (`changes-on-default-branch` step 4) and 1117-1120 (`detached-head`); `src/git_hints/git.py:397-419`; `proactive.py:964` and `:309`.
   - **Problem:** detection relies only on `CHERRY_PICK_HEAD` and `REVERT_HEAD`. Git's `wt_status_get_state` (`wt-status.c:1950-1958`) also reports a cherry-pick or revert from `.git/sequencer`.
   - **Reproduced:** `git cherry-pick A B` stops on a conflict at A; resolve it, `git commit`, and edit a file on the default branch. `CHERRY_PICK_HEAD` is gone and `sequencer/` remains. `git-hints` lists `changes-on-default-branch`, while `git switch -c x` fails with "cannot switch branch while cherry-picking".
   - **Why it matters:** this contradicts the stated reason for the change ("`git switch` refuses to run during a … cherry-pick, revert"). `operation-in-progress` documents this limitation for itself, but these two sections do not.

4. **Most of the new `detached-head` suppressions are untested.**
   - **Where:** spec.md test case steps 17-18 (1224-1234); `tests/test_state.py:624-656`.
   - **Problem:** only merge and unmerged paths are exercised. Replacing `operations.combining` with `operations.merge or operations.rebase` (which drops cherry-pick, revert and `git am`) still passes `test_detached_head`. The same is true, from before this change, of `changes-on-default-branch` with cherry-pick and revert (removing them still passes `test_changes_on_default_branch`).
   - **Why it matters:** the Development strategy requires a test for every behavior change. Here the tests cannot detect the loss of the cherry-pick, revert, or `git am` suppression.

5. **The code does not check what `changes-on-default-branch` step 4 specifies.**
   - **Where:** spec.md 1411-1414, versus `Repo.operations` in `src/git_hints/git.py:399-418`.
   - **Problem:** the spec says to suppress the hint "if any returned path exists" for `MERGE_HEAD`, `CHERRY_PICK_HEAD`, `REVERT_HEAD`, `rebase-merge` and `rebase-apply`. The code instead resolves `MERGE_HEAD`, `CHERRY_PICK_HEAD` and `REVERT_HEAD` with `rev-parse --verify` and requires `rebase-merge` and `rebase-apply` to be directories. The same directory test applies to `detached-head` step 4 ("if any of the returned paths exists").
   - **Reproduced:** with an empty `.git/MERGE_HEAD`, or a `rebase-merge` regular file, `changes-on-default-branch` is still listed. `git switch -c` refuses in both cases, because Git only `stat`s `MERGE_HEAD` and the rebase paths (`wt-status.c:1934`).
   - **Why it matters:** this is a narrow, corrupted-state case, but the code diverges from the spec, and the spec's version matches Git.

6. **The quoting rule's PowerShell claim is wrong for curly quotes in branch names.**
   - **Where:** spec.md Hint structure item 2 (162-167), which `unpushed-branches` now cites (1871-1872); `src/git_hints/hint.py:244-259`.
   - **Problem:** PowerShell treats U+201C, U+201D and U+201E as double quotes, and U+2018, U+2019, U+201A and U+201B as single quotes. Ref names may contain these characters. A branch named `a“b` gets `git push -u origin "a“b"`, which PowerShell splits. On Windows, `it’s$x` gets `'it’s$x'`, where `’` ends the string because only ASCII `'` is doubled.
   - **Why it matters:** the spec says double quotes "work in POSIX shells, PowerShell, and `cmd`" without exception, and the code relies on that. Such names produce push commands that fail in PowerShell.

Total number of findings: 6

Scratch scripts and downloaded pages are in `<scratch>/impl-review-5` (`fragments.py`, `compare.py`, `compare2.py`, `links.py`, and `exp1`–`exp4` for the reproductions). No repository file was modified.

I rejected finding 2 because the specification hides `detached-head` while
unmerged paths exist on purpose. Round 5 confirmed the fixes of round 4. I
recorded its other findings without acting on them: finding 1 is a missing test
case (a branch ahead of its `origin` namesake), and findings 3 to 6 are rare
cases or test-strength points, for the same reason as the specification review.

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
