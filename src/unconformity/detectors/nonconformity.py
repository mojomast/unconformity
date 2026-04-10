"""Deleted branch detector."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from git import Repo

from ..models import Severity, UnconformityEvent, UnconformityType


def detect_nonconformity(repo: Repo) -> List[UnconformityEvent]:
    events: List[UnconformityEvent] = []
    unreachable = []
    try:
        out = repo.git.fsck("--unreachable", "--no-reflogs")
        unreachable = [
            line for line in out.splitlines() if "unreachable commit" in line
        ]
    except Exception:
        unreachable = []
    for line in unreachable:
        sha = line.split()[-1]
        events.append(
            UnconformityEvent(
                type=UnconformityType.NONCONFORMITY,
                severity=Severity.MEDIUM,
                description="Unreachable commit suggests a deleted branch or orphaned work.",
                affected_commits=[sha],
                detected_at=datetime.now(timezone.utc),
                forensic_details={"fsck_line": line},
                geological_metaphor="An intrusion was eroded away, leaving an exposed gap.",
            )
        )
    return events
