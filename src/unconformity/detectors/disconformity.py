"""Squash merge detector."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from git import Repo

from ..models import Severity, UnconformityEvent, UnconformityType


def detect_disconformity(repo: Repo) -> List[UnconformityEvent]:
    events: List[UnconformityEvent] = []
    for commit in repo.iter_commits(all=True):
        message = commit.message.lower()
        if "squash" in message or "squashed" in message:
            events.append(
                UnconformityEvent(
                    type=UnconformityType.DISCONFORMITY,
                    severity=Severity.MEDIUM,
                    description="Commit message suggests a squash merge that compressed multiple changes.",
                    affected_commits=[commit.hexsha],
                    detected_at=datetime.now(timezone.utc),
                    forensic_details={
                        "message": commit.message.strip(),
                        "author": commit.author.name,
                    },
                    geological_metaphor="Parallel layers are compressed into a single preserved seam.",
                )
            )
    return events
