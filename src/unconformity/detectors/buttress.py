"""Rebase detector."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from git import Repo

from ..models import Severity, UnconformityEvent, UnconformityType


def detect_buttress(repo: Repo) -> List[UnconformityEvent]:
    events: List[UnconformityEvent] = []
    for commit in repo.iter_commits(all=True):
        if commit.authored_date != commit.committed_date:
            events.append(
                UnconformityEvent(
                    type=UnconformityType.BUTTRESS,
                    severity=Severity.LOW
                    if abs(commit.authored_date - commit.committed_date) < 86400
                    else Severity.MEDIUM,
                    description="Author date differs from committer date, often seen in rebases.",
                    affected_commits=[commit.hexsha],
                    detected_at=datetime.now(timezone.utc),
                    forensic_details={
                        "author_date": commit.authored_datetime,
                        "committer_date": commit.committed_date,
                        "message": commit.message.strip(),
                    },
                    geological_metaphor="Older layers are truncated and fresh strata are deposited against them.",
                )
            )
    return events
