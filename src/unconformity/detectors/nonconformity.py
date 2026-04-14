"""Deleted-branch detector.

Detects nonconformities — unreachable commits suggesting a branch was
deleted without merging, leaving orphaned work.

Fix over v1:
- Tries to recover the original branch name from the reflog (makes
  forensic output much more useful).
- Attaches earliest/latest commit timestamps so analysts know *when*
  the work happened.
- Severity thresholds tuned: >10 commits = HIGH, 4-10 = MEDIUM, <4 = LOW.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from git import Repo

from ..git_forensics import (
    collect_unreachable_chain,
    fsck_unreachable_commits,
    iter_reflog_events,
    unreachable_commit_tips,
)
from ..models import Severity, UnconformityEvent, UnconformityType


def _branch_name_from_reflog(repo: Repo, tip_sha: str) -> Optional[str]:
    """Try to recover the deleted branch name from the reflog."""
    for event in iter_reflog_events(repo):
        if event.newhexsha == tip_sha or event.oldhexsha == tip_sha:
            # refname looks like refs/heads/feature-xyz
            parts = event.refname.split("/")
            if len(parts) >= 3 and parts[1] == "heads":
                return "/".join(parts[2:])
    return None


def _chain_timestamps(
    repo: Repo, chain: List[str]
) -> tuple[Optional[datetime], Optional[datetime]]:
    """Return (earliest, latest) authored datetimes across a commit chain."""
    dates: List[datetime] = []
    for sha in chain:
        try:
            dates.append(repo.commit(sha).authored_datetime)
        except Exception:
            pass
    if not dates:
        return None, None
    return min(dates), max(dates)


def detect_nonconformity(repo: Repo) -> List[UnconformityEvent]:
    """Detect orphaned commits from deleted branches."""
    events: List[UnconformityEvent] = []
    unreachable = fsck_unreachable_commits(repo)

    for tip_sha in unreachable_commit_tips(repo, unreachable):
        chain = collect_unreachable_chain(repo, tip_sha, unreachable)
        if not chain:
            continue

        n = len(chain)
        if n > 10:
            severity = Severity.HIGH
        elif n > 3:
            severity = Severity.MEDIUM
        else:
            severity = Severity.LOW

        branch_name = _branch_name_from_reflog(repo, tip_sha)
        earliest, latest = _chain_timestamps(repo, chain)

        branch_hint = f" (was branch: '{branch_name}')" if branch_name else ""
        events.append(
            UnconformityEvent(
                type=UnconformityType.NONCONFORMITY,
                severity=severity,
                description=(
                    f"{n} unreachable commit(s) suggest a deleted, unmerged branch{branch_hint}."
                ),
                affected_commits=chain,
                detected_at=datetime.now(timezone.utc),
                forensic_details={
                    "tip": tip_sha,
                    "unreachable_commit_count": n,
                    "recovered_branch_name": branch_name,
                    "earliest_commit": str(earliest) if earliest else None,
                    "latest_commit": str(latest) if latest else None,
                },
                geological_metaphor=(
                    "An igneous intrusion was eroded away — "
                    "only the cavity it once occupied remains in the rock record."
                ),
            )
        )
    return events
