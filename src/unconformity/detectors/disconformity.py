"""Squash merge detector.

Detects disconformities — single-parent commits that compressed multiple
logical changes into one.  The classic signal is a ``git merge --squash``
which produces a commit with only one parent even though the changes
originated on a separate branch.

Detection strategy
------------------
1. Find unreachable commit tips (from ``git fsck``).
2. For each unreachable tip, build the full unreachable chain.
3. Check if the squash commit's tree matches the unreachable tip's tree
   (strongest signal: ``git merge --squash`` preserves the tree).
4. As a secondary signal, flag single-parent commits whose diff is
   significantly larger than the branch average.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from git import Repo

from ..git_forensics import (
    collect_unreachable_chain,
    default_branch_name,
    fsck_unreachable_commits,
    unreachable_commit_tips,
)
from ..models import Severity, UnconformityEvent, UnconformityType


def _diff_stats(repo: Repo, parent_sha: str, commit_sha: str) -> int:
    """Return number of files changed in a diff."""
    try:
        output = repo.git.diff(
            parent_sha, commit_sha, "--numstat", "--no-ext-diff"
        )
        return len([l for l in output.splitlines() if l.strip()])
    except Exception:
        return 0


def detect_disconformity(repo: Repo) -> List[UnconformityEvent]:
    events: List[UnconformityEvent] = []
    branch = default_branch_name(repo)
    if not branch:
        return events

    # Gather unreachable commits for cross-referencing
    unreachable_shas = fsck_unreachable_commits(repo)
    if not unreachable_shas:
        return events

    unreachable_tips = unreachable_commit_tips(repo, unreachable_shas)
    tip_chains: dict[str, List[str]] = {}
    for tip in unreachable_tips:
        chain = collect_unreachable_chain(repo, tip, unreachable_shas)
        tip_chains[tip] = chain

    # Build a set of unreachable commit trees for fast lookup
    unreachable_trees: dict[str, str] = {}  # tree_hexsha -> tip_sha
    for tip, chain in tip_chains.items():
        try:
            tip_commit = repo.commit(tip)
            unreachable_trees[tip_commit.tree.hexsha] = tip
        except Exception:
            pass

    # Check each single-parent commit on the main branch
    for commit in repo.iter_commits(branch, first_parent=True):
        if len(commit.parents) != 1:
            continue
        parent = commit.parents[0]

        # Signal 1: Tree match — the squash commit has the same tree as
        # an unreachable tip.  This is the strongest possible signal.
        matched_chain: List[str] = []
        if commit.tree.hexsha in unreachable_trees:
            tip = unreachable_trees[commit.tree.hexsha]
            matched_chain = tip_chains.get(tip, [])

        # Signal 2: The squash commit's diff is significantly larger
        # than what a typical single commit would produce
        files_changed = _diff_stats(repo, parent.hexsha, commit.hexsha)

        if not matched_chain and files_changed < 4:
            continue

        severity = Severity.MEDIUM
        description = (
            f"Single-parent commit with {files_changed} files changed."
        )
        if matched_chain:
            description += (
                f" Unreachable chain of {len(matched_chain)} commits "
                f"shares the same tree — likely a squash merge."
            )
            if len(matched_chain) > 5:
                severity = Severity.HIGH

        events.append(
            UnconformityEvent(
                type=UnconformityType.DISCONFORMITY,
                severity=severity,
                description=description,
                affected_commits=[*matched_chain[-3:], commit.hexsha],
                detected_at=datetime.now(timezone.utc),
                forensic_details={
                    "message": commit.message.strip(),
                    "files_changed": files_changed,
                    "hidden_commit_count": len(matched_chain),
                    "parent": parent.hexsha,
                },
                geological_metaphor="Parallel strata were compressed into one preserved seam.",
            )
        )
    return events
