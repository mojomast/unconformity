"""Git repository fixtures for detector tests."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

import pytest
from git import Actor, Repo


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


def _commit(
    repo: Repo,
    path: Path,
    name: str,
    message: str,
    when: datetime,
    committed_when: datetime | None = None,
) -> str:
    path.write_text(f"{message}\n", encoding="utf-8")
    repo.index.add([str(path.relative_to(repo.working_tree_dir))])
    author = Actor(name, f"{name.lower()}@example.com")
    return repo.index.commit(
        message,
        author=author,
        committer=author,
        author_date=when,
        commit_date=committed_when or when,
    ).hexsha


@pytest.fixture()
def git_repo(tmp_path: Path) -> Repo:
    repo = Repo.init(tmp_path)
    base = datetime(2024, 1, 1, tzinfo=timezone.utc)
    _commit(repo, tmp_path / "file.txt", "Alice", "initial commit", base)
    return repo


@pytest.fixture()
def force_push_repo(tmp_path: Path) -> Repo:
    repo = Repo.init(tmp_path)
    base = datetime(2024, 1, 1, tzinfo=timezone.utc)
    first = _commit(repo, tmp_path / "force.txt", "Alice", "before rewrite", base)
    repo.git.reset("--hard", first)
    _commit(
        repo,
        tmp_path / "force.txt",
        "Alice",
        "after rewrite",
        base + timedelta(hours=1),
    )
    return repo


@pytest.fixture()
def squash_repo(tmp_path: Path) -> Repo:
    repo = Repo.init(tmp_path)
    base = datetime(2024, 1, 1, tzinfo=timezone.utc)
    _commit(repo, tmp_path / "a.txt", "Alice", "feature work squash", base)
    _commit(repo, tmp_path / "b.txt", "Bob", "regular commit", base + timedelta(days=1))
    return repo


@pytest.fixture()
def deleted_branch_repo(tmp_path: Path) -> Repo:
    repo = Repo.init(tmp_path)
    base = datetime(2024, 1, 1, tzinfo=timezone.utc)
    base_branch = repo.active_branch.name
    _commit(repo, tmp_path / "main.txt", "Alice", "main", base)
    branch = repo.create_head("feature")
    branch.checkout()
    _commit(
        repo, tmp_path / "feature.txt", "Bob", "orphaned work", base + timedelta(days=1)
    )
    repo.heads[base_branch].checkout()
    repo.delete_head(branch, force=True)
    return repo


@pytest.fixture()
def time_gap_repo(tmp_path: Path) -> Repo:
    repo = Repo.init(tmp_path)
    base = datetime(2024, 1, 1, tzinfo=timezone.utc)
    _commit(repo, tmp_path / "gap.txt", "Alice", "first", base)
    _commit(repo, tmp_path / "gap.txt", "Alice", "second", base + timedelta(days=30))
    return repo


@pytest.fixture()
def rebase_repo(tmp_path: Path) -> Repo:
    repo = Repo.init(tmp_path)
    base = datetime(2024, 1, 1, tzinfo=timezone.utc)
    _commit(repo, tmp_path / "rebase.txt", "Alice", "rebased content", base)
    _commit(
        repo,
        tmp_path / "rebase.txt",
        "Alice",
        "rebased content updated",
        base,
        base + timedelta(days=1),
    )
    return repo
