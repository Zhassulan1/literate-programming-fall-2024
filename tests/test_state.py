# `test_state.py` -- Tests for hints about the repository's state
# ===============================================================
#
# Each test follows the test case of the same name in the specification;
# tests without one cover requirements stated elsewhere in it.
import json
import os
import subprocess
from pathlib import Path

import pytest
from git_test_tools import (
    all_blocks,
    blocks,
    collapse,
    commit_file,
    config_user,
    git,
    hint_ids,
    make_repo,
    make_temps,
    run_hints,
    write,
)

NOT_IN_WORK_TREE = (
    "Not inside a working tree (bare repository or .git directory); "
    "run git-hints from the project directory."
)


def git_paths(repo: Path, *names: str) -> list[Path]:
    args = ["rev-parse", "--path-format=absolute"]
    for name in names:
        args += ["--git-path", name]
    return [Path(line) for line in git(repo, *args).stdout.splitlines()]


def current_branch(repo: Path) -> subprocess.CompletedProcess[str]:
    return git(repo, "symbolic-ref", "--quiet", "--short", "HEAD", check=False)


def trace_environments(path: Path) -> list[tuple[list[str], dict[str, str]]]:
    events = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
    ]
    processes: dict[str, tuple[list[str], dict[str, str]]] = {}
    for event in events:
        sid = event.get("sid")
        if not sid:
            continue
        if event.get("event") == "start":
            processes[sid] = (event["argv"], {})
        elif event.get("event") == "def_param" and sid in processes:
            processes[sid][1][event["param"]] = event["value"]
    return list(processes.values())


# Location
# --------
def test_not_a_repo(tmp_path_factory: pytest.TempPathFactory) -> None:
    (directory,) = make_temps(tmp_path_factory, 1)
    result = git(directory, "rev-parse", "--is-inside-work-tree", check=False)
    assert result.returncode == 128
    assert hint_ids(directory) == ["not-a-repo"]
    lines, found = all_blocks(directory)
    block = found["not-a-repo"]
    assert "Command: git clone <repository-url>" in block
    assert "Command: git init" in block
    assert "https://git-scm.com/docs/git-clone" in block
    assert "https://git-scm.com/docs/git-init" in block
    assert lines[0] == "ID: not-a-repo"
    git(directory, "init", "-b", "main")
    assert "not-a-repo" not in hint_ids(directory)


def test_not_inside_work_tree(tmp_path_factory: pytest.TempPathFactory) -> None:
    bare, repo = make_temps(tmp_path_factory, 2)
    make_repo(bare, [["git", "init", "--bare", "-b", "main"]])
    make_repo(repo, [["git", "init", "-b", "main"]])
    for directory in (bare, repo / ".git"):
        result = run_hints(directory, "--all")
        assert result.returncode == 0, result.stderr
        assert result.stdout.splitlines() == [NOT_IN_WORK_TREE]
        result = run_hints(directory, "--all", "--ids-only")
        assert result.returncode == 0
        assert result.stdout == ""


def test_inspection_environment(
    tmp_path_factory: pytest.TempPathFactory,
) -> None:
    repo, remote = make_temps(tmp_path_factory, 2)
    trace_dir = tmp_path_factory.mktemp("trace")
    config_user("user1", "user1@example.com")
    make_repo(remote, [["git", "init", "--bare", "-b", "main"]])
    git(repo.parent, "clone", str(remote), str(repo))
    make_repo(
        repo,
        [
            write(repo / "foo.txt", "base"),
            ["git", "add", "foo.txt"],
            ["git", "commit", "-m", "Add foo."],
            ["git", "push", "-u", "origin", "main"],
        ],
    )

    trace = trace_dir / "inspection.json"
    env = dict(os.environ)
    env.update(
        GIT_TRACE2_EVENT=str(trace),
        GIT_TRACE2_ENV_VARS="GIT_OPTIONAL_LOCKS,LC_ALL",
        LC_ALL="C.UTF-8",
    )
    result = run_hints(repo, "--all", env=env)
    assert result.returncode == 0, result.stderr
    processes = trace_environments(trace)
    assert processes
    for _, values in processes:
        assert values == {"GIT_OPTIONAL_LOCKS": "0", "LC_ALL": "C"}

    explain_trace = trace_dir / "explain.json"
    env["GIT_TRACE2_EVENT"] = str(explain_trace)
    result = run_hints(
        repo,
        "explain",
        "--",
        "git",
        "status",
        "--short",
        env=env,
    )
    assert result.returncode == 0, result.stderr
    processes = trace_environments(explain_trace)
    explained = [
        values
        for args, values in processes
        if args[-2:] == ["status", "--short"]
    ]
    inspected = [
        values
        for args, values in processes
        if args[-2:] != ["status", "--short"]
    ]
    assert explained == [{"LC_ALL": "C.UTF-8"}]
    assert inspected
    for values in inspected:
        assert values == {"GIT_OPTIONAL_LOCKS": "0", "LC_ALL": "C"}

    old = (repo / "foo.txt").stat().st_mtime - 3600
    os.utime(repo / "foo.txt", (old, old))
    (index_lock,) = git_paths(repo, "index.lock")
    index_lock.write_bytes(b"")
    try:
        result = run_hints(repo, "--all")
        assert result.returncode == 0, result.stderr
        assert result.stdout.splitlines()[0] == "Branch: main"
        assert not any(
            line.startswith("git-hints:") for line in result.stderr.splitlines()
        )
        assert index_lock.read_bytes() == b""
    finally:
        index_lock.unlink(missing_ok=True)

    write(repo / "bar.txt", "next")()
    git(repo, "add", "bar.txt")
    git(repo, "commit", "-m", "Add bar.")
    git(repo, "tag", "main")
    assert "push-ahead" in hint_ids(repo)


def reported_failures(stderr: str) -> list[str]:
    return [
        line for line in stderr.splitlines() if line.startswith("git-hints: ")
    ]


def test_failure_reporting(tmp_path_factory: pytest.TempPathFactory) -> None:
    repo, empty, local, remote, pusher, pusher_remote = make_temps(
        tmp_path_factory, 6
    )
    config_user("user1", "user1@example.com")
    make_repo(
        repo,
        [
            ["git", "init", "-b", "main"],
            write(repo / "foo.txt", "base"),
            ["git", "add", "foo.txt"],
            ["git", "commit", "-m", "Add foo."],
            ["git", "remote", "add", "origin", str(empty)],
            write(repo / "foo.txt", "base\nmore"),
        ],
    )
    ids = hint_ids(repo)
    assert "no-upstream-branch" in ids
    assert "unstaged-changes" in ids
    # An unreadable index makes every Git command that reads it exit with 128.
    (index,) = git_paths(repo, "index")
    index.write_bytes(b"garbage")

    result = run_hints(repo, "--all")
    assert result.returncode == 1
    assert result.stdout.splitlines()[0] == "Branch: main"
    found = blocks(result.stdout)
    assert "no-upstream-branch" in found
    assert "unstaged-changes" not in found
    # Each failed command is reported once, with its exit code.
    failures = reported_failures(result.stderr)
    assert failures
    assert len(set(failures)) == len(failures)
    assert all("128" in line for line in failures)

    result = run_hints(repo, "--all", "--ids-only")
    assert result.returncode == 1
    ids = result.stdout.splitlines()
    assert "no-upstream-branch" in ids
    assert "unstaged-changes" not in ids
    assert not any(line.startswith("Branch:") for line in ids)
    assert sorted(reported_failures(result.stderr)) == sorted(failures)

    # Git's own message comes first, then the failed `merge-conflicts`
    # inspection.
    for options, stdout_line in (
        ([], "Git exited with code 128."),
        (["--ids-only"], None),
    ):
        result = run_hints(
            repo, *options, "explain", "--", "git", "status", "--short"
        )
        assert result.returncode == 1
        if stdout_line is None:
            assert result.stdout == ""
        else:
            assert stdout_line in result.stdout.splitlines()
        lines = result.stderr.splitlines()
        fatal = [i for i, line in enumerate(lines) if line.startswith("fatal:")]
        failed = [
            i for i, line in enumerate(lines) if line.startswith("git-hints: ")
        ]
        assert fatal and failed
        assert fatal[0] < failed[0]
        assert "--diff-filter=U" in lines[failed[0]]
        assert "128" in lines[failed[0]]

    # With no `git` executable on `PATH`, Git cannot be launched.
    env = dict(os.environ, PATH=str(empty))
    for args in (["--all"], ["explain", "--", "git", "status"]):
        result = run_hints(repo, *args, env=env)
        assert result.returncode == 1
        assert result.stdout == ""
        assert result.stderr.startswith("git-hints: ")
        assert len(reported_failures(result.stderr)) == 1

    # The integration-failure counter and the `merge-conflicts` check both
    # fail to read the index; each failed command is reported once, and the
    # counter's state file is left unchanged.
    make_repo(remote, [["git", "init", "--bare", "-b", "main"]])
    make_repo(
        local,
        [
            ["git", "init", "-b", "main"],
            ["git", "remote", "add", "origin", str(remote)],
            write(local / "foo.txt", "base"),
            ["git", "add", "foo.txt"],
            ["git", "commit", "-m", "Add foo."],
            ["git", "push", "-u", "origin", "main"],
            ["git", "commit", "--amend", "-m", "Add foo again."],
        ],
    )
    index, counts = git_paths(
        local, "index", "git-hints/integration-failures.json"
    )
    index.write_bytes(b"garbage")
    for options in ([], ["--ids-only"]):
        result = run_hints(local, *options, "explain", "--", "git", "push")
        assert result.returncode == 1
        if options:
            found = result.stdout.splitlines()
        else:
            found = list(blocks(result.stdout))
        assert "push-rejected-non-fast-forward" in found
        failures = reported_failures(result.stderr)
        assert failures
        assert len(set(failures)) == len(failures)
        assert not counts.exists()

    # A state file that cannot be written is reported, naming the file.
    make_repo(pusher_remote, [["git", "init", "--bare", "-b", "main"]])
    make_repo(
        pusher,
        [
            ["git", "init", "-b", "main"],
            ["git", "remote", "add", "origin", str(pusher_remote)],
            write(pusher / "foo.txt", "base"),
            ["git", "add", "foo.txt"],
            ["git", "commit", "-m", "Add foo."],
            ["git", "push", "-u", "origin", "main"],
            ["git", "commit", "--amend", "-m", "Add foo again."],
        ],
    )
    (state,) = git_paths(pusher, "git-hints/integration-failures.json")
    state.mkdir(parents=True)
    result = run_hints(pusher, "explain", "--", "git", "push")
    assert result.returncode == 1
    assert "push-rejected-non-fast-forward" in blocks(result.stdout)
    failures = reported_failures(result.stderr)
    assert len(failures) == 1
    assert "integration-failures.json" in failures[0]

    # Git ended by a signal has the exit code a shell would report.
    if os.name != "nt":
        result = run_hints(
            pusher,
            "explain",
            "--",
            "git",
            "-c",
            "alias.die=!kill -TERM $PPID",
            "die",
        )
        assert result.returncode == 143
        assert "Git exited with code 143." in result.stdout.splitlines()


# `detached-head`
# ---------------
def test_detached_head(tmp_path_factory: pytest.TempPathFactory) -> None:
    local, remote = make_temps(tmp_path_factory, 2)
    config_user("user1", "user1@example.com")
    make_repo(remote, [["git", "init", "--bare", "-b", "main"]])
    make_repo(
        local,
        [
            ["git", "init", "-b", "main"],
            ["git", "remote", "add", "origin", str(remote)],
            write(local / "foo.txt", "xxx"),
            ["git", "add", "foo.txt"],
            ["git", "commit", "-m", "Add foo."],
            write(local / "foo.txt", "xxxy"),
            ["git", "commit", "-am", "Append y."],
            write(local / "foo.txt", "xxxyz"),
            ["git", "commit", "-am", "Append z."],
        ],
    )
    branch = current_branch(local)
    assert (branch.returncode, branch.stdout.strip()) == (0, "main")
    result = run_hints(local, "--all")
    assert result.returncode == 0
    assert result.stdout.splitlines()[0] == "Branch: main"
    ids = hint_ids(local)
    assert "detached-head" not in ids
    assert "no-upstream-branch" in ids

    git(local, "switch", "--detach", "HEAD")
    assert current_branch(local).returncode == 1
    assert (
        git(
            local, "rev-parse", "--verify", "--quiet", "HEAD^{commit}"
        ).returncode
        == 0
    )
    operation_paths = git_paths(
        local, "rebase-merge", "rebase-apply", "BISECT_START"
    )
    assert not any(path.exists() for path in operation_paths)

    lines, found = all_blocks(local)
    block = found["detached-head"]
    assert "Priority: informational" in block
    assert "git switch -c" in block
    assert "git switch main" in block
    assert "https://git-scm.com/docs/git-checkout#_detached_head" in block
    assert lines[0] == "Branch: detached HEAD"
    ids = hint_ids(local)
    assert "detached-head" in ids
    assert "no-upstream-branch" not in ids
    assert "no-commits" not in ids

    # Commit while detached.
    make_repo(
        local,
        [
            write(local / "foo.txt", "xxxyzw"),
            ["git", "commit", "-am", "Append w."],
        ],
    )
    containing = git(
        local,
        "for-each-ref",
        "--contains",
        "HEAD",
        "--format=%(refname:short)",
        "refs/heads",
    )
    assert containing.stdout == ""
    _, found = all_blocks(local)
    block = found["detached-head"]
    assert "Priority: data-loss risk" in block
    assert "git switch -c" in block
    assert "git switch main" not in block
    git(local, "switch", "-c", "saved-work")
    assert current_branch(local).stdout.strip() == "saved-work"
    assert "detached-head" not in hint_ids(local)

    # Bisect.
    git(local, "bisect", "start", "HEAD", "HEAD~2")
    try:
        assert current_branch(local).returncode == 1
        assert git_paths(local, "BISECT_START")[0].exists()
        result = run_hints(local, "--all")
        assert result.returncode == 0
        assert result.stdout.splitlines()[0] == "Branch: detached HEAD"
        ids = hint_ids(local)
        assert "detached-head" not in ids
        assert "no-upstream-branch" not in ids
        assert "bisect-in-progress" in ids
        # Operation-state paths must resolve correctly from a subdirectory.
        (local / "sub").mkdir()
        assert "detached-head" not in hint_ids(local / "sub")
    finally:
        git(local, "bisect", "reset")
    assert current_branch(local).stdout.strip() == "saved-work"
    assert not git_paths(local, "BISECT_START")[0].exists()

    # A stopped rebase.
    missing = "refs/heads/git-hints-test-missing"
    assert (
        git(
            local, "show-ref", "--verify", "--quiet", missing, check=False
        ).returncode
        != 0
    )
    rebase = subprocess.run(
        [
            "git",
            "rebase",
            "--exec",
            f"git rev-parse --verify {missing}",
            "HEAD~1",
        ],
        cwd=local,
        shell=False,
        check=False,
        capture_output=True,
    )
    try:
        assert rebase.returncode != 0
        assert current_branch(local).returncode == 1
        assert git_paths(local, "rebase-merge")[0].exists()
        result = run_hints(local, "--all")
        assert result.returncode == 0
        assert result.stdout.splitlines()[0] == "Branch: detached HEAD"
        ids = hint_ids(local)
        assert "detached-head" not in ids
        assert "no-upstream-branch" not in ids
    finally:
        git(local, "rebase", "--abort")
    assert current_branch(local).stdout.strip() == "saved-work"
    assert not any(
        path.exists()
        for path in git_paths(local, "rebase-merge", "rebase-apply")
    )
    git(local, "switch", "--detach", "HEAD")
    assert "detached-head" in hint_ids(local)
    bisect_log = git_paths(local, "BISECT_LOG")[0]
    bisect_log.touch()
    try:
        ids = hint_ids(local)
        assert "detached-head" in ids
        assert "bisect-in-progress" not in ids
    finally:
        bisect_log.unlink(missing_ok=True)

    bisect_start = git_paths(local, "BISECT_START")[0]
    bisect_start.touch()
    try:
        ids = hint_ids(local)
        assert "detached-head" not in ids
        assert "bisect-in-progress" in ids
    finally:
        bisect_start.unlink(missing_ok=True)
        git(local, "switch", "saved-work")


# An unreadable HEAD is reported separately, with a nonzero exit, while other
# hints are still shown.
def test_invalid_detached_head(
    tmp_path_factory: pytest.TempPathFactory,
) -> None:
    (repo,) = make_temps(tmp_path_factory, 1)
    config_user("user1", "user1@example.com")
    make_repo(repo, [["git", "init", "-b", "main"]])
    commit_file(repo, "foo.txt", "xxx", "Add foo.")
    # `commit-identity` doesn't depend on HEAD, so it still triggers.
    git(repo, "config", "--global", "--unset", "user.email")
    (repo / ".git" / "HEAD").write_text("1" * 40 + "\n", encoding="utf-8")
    result = run_hints(repo, "--all", "--ids-only")
    assert result.returncode == 1
    assert "HEAD is detached but names no commit" in result.stderr
    assert "commit-identity" in result.stdout.splitlines()
    assert "detached-head" not in result.stdout.splitlines()


# `no-commits`
# ------------
def test_no_commits(tmp_path_factory: pytest.TempPathFactory) -> None:
    local, remote = make_temps(tmp_path_factory, 2)
    config_user("user1", "user1@example.com")
    make_repo(remote, [["git", "init", "--bare", "-b", "main"]])
    make_repo(
        local,
        [
            ["git", "init", "-b", "main"],
            ["git", "remote", "add", "origin", str(remote)],
        ],
    )
    head = git(local, "rev-parse", "--verify", "--quiet", "HEAD", check=False)
    assert (head.returncode, head.stdout, head.stderr) == (1, "", "")
    assert current_branch(local).stdout.strip() == "main"
    assert (
        git(
            local,
            "show-ref",
            "--verify",
            "--quiet",
            "refs/heads/main",
            check=False,
        ).returncode
        == 1
    )
    assert (
        git(local, "diff", "--cached", "--quiet", check=False).returncode == 0
    )

    lines, found = all_blocks(local)
    assert lines[0] == "Branch: main"
    block = found["no-commits"]
    assert "git status" in block and "git add" in block
    assert "https://git-scm.com/docs/git-add" in block
    assert "git commit" not in block
    ids = hint_ids(local)
    assert "no-commits" in ids
    for absent in (
        "detached-head",
        "many-changed-files",
        "staged-changes",
        "no-upstream-branch",
    ):
        assert absent not in ids

    write(local / "foo.txt", "xxx")()
    lines, found = all_blocks(local)
    assert lines[0] == "Branch: main"
    assert "git commit" not in found["no-commits"]
    ids = hint_ids(local)
    assert "no-commits" in ids and "untracked-files" in ids
    for absent in ("detached-head", "many-changed-files", "staged-changes"):
        assert absent not in ids

    git(local, "add", "foo.txt")
    assert (
        git(local, "diff", "--cached", "--quiet", check=False).returncode == 1
    )
    assert (
        git(
            local, "rev-parse", "--verify", "--quiet", "HEAD", check=False
        ).returncode
        == 1
    )
    _, found = all_blocks(local)
    block = found["no-commits"]
    assert 'git commit -m "Initial commit"' in block
    assert "https://git-scm.com/docs/git-commit" in block
    ids = hint_ids(local)
    assert "no-commits" in ids and "staged-changes" in ids
    assert "detached-head" not in ids and "many-changed-files" not in ids

    git(local, "commit", "-m", "Initial commit")
    assert git(local, "rev-parse", "--verify", "--quiet", "HEAD").stdout.strip()
    assert current_branch(local).stdout.strip() == "main"
    assert (
        git(local, "diff", "--cached", "--quiet", check=False).returncode == 0
    )
    lines, _ = all_blocks(local)
    assert lines[0] == "Branch: main"
    ids = hint_ids(local)
    assert "no-upstream-branch" in ids
    for absent in (
        "no-commits",
        "detached-head",
        "many-changed-files",
        "staged-changes",
    ):
        assert absent not in ids

    git(local, "switch", "--orphan", "fresh")
    try:
        assert current_branch(local).stdout.strip() == "fresh"
        assert (
            git(
                local, "rev-parse", "--verify", "--quiet", "HEAD", check=False
            ).returncode
            == 1
        )
        assert (
            git(
                local,
                "show-ref",
                "--verify",
                "--quiet",
                "refs/heads/fresh",
                check=False,
            ).returncode
            == 1
        )
        assert (
            git(
                local,
                "show-ref",
                "--verify",
                "--quiet",
                "refs/heads/main",
                check=False,
            ).returncode
            == 0
        )
        assert (
            git(local, "diff", "--cached", "--quiet", check=False).returncode
            == 0
        )
        lines, found = all_blocks(local)
        assert lines[0] == "Branch: fresh"
        block = found["no-commits"]
        assert "git status" in block and "git add" in block
        assert "git commit" not in block
        ids = hint_ids(local)
        assert "no-commits" in ids
        for absent in (
            "detached-head",
            "many-changed-files",
            "staged-changes",
            "no-upstream-branch",
        ):
            assert absent not in ids
    finally:
        git(local, "switch", "main")


# `operation-in-progress`
# -----------------------
OPERATIONS = ("merge", "rebase", "cherry-pick", "revert")


# Check the block for one operation: it names the operation, links to its
# documentation, and shows only its continue and abort commands.
def check_operation_block(block: str, operation: str) -> None:
    text = collapse(block)
    assert f"A {operation} [1] is in progress" in text
    assert f"git {operation} --continue" in text
    assert f"Warning: git {operation} --abort" in text
    assert f"https://git-scm.com/docs/git-{operation}" in text
    for other in OPERATIONS:
        if other != operation:
            assert f"git {other} --continue" not in text
            assert f"git {other} --abort" not in text


def test_operation_in_progress(
    tmp_path_factory: pytest.TempPathFactory,
) -> None:
    (repo,) = make_temps(tmp_path_factory, 1)
    make_repo(repo, [["git", "init", "-b", "main"]])
    config_user("user1", "user1@example.com")
    commit_file(repo, "foo.txt", "base", "Add foo.")
    assert "operation-in-progress" not in hint_ids(repo)
    make_repo(
        repo,
        [
            ["git", "switch", "-c", "topic"],
            write(repo / "foo.txt", "topic"),
            ["git", "commit", "-am", "Topic change."],
            ["git", "switch", "main"],
            write(repo / "foo.txt", "main"),
            ["git", "commit", "-am", "Main change."],
        ],
    )

    # Merge conflict.
    assert git(repo, "merge", "topic", check=False).returncode != 0
    try:
        assert (
            git(
                repo, "rev-parse", "--verify", "--quiet", "MERGE_HEAD"
            ).returncode
            == 0
        )
        assert git(
            repo, "diff", "--name-only", "--diff-filter=U"
        ).stdout.split() == ["foo.txt"]
        lines, found = all_blocks(repo)
        assert lines[0] == "Branch: main"
        block = found["operation-in-progress"]
        check_operation_block(block, "merge")
        assert "foo.txt" in block
        assert "git add" in block
        assert "operation-in-progress" in hint_ids(repo)

        # Resolved but not yet continued.
        make_repo(
            repo,
            [write(repo / "foo.txt", "resolved"), ["git", "add", "foo.txt"]],
        )
        assert "operation-in-progress" in hint_ids(repo)
        _, found = all_blocks(repo)
        block = collapse(found["operation-in-progress"])
        assert "No conflicts remain" in block
        assert "git merge --continue" in block
        assert "foo.txt" not in block

        git(repo, "merge", "--continue")
    finally:
        if (
            git(
                repo,
                "rev-parse",
                "--verify",
                "--quiet",
                "MERGE_HEAD",
                check=False,
            ).returncode
            == 0
        ):
            git(repo, "merge", "--abort")
    assert (
        git(
            repo, "rev-parse", "--verify", "--quiet", "MERGE_HEAD", check=False
        ).returncode
        == 1
    )
    assert "operation-in-progress" not in hint_ids(repo)

    # Abort.
    make_repo(
        repo,
        [
            ["git", "switch", "-c", "topic2"],
            write(repo / "foo.txt", "topic2"),
            ["git", "commit", "-am", "Topic change 2."],
            ["git", "switch", "main"],
            write(repo / "foo.txt", "main2"),
            ["git", "commit", "-am", "Main change 2."],
        ],
    )
    assert git(repo, "merge", "topic2", check=False).returncode != 0
    try:
        assert "operation-in-progress" in hint_ids(repo)
    finally:
        git(repo, "merge", "--abort")
    assert "operation-in-progress" not in hint_ids(repo)

    # Rebase.
    git(repo, "switch", "topic2")
    assert git(repo, "rebase", "main", check=False).returncode != 0
    try:
        assert git_paths(repo, "rebase-merge")[0].is_dir()
        lines, found = all_blocks(repo)
        check_operation_block(found["operation-in-progress"], "rebase")
        assert "cherry-pick" not in found["operation-in-progress"]
        assert lines[0] == "Branch: detached HEAD"
        assert "detached-head" not in hint_ids(repo)
        make_repo(
            repo,
            [write(repo / "foo.txt", "resolved2"), ["git", "add", "foo.txt"]],
        )
        git(repo, "rebase", "--continue")
        assert "operation-in-progress" not in hint_ids(repo)
    finally:
        if git_paths(repo, "rebase-merge")[0].exists():
            git(repo, "rebase", "--abort")

    # Cherry-pick.
    make_repo(
        repo,
        [
            ["git", "switch", "main"],
            ["git", "switch", "-c", "pick-src"],
            write(repo / "foo.txt", "pick"),
            ["git", "commit", "-am", "Pick change."],
            ["git", "switch", "main"],
            write(repo / "foo.txt", "main3"),
            ["git", "commit", "-am", "Main change 3."],
        ],
    )
    assert git(repo, "cherry-pick", "pick-src", check=False).returncode != 0
    try:
        assert (
            git(
                repo, "rev-parse", "--verify", "--quiet", "CHERRY_PICK_HEAD"
            ).returncode
            == 0
        )
        _, found = all_blocks(repo)
        check_operation_block(found["operation-in-progress"], "cherry-pick")
    finally:
        git(repo, "cherry-pick", "--abort")
    assert "operation-in-progress" not in hint_ids(repo)

    # Revert.
    make_repo(
        repo,
        [
            write(repo / "foo.txt", "main4"),
            ["git", "commit", "-am", "Main change 4."],
        ],
    )
    assert git(repo, "revert", "HEAD~1", check=False).returncode != 0
    try:
        assert (
            git(
                repo, "rev-parse", "--verify", "--quiet", "REVERT_HEAD"
            ).returncode
            == 0
        )
        _, found = all_blocks(repo)
        check_operation_block(found["operation-in-progress"], "revert")
    finally:
        git(repo, "revert", "--abort")
    assert "operation-in-progress" not in hint_ids(repo)


# `commit-identity`
# -----------------
def test_commit_identity(tmp_path_factory: pytest.TempPathFactory) -> None:
    (repo,) = make_temps(tmp_path_factory, 1)
    make_repo(repo, [["git", "init", "-b", "main"]])
    _, found = all_blocks(repo)
    block = found["commit-identity"]
    assert "Priority: workflow" in block
    assert 'git config --global user.name "Your Name"' in block
    assert 'git config --global user.email "you@example.com"' in block
    assert "https://git-scm.com/docs/git-config" in block

    # Fixing only the name leaves the email missing.
    git(repo, "config", "--global", "user.name", "user1")
    _, found = all_blocks(repo)
    block = found["commit-identity"]
    assert "user.name" not in block.split("Command:", 1)[1]
    assert 'git config --global user.email "you@example.com"' in block

    git(repo, "config", "--global", "user.email", "user1@example.com")
    assert "commit-identity" not in hint_ids(repo)

    # An empty local value overrides the global one and is fixed locally.
    git(repo, "config", "--local", "user.email", "")
    _, found = all_blocks(repo)
    assert (
        'git config --local user.email "you@example.com"'
        in found["commit-identity"]
    )
