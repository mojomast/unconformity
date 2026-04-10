"""Time-gap detector."""

from __future__ import annotations

from datetime import datetime, timezone
from statistics import mean, pstdev
from typing import List

from git import Repo

from ..models import Severity, UnconformityEvent, UnconformityType


def detect_paraconformity(
    repo: Repo, gap_threshold_seconds: int = 60 * 60 * 24 * 14
) -> List[UnconformityEvent]:
    events: List[UnconformityEvent] = []
    commits = list(repo.iter_commits(max_count=200))
    if len(commits) < 2:
        return events
    deltas = []
    for older, newer in zip(commits[1:], commits[:-1]):
        delta = abs(
            (newer.committed_datetime - older.committed_datetime).total_seconds()
        )
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
                    description="Large time gap between consecutive commits.",
                    affected_commits=[older.hexsha, newer.hexsha],
                    detected_at=datetime.now(timezone.utc),
                    forensic_details={
                        "gap_seconds": delta,
                        "mean_gap": avg,
                        "stddev_gap": spread,
                    },
                    geological_metaphor="Sediment appears continuous, but a temporal break exists between layers.",
                )
            )
    return events
