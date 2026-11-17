# `test_remote.py` -- Tests for hints about upstream branches and fetching
# ========================================================================
#
# Each test follows the test case of the same name in the specification.
import shutil
from pathlib import Path

import pytest
from git_test_tools import (
    all_blocks,
    append,
    collapse,
    commands,
    commit_file,
    config_user,
    git,
    hint_ids,
    make_repo,
    make_temps,
    run_hints,
    write,
)

FETCH_FAILED = "Fetch failed; showing results as of last fetch."


def branch_ab(repo: Path) -> str:
    status = git(repo, "status", "--porcelain=v2", "--branch").stdout
    return next(
        line for line in status.splitlines() if line.startswith("# branch.ab ")
    )


def branch_upstream(repo: Path) -> str:
    status = git(repo, "status", "--porcelain=v2", "--branch").stdout
    return next(
        line
        for line in status.splitlines()
        if line.startswith("# branch.upstream ")
    )


# `push-ahead`
# ------------
# <fragment id="cc-4y5nYGCo86" following="5"></fragment>
def test_push_ahead(tmp_path_factory: pytest.TempPathFactory) -> None:
    remote, local, other = make_temps(tmp_path_factory, 3)
    config_user("user1", "user1@example.com")
    make_repo(remote, [["git", "init", "--bare", "-b", "main"]])
    make_repo(local, [["git", "clone", str(remote), str(local)]])
    make_repo(
        local,
        [
            write(local / "foo.txt", "xxx"),
            ["git", "add", "foo.txt"],
            ["git", "commit", "-m", "Add foo."],
            ["git", "push", "-u", "origin", "main"],
        ],
    )
    assert "push-ahead" not in hint_ids(local)

    make_repo(
        local,
        [
            append(local / "foo.txt", "y"),
            ["git", "commit", "-am", "Change foo."],
        ],
    )
    log = git(local, "log", "--format=%H", "origin/main..HEAD").stdout
    assert len(log.splitlines()) == 1
    ids = hint_ids(local)
    assert "push-ahead" in ids
    assert "behind" not in ids and "diverged" not in ids
    _, found = all_blocks(local)
    block = found["push-ahead"]
    assert "As of last fetch: " in block
    assert "git push origin HEAD:main" in commands(block)
    assert "https://git-scm.com/docs/git-push#_description" in block

    make_repo(other, [["git", "clone", str(remote), str(other)]])
    commit_file(other, "other.txt", "other", "Add other.")
    git(other, "push")
    git(local, "fetch")
    assert branch_ab(local) == "# branch.ab +1 -1"
    ids = hint_ids(local)
    assert "push-ahead" not in ids
    assert "diverged" in ids

    # Different local and upstream branch names.
    make_repo(
        local,
        [
            ["git", "switch", "-c", "dev", "--track", "origin/main"],
            write(local / "dev.txt", "xxx"),
            ["git", "add", "dev.txt"],
            ["git", "commit", "-m", "Add dev."],
        ],
    )
    assert branch_upstream(local) == "# branch.upstream origin/main"
    assert branch_ab(local) == "# branch.ab +1 -0"
    assert "push-ahead" in hint_ids(local)
    _, found = all_blocks(local)
    assert "git push origin HEAD:main" in commands(found["push-ahead"])

    # A local upstream can't be pushed to.
    make_repo(
        local,
        [
            ["git", "switch", "main"],
            ["git", "switch", "-c", "local-test"],
            ["git", "branch", "--set-upstream-to=main", "local-test"],
            write(local / "local.txt", "xxx"),
            ["git", "add", "local.txt"],
            ["git", "commit", "-m", "Add local."],
        ],
    )
    assert branch_upstream(local) == "# branch.upstream main"
    assert branch_ab(local) == "# branch.ab +1 -0"
    assert "push-ahead" not in hint_ids(local)


# `behind`
# --------
#
# Steps 1–5 of the `behind` test case: `repo1` has a commit that `repo2`, its
# clone, hasn't fetched.
def behind_setup(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, Path]:
    repo1, repo2 = make_temps(tmp_path_factory, 2)
    make_repo(repo1, [["git", "init", "-b", "main"]])
    config_user("user1", "user1@example.com")
    commit_file(repo1, "foo.txt", "xxx", "Add foo.")
    make_repo(repo2, [["git", "clone", str(repo1), str(repo2)]])
    make_repo(
        repo1,
        [
            append(repo1 / "foo.txt", "y"),
            ["git", "commit", "-am", "Change foo."],
        ],
    )
    return repo1, repo2


# The `behind` test case, after the setup above.
# <fragment id="cc-wvWM_xhJVH" following="3"></fragment>
def test_behind(tmp_path_factory: pytest.TempPathFactory) -> None:
    repo1, repo2 = behind_setup(tmp_path_factory)
    assert branch_ab(repo2) == "# branch.ab +0 -0"
    assert "behind" not in hint_ids(repo2)

    git(repo2, "fetch")
    assert branch_ab(repo2) == "# branch.ab +0 -1"
    ids = hint_ids(repo2)
    assert "behind" in ids
    assert "diverged" not in ids and "push-ahead" not in ids
    _, found = all_blocks(repo2)
    block = found["behind"]
    assert "As of last fetch: " in block
    assert "git pull" in commands(block)
    assert "https://git-scm.com/docs/git-pull#_description" in block

    make_repo(
        repo1,
        [
            append(repo1 / "foo.txt", "z"),
            ["git", "commit", "-am", "Change foo again."],
        ],
    )
    git(repo2, "fetch")
    assert branch_ab(repo2) == "# branch.ab +0 -2"
    assert "behind" in hint_ids(repo2)

    git(repo2, "pull")
    assert branch_ab(repo2) == "# branch.ab +0 -0"
    assert "behind" not in hint_ids(repo2)

    make_repo(
        repo1,
        [
            append(repo1 / "foo.txt", "w"),
            ["git", "commit", "-am", "Change foo once more."],
        ],
    )
    assert "behind" not in hint_ids(repo2)
    assert "behind" in hint_ids(repo2, "--fetch")
    # A successful fetch removes the qualifier.
    result = run_hints(repo2, "--all", "--fetch")
    assert result.returncode == 0, result.stderr
    assert "As of last fetch" not in result.stdout
    assert FETCH_FAILED not in result.stdout


# `diverged`
# ----------
# <fragment id="cc-EBrzwxTdKn" following="1"></fragment>
def test_diverged(tmp_path_factory: pytest.TempPathFactory) -> None:
    _, repo2 = behind_setup(tmp_path_factory)
    commit_file(repo2, "bar.txt", "zzz", "Add bar.")
    assert branch_ab(repo2) == "# branch.ab +1 -0"
    ids = hint_ids(repo2)
    assert "push-ahead" in ids
    assert "diverged" not in ids

    git(repo2, "fetch")
    assert branch_ab(repo2) == "# branch.ab +1 -1"
    ids = hint_ids(repo2)
    assert "diverged" in ids
    assert "behind" not in ids and "push-ahead" not in ids
    _, found = all_blocks(repo2)
    block = found["diverged"]
    assert "As of last fetch: " in block
    assert (
        "git pull --no-rebase, resolve any conflicts, then git push"
        in commands(block)
    )
    assert any(
        command.startswith("Caution: git pull --rebase")
        for command in commands(block)
    )
    assert "https://git-scm.com/docs/git-pull#_description" in block
    assert (
        "https://git-scm.com/docs/git-push#_note_about_fast_forwards" in block
    )


# Return the IDs that `git-hints` shows during a `git am` session, which Git
# records as a `rebase-apply` directory containing an `applying` file. Only
# these paths tell `git-hints` that a session is in progress, so the test
# creates them instead of stopping a real `git am`.
def ids_during_am(repo: Path) -> list[str]:
    rebase_apply = Path(
        git(
            repo,
            "rev-parse",
            "--path-format=absolute",
            "--git-path",
            "rebase-apply",
        ).stdout.strip()
    )
    rebase_apply.mkdir()
    try:
        (rebase_apply / "applying").touch()
        return hint_ids(repo)
    finally:
        shutil.rmtree(rebase_apply)


# `behind` and `diverged` during a merge or a `git am` session.
# <fragment id="cc-hv2RyOfXis" following="1"></fragment>
def test_upstream_hints_suppressed_during_merge(
    tmp_path_factory: pytest.TempPathFactory,
) -> None:
    _, repo2 = behind_setup(tmp_path_factory)
    git(repo2, "fetch")
    assert "behind" in hint_ids(repo2)
    git(repo2, "merge", "--no-commit", "--no-ff", "origin/main")
    try:
        ids = hint_ids(repo2)
        assert "behind" not in ids
    finally:
        git(repo2, "merge", "--abort")
    assert "behind" not in ids_during_am(repo2)

    commit_file(repo2, "bar.txt", "local\n", "Add local change.")
    git(repo2, "fetch")
    assert "diverged" in hint_ids(repo2)
    git(repo2, "merge", "--no-commit", "--no-ff", "origin/main")
    try:
        ids = hint_ids(repo2)
        assert "diverged" not in ids
        assert "behind" not in ids
    finally:
        git(repo2, "merge", "--abort")
    assert "diverged" not in ids_during_am(repo2)


# `no-upstream-branch`
# --------------------
# <fragment id="cc-t7V1Ualy4j" following="3"></fragment>
def test_no_upstream_branch(tmp_path_factory: pytest.TempPathFactory) -> None:
    first, second = make_temps(tmp_path_factory, 2)
    make_repo(first, [["git", "init", "-b", "main"]])
    config_user("user1", "user1@example.com")
    commit_file(first, "foo.txt", "xxx", "Add foo.")
    git(first, "switch", "-c", "feature-test")
    make_repo(second, [["git", "init", "--bare", "-b", "main"]])
    git(first, "remote", "add", "origin", str(second))
    upstream = [
        "rev-parse",
        "--abbrev-ref",
        "--symbolic-full-name",
        "@{upstream}",
    ]
    assert git(first, *upstream, check=False).returncode != 0

    assert "no-upstream-branch" in hint_ids(first)
    _, found = all_blocks(first)
    assert "git push -u origin feature-test" in commands(
        found["no-upstream-branch"]
    )

    git(first, "push", "-u", "origin", "feature-test")
    assert git(first, *upstream).stdout.strip() == "origin/feature-test"
    assert "no-upstream-branch" not in hint_ids(first)

    # The upstream stays configured after the remote branch is deleted.
    git(first, "push", "origin", "--delete", "feature-test")
    assert "[origin/feature-test: gone]" in git(first, "branch", "-vv").stdout
    assert git(first, *upstream, check=False).returncode != 0
    assert "no-upstream-branch" not in hint_ids(first)

    git(first, "switch", "-c", "+plus")
    _, found = all_blocks(first)
    assert "git push -u origin refs/heads/+plus" in commands(
        found["no-upstream-branch"]
    )


# `unpushed-branches`
# -------------------
# <fragment id="cc-LJhA9bcV9b" following="1"></fragment>
def test_unpushed_branches(tmp_path_factory: pytest.TempPathFactory) -> None:
    remote, local, single = make_temps(tmp_path_factory, 3)
    config_user("user1", "user1@example.com")
    make_repo(remote, [["git", "init", "--bare", "-b", "main"]])
    git(local.parent, "clone", str(remote), str(local))
    commit_file(local, "foo.txt", "base\n", "Add foo.")
    git(local, "push", "-u", "origin", "main")

    assert "unpushed-branches" not in hint_ids(local)
    git(local, "branch", "topic")
    assert "unpushed-branches" not in hint_ids(local)

    git(local, "switch", "-c", "feature")
    commit_file(local, "bar.txt", "feature\n", "Add feature file.")
    git(local, "switch", "main")
    assert "unpushed-branches" in hint_ids(local)
    _, found = all_blocks(local)
    block = collapse(found["unpushed-branches"])
    assert "As of last fetch:" in block
    assert "feature (no upstream)" in block
    assert "main (" not in block and "topic (" not in block
    assert commands(found["unpushed-branches"]) == [
        "git push -u origin feature"
    ]
    assert "https://git-scm.com/docs/git-push#UPSTREAM-BRANCHES" in block

    git(local, "switch", "feature")
    assert "unpushed-branches" not in hint_ids(local)
    assert "no-upstream-branch" in hint_ids(local)
    git(local, "switch", "main")

    git(local, "push", "-u", "origin", "feature")
    assert "unpushed-branches" not in hint_ids(local)
    git(local, "switch", "feature")
    commit_file(local, "next.txt", "next\n", "Add another feature file.")
    git(local, "switch", "main")
    assert "[origin/feature: ahead 1]" in git(local, "branch", "-vv").stdout
    _, found = all_blocks(local)
    block = collapse(found["unpushed-branches"])
    assert "feature (ahead of origin/feature by 1 commit)" in block
    assert commands(found["unpushed-branches"]) == ["git push origin feature"]

    git(local, "switch", "--detach", "feature")
    _, found = all_blocks(local)
    assert "feature (ahead of origin/feature by 1 commit)" in collapse(
        found["unpushed-branches"]
    )
    git(local, "switch", "main")

    git(local, "branch", "--track", "loc", "main")
    git(local, "switch", "loc")
    commit_file(local, "local.txt", "local\n", "Add local-upstream file.")
    git(local, "switch", "main")
    _, found = all_blocks(local)
    assert "loc (" not in collapse(found["unpushed-branches"])

    git(local, "switch", "-c", "side", "main")
    commit_file(local, "side.txt", "side\n", "Add side.")
    git(local, "push", "origin", "side")
    commit_file(local, "side2.txt", "side\n", "Add another side file.")
    git(local, "switch", "main")
    _, found = all_blocks(local)
    assert "side (no upstream)" in collapse(found["unpushed-branches"])
    assert "git push -u origin side" in commands(found["unpushed-branches"])
    git(local, "branch", "-f", "side", "main")
    git(local, "switch", "side")
    commit_file(local, "side3.txt", "side\n", "Add a diverging side file.")
    git(local, "switch", "main")
    _, found = all_blocks(local)
    assert "side (" not in collapse(found["unpushed-branches"])

    for number in range(1, 7):
        branch = f"b{number}"
        git(local, "switch", "-c", branch, "main")
        commit_file(local, f"{branch}.txt", branch, f"Add {branch}.")
    git(local, "switch", "main")
    _, found = all_blocks(local)
    block = collapse(found["unpushed-branches"])
    for number in range(1, 6):
        assert f"b{number} (no upstream)" in block
    assert "b6 (" not in block and "feature (" not in block
    assert "and 2 more" in block

    git(local, "push", "-u", "origin", "b1")
    git(local, "push", "origin", "--delete", "b1")
    assert "[origin/b1: gone]" in git(local, "branch", "-vv").stdout
    git(local, "push", "-u", "origin", "b2")
    git(local, "switch", "b2")
    git(local, "commit", "--amend", "-m", "Change b2.")
    git(local, "switch", "main")
    assert (
        "[origin/b2: ahead 1, behind 1]" in git(local, "branch", "-vv").stdout
    )
    _, found = all_blocks(local)
    block = collapse(found["unpushed-branches"])
    assert "b1 (" not in block and "b2 (" not in block

    append(local / "foo.txt", "main\n")()
    git(local, "commit", "-am", "Change foo on main.")
    git(local, "switch", "-c", "clash", "HEAD^")
    write(local / "foo.txt", "clash\n")()
    git(local, "commit", "-am", "Change foo on clash.")
    git(local, "switch", "main")
    assert git(local, "merge", "clash", check=False).returncode != 0
    try:
        assert "unpushed-branches" not in hint_ids(local)
    finally:
        git(local, "merge", "--abort")

    git(single.parent, "clone", "--single-branch", str(remote), str(single))
    git(single, "switch", "-c", "nf")
    commit_file(single, "nf.txt", "nf\n", "Add nf.")
    git(single, "push", "-u", "origin", "nf")
    assert "no-upstream-branch" not in hint_ids(single)
    git(single, "switch", "main")
    assert (
        git(
            single,
            "for-each-ref",
            "--format=%(upstream)",
            "refs/heads/nf",
        ).stdout
        == "\n"
    )
    assert "unpushed-branches" not in hint_ids(single)

    git(local, "switch", "clash")
    assert git(local, "rebase", "main", check=False).returncode != 0
    try:
        assert "unpushed-branches" not in hint_ids(local)
    finally:
        git(local, "rebase", "--abort")
        git(local, "switch", "main")

    git(local, "switch", "-c", "+plus", "main")
    commit_file(local, "plus.txt", "plus\n", "Add plus.")
    git(local, "switch", "main")
    _, found = all_blocks(local)
    assert "+plus (no upstream)" in collapse(found["unpushed-branches"])
    assert "git push -u origin refs/heads/+plus" in commands(
        found["unpushed-branches"]
    )
    git(local, "push", "-u", "origin", "refs/heads/+plus")
    _, found = all_blocks(local)
    assert "+plus (" not in collapse(found["unpushed-branches"])
    git(local, "switch", "+plus")
    commit_file(local, "plus2.txt", "plus\n", "Add another plus file.")
    git(local, "switch", "main")
    _, found = all_blocks(local)
    assert "git push origin refs/heads/+plus" in commands(
        found["unpushed-branches"]
    )

    git(local, "remote", "remove", "origin")
    assert "unpushed-branches" not in hint_ids(local)


# `--fetch`
# ---------
def test_fetch_failure(tmp_path_factory: pytest.TempPathFactory) -> None:
    repo1, repo2 = behind_setup(tmp_path_factory)
    git(repo2, "fetch")
    git(repo2, "remote", "set-url", "origin", str(repo1.parent / "missing"))
    result = run_hints(repo2, "--all", "--fetch")
    assert result.returncode == 0, result.stderr
    lines = result.stdout.splitlines()
    assert lines[:2] == ["Branch: main", FETCH_FAILED]
    block = result.stdout.split("ID: behind", 1)[1]
    assert "As of last fetch: " in block
    # `--ids-only` prints only IDs.
    result = run_hints(repo2, "--all", "--ids-only", "--fetch")
    assert result.returncode == 0
    assert "behind" in result.stdout.splitlines()
    assert FETCH_FAILED not in result.stdout


def test_fetch_without_remote(tmp_path_factory: pytest.TempPathFactory) -> None:
    (repo,) = make_temps(tmp_path_factory, 1)
    make_repo(repo, [["git", "init", "-b", "main"]])
    config_user("user1", "user1@example.com")
    commit_file(repo, "foo.txt", "xxx", "Add foo.")
    result = run_hints(repo, "--all", "--fetch")
    assert result.returncode == 0, result.stderr
    assert FETCH_FAILED not in result.stdout
    assert result.stdout.splitlines()[0] == "Branch: main"
