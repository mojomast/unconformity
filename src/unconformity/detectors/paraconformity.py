"""Time-gap detector."""

from __future__ import annotations

from datetime import datetime, timezone
from statistics import mean, pstdev
from typing import List

from git import Repo

from ..git_forensics import business_gap_seconds, default_branch_name
from ..models import Severity, UnconformityEvent, UnconformityType


def detect_paraconformity(
    repo: Repo, gap_threshold_seconds: int = 60 * 60 * 24 * 14
) -> List[UnconformityEvent]:
    events: List[UnconformityEvent] = []
    branch = default_branch_name(repo)
    commits = (
        list(repo.iter_commits(branch or "--all", max_count=200))
        if branch
        else list(repo.iter_commits(all=True, max_count=200))
    )
    if len(commits) < 2:
        return events
    deltas = []
    ordered = list(reversed(commits))
    for older, newer in zip(ordered[:-1], ordered[1:]):
        delta = business_gap_seconds(older.committed_datetime, newer.committed_datetime)
        deltas.append((older, newer, delta))
    values = [delta for _, _, delta in deltas]
    avg = mean(values)
    spread = pstdev(values) if len(values) > 1 else 0
    for older, newer, delta in deltas:
        if delta >= gap_threshold_seconds or (spread and delta > avg + 2 * spread):
            events.append(
                UnconformityEvent(
                    type=UnconformityType.PARACONFORMITY,
                    severity=Severity.LOW
                    if delta < gap_threshold_seconds * 2
                    else Severity.MEDIUM,
                    description="Large time gap between consecutive commits suggests a temporal break.",
                    affected_commits=[older.hexsha, newer.hexsha],
                    detected_at=datetime.now(timezone.utc),
                    forensic_details={
                        "gap_seconds": delta,
                        "mean_gap": avg,
                        "stddev_gap": spread,
                        "previous_commit_date": older.committed_datetime,
                        "next_commit_date": newer.committed_datetime,
                    },
                    geological_metaphor="Sediment appears continuous, but a temporal break exists between layers.",
                )
            )
    return events
