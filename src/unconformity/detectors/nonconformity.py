"""Deleted branch detector."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from git import Repo

from ..git_forensics import (
    collect_unreachable_chain,
    fsck_unreachable_commits,
    unreachable_commit_tips,
)
from ..models import Severity, UnconformityEvent, UnconformityType


def detect_nonconformity(repo: Repo) -> List[UnconformityEvent]:
    events: List[UnconformityEvent] = []
    unreachable = fsck_unreachable_commits(repo)
    for sha in unreachable_commit_tips(repo, unreachable):
        chain = collect_unreachable_chain(repo, sha, unreachable)
        if not chain:
            continue
        severity = Severity.HIGH if len(chain) > 5 else Severity.MEDIUM
        events.append(
            UnconformityEvent(
                type=UnconformityType.NONCONFORMITY,
                severity=severity,
                description="Unreachable commits suggest a deleted branch or orphaned work.",
                affected_commits=chain,
                detected_at=datetime.now(timezone.utc),
                forensic_details={
                    "tip": sha,
                    "unreachable_commit_count": len(chain),
                    "fsck_unreachable": unreachable,
                },
                geological_metaphor="An intrusion was eroded away, leaving only the gap it occupied.",
            )
        )
    return events
