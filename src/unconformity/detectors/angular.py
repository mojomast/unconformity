"""Force-push detector."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from git import Repo

from ..models import Severity, UnconformityEvent, UnconformityType


def detect_angular(repo: Repo) -> List[UnconformityEvent]:
    events: List[UnconformityEvent] = []
    head_ref = repo.active_branch.name if not repo.head.is_detached else "HEAD"
    reflog_lines = []
    try:
        reflog_lines = repo.git.reflog(head_ref).splitlines()
    except Exception:
        reflog_lines = []
    shas = []
    for line in reflog_lines:
        parts = line.split()
        if parts:
            shas.append(parts[0])
    if len(set(shas)) > 1:
        events.append(
            UnconformityEvent(
                type=UnconformityType.ANGULAR,
                severity=Severity.HIGH
                if head_ref != "main" and head_ref != "master"
                else Severity.CRITICAL,
                description="Reflog history shows overwritten commits consistent with a force-push.",
                affected_commits=shas[-2:],
                detected_at=datetime.now(timezone.utc),
                forensic_details={"ref": head_ref, "reflog_entries": len(reflog_lines)},
                geological_metaphor="Tilted strata were cut away and replaced by a newer flat layer.",
            )
        )
    return events
