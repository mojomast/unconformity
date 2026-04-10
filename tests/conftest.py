"""Git repository fixtures for detector tests."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

import pytest
from git import Actor, Repo


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


AUTHOR = Actor("Alice", "alice@example.com")
BOB = Actor("Bob", "bob@example.com")


def _write(repo: Repo, path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    repo.index.add([str(path.relative_to(repo.working_tree_dir))])


def _commit(
    repo: Repo,
    path: Path,
    content: str,
    message: str,
    when: datetime,
    author: Actor = AUTHOR,
    committer: Actor | None = None,
    commit_date: datetime | None = None,
) -> str:
    _write(repo, path, content)
    return repo.index.commit(
        message,
        author=author,
        committer=committer or author,
        author_date=when,
        commit_date=commit_date or when,
    ).hexsha


def _checkout_branch(repo: Repo, name: str) -> None:
    repo.heads[name].checkout()


@pytest.fixture()
def git_repo(tmp_path: Path) -> Repo:
    repo = Repo.init(tmp_path)
    base = datetime(2024, 1, 1, tzinfo=timezone.utc)
    _commit(repo, tmp_path / "file.txt", "initial\n", "initial commit", base)
    return repo


@pytest.fixture()
def force_push_repo(tmp_path: Path) -> Repo:
    repo = Repo.init(tmp_path)
    base = datetime(2024, 1, 1, tzinfo=timezone.utc)
    first = _commit(repo, tmp_path / "force.txt", "old\n", "before rewrite", base)
    repo.git.reset("--hard", first)
    _commit(
        repo,
        tmp_path / "force.txt",
        "rewritten\n",
        "after rewrite",
        base + timedelta(hours=1),
    )
    return repo


@pytest.fixture()
def squash_repo(tmp_path: Path) -> Repo:
    repo = Repo.init(tmp_path)
    base = datetime(2024, 1, 1, tzinfo=timezone.utc)
    _commit(repo, tmp_path / "main.txt", "base\n", "base", base)
    repo.create_head("feature").checkout()
    # Create multiple commits on the feature branch touching different files
    for i in range(5):
        _commit(
            repo,
            tmp_path / f"feature_{i}.txt",
            f"feature content {i}\n",
            f"feature step {i+1}",
            base + timedelta(hours=i+1),
            author=BOB,
        )
    _checkout_branch(repo, "master")
    repo.git.merge("--squash", "feature")
    repo.index.commit(
        "squash merge feature",
        author=AUTHOR,
        committer=AUTHOR,
        author_date=base + timedelta(hours=6),
        commit_date=base + timedelta(hours=6),
    )
    repo.delete_head("feature", force=True)
    return repo


@pytest.fixture()
def deleted_branch_repo(tmp_path: Path) -> Repo:
    repo = Repo.init(tmp_path)
    base = datetime(2024, 1, 1, tzinfo=timezone.utc)
    _commit(repo, tmp_path / "main.txt", "main\n", "main", base)
    repo.create_head("feature").checkout()
    _commit(
        repo,
        tmp_path / "feature.txt",
        "orphan 1\n",
        "orphaned work 1",
        base + timedelta(days=1),
        author=BOB,
    )
    _commit(
        repo,
        tmp_path / "feature.txt",
        "orphan 2\n",
        "orphaned work 2",
        base + timedelta(days=2),
        author=BOB,
    )
    repo.heads.master.checkout()
    repo.delete_head(repo.heads.feature, force=True)
    return repo


@pytest.fixture()
def time_gap_repo(tmp_path: Path) -> Repo:
    repo = Repo.init(tmp_path)
    base = datetime(2024, 1, 1, tzinfo=timezone.utc)
    _commit(repo, tmp_path / "gap.txt", "a\n", "first", base)
    _commit(repo, tmp_path / "gap.txt", "b\n", "second", base + timedelta(days=30))
    return repo


@pytest.fixture()
def rebase_repo(tmp_path: Path) -> Repo:
    repo = Repo.init(tmp_path)
    # Set local identity so rebase doesn't fail
    repo.config_writer().set_value("user", "name", "Test").release()
    repo.config_writer().set_value("user", "email", "test@test.com").release()
    base = datetime(2024, 1, 1, tzinfo=timezone.utc)
    _commit(repo, tmp_path / "base.txt", "root\n", "root", base)
    repo.create_head("feature").checkout()
    _commit(
        repo,
        tmp_path / "feature_work.txt",
        "feature work\n",
        "feature step",
        base + timedelta(days=1),
        author=BOB,
    )
    repo.heads.master.checkout()
    _commit(
        repo,
        tmp_path / "base.txt",
        "root updated\n",
        "mainline change",
        base + timedelta(days=2),
    )
    # Rebase feature onto master (no conflict - different files)
    repo.heads.feature.checkout()
    repo.git.rebase("master")
    return repo


@pytest.fixture()
def mixed_repo(
    force_push_repo: Repo,
    squash_repo: Repo,
    deleted_branch_repo: Repo,
    time_gap_repo: Repo,
    rebase_repo: Repo,
) -> Repo:
    return rebase_repo
