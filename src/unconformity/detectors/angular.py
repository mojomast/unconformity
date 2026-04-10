"""Force-push detector."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from git import Repo

from ..git_forensics import default_branch_name, iter_reflog_events, is_ancestor
from ..models import Severity, UnconformityEvent, UnconformityType


def detect_angular(repo: Repo) -> List[UnconformityEvent]:
    events: List[UnconformityEvent] = []
    branch = default_branch_name(repo)
    branch_refs = [repo.head.reference] if not repo.head.is_detached else []
    branch_refs.extend(repo.heads)
    for event in iter_reflog_events(repo):
        if branch and not event.refname.endswith(f"/{branch}"):
            continue
        if not event.oldhexsha or not event.newhexsha:
            continue
        if event.oldhexsha == event.newhexsha:
            continue
        if is_ancestor(repo, event.oldhexsha, event.newhexsha):
            continue
        severity = (
            Severity.CRITICAL
            if branch in {"main", "master", "trunk"}
            else Severity.HIGH
        )
        events.append(
            UnconformityEvent(
                type=UnconformityType.ANGULAR,
                severity=severity,
                description="Reflog shows a non-fast-forward ref update consistent with rewritten history.",
                affected_commits=[event.oldhexsha, event.newhexsha],
                detected_at=datetime.now(timezone.utc),
                forensic_details={
                    "ref": event.refname,
                    "oldhexsha": event.oldhexsha,
                    "newhexsha": event.newhexsha,
                    "reflog_message": event.message,
                    "fast_forward": False,
                },
                geological_metaphor="Older tilted strata were eroded away and replaced by a flatter sequence.",
            )
        )
    return events
