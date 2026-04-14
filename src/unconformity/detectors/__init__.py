"""Detector collection.

Provides individual detectors and a convenience ``detect_all`` function
that runs every detector against a repo and returns a combined list.
"""

from __future__ import annotations

from typing import List

from git import Repo

from ..models import UnconformityEvent
from .angular import detect_angular
from .buttress import detect_buttress
from .disconformity import detect_disconformity
from .nonconformity import detect_nonconformity
from .paraconformity import detect_paraconformity


def detect_all(repo: Repo) -> List[UnconformityEvent]:
    """Run all detectors and return a combined, severity-sorted list."""
    findings: List[UnconformityEvent] = []
    for fn in (
        detect_angular,
        detect_disconformity,
        detect_nonconformity,
        detect_buttress,
        detect_paraconformity,
    ):
        try:
            findings.extend(fn(repo))
        except Exception:
            pass  # Never let one detector crash the whole scan

    _severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    findings.sort(key=lambda e: _severity_order.get(e.severity.value, 99))
    return findings


__all__ = [
    "detect_all",
    "detect_angular",
    "detect_buttress",
    "detect_disconformity",
    "detect_nonconformity",
    "detect_paraconformity",
]
