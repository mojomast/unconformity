"""Timeline visualization."""

from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from .models import ScanResult


def render_timeline(result: ScanResult, width: int = 80) -> str:
    commits = max(1, result.total_commits_scanned)
    bars = ["■" for _ in range(min(width, commits))]
    lines = ["Timeline:", "".join(bars)]
    for item in result.unconformities:
        lines.append(f"{item.type.value}: {item.description}")
    lines.append("Legend: ■ history | gaps indicate unconformities")
    return "\n".join(lines)
