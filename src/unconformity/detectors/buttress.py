"""Rebase detector.

Detects buttress unconformities — commits where history was rewritten via
rebase.  The primary signal is a significant difference between author_date
and committer_date, which git sets during rebase (the author date is
preserved from the original commit, but the committer date becomes the
rebase timestamp).

Secondary signals include reflog entries with "rebase" in the message,
and commits reachable from reflog entries that are no longer reachable
from any branch.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from git import Repo

from ..git_forensics import default_branch_name, iter_reflog_events
from ..models import Severity, UnconformityEvent, UnconformityType


def detect_buttress(repo: Repo) -> List[UnconformityEvent]:
    events: List[UnconformityEvent] = []
    branch = default_branch_name(repo)
    if not branch:
        return events

    seen_shas: set[str] = set()

    # Strategy 1: Check for author_date ≠ committer_date on single-parent commits
    # A large delta is a strong rebase signal. Scan ALL branches, not just default.
    for head in repo.heads:
        for commit in repo.iter_commits(head.name):
            if len(commit.parents) != 1:
                continue
            if commit.hexsha in seen_shas:
                continue

            delta = abs(commit.committed_date - commit.authored_date)
            # Normal commits have delta ~0; rebases typically have delta > 1 hour
            # We use 3600s as the threshold
            if delta < 3600:
                continue

            seen_shas.add(commit.hexsha)
            events.append(
                UnconformityEvent(
                    type=UnconformityType.BUTTRESS,
                    severity=Severity.LOW if delta < 86400 else Severity.MEDIUM,
                    description=(
                        f"Commit has {delta/3600:.1f}h gap between author and committer dates, "
                        f"suggesting rebased history."
                    ),
                    affected_commits=[commit.hexsha],
                    detected_at=datetime.now(timezone.utc),
                    forensic_details={
                        "author_date": str(commit.authored_datetime),
                        "committer_date": str(commit.committed_datetime),
                        "delta_seconds": delta,
                        "parent": commit.parents[0].hexsha,
                        "message": commit.message.strip(),
                    },
                    geological_metaphor="Older layers were truncated and fresh strata were deposited against the cut face.",
                )
            )

    # Strategy 2: Check reflog for rebase entries
    # These directly indicate rebase operations
    rebase_refs: dict[str, str] = {}  # old_sha -> message
    for evt in iter_reflog_events(repo):
        if "rebase" in evt.message.lower():
            if evt.oldhexsha and evt.oldhexsha != "0" * 40:
                rebase_refs[evt.oldhexsha] = evt.message

    # Check if pre-rebase SHAs are now unreachable (confirming the rebase)
    for old_sha in rebase_refs:
        try:
            # If the commit is reachable, no unconformity from this angle
            repo.commit(old_sha)
        except Exception:
            continue
        # Check if it's reachable from any branch
        reachable = False
        for head in repo.heads:
            try:
                repo.git.merge_base("--is-ancestor", old_sha, head.commit.hexsha)
                reachable = True
                break
            except Exception:
                continue
        if not reachable and old_sha not in seen_shas:
            seen_shas.add(old_sha)
            events.append(
                UnconformityEvent(
                    type=UnconformityType.BUTTRESS,
                    severity=Severity.MEDIUM,
                    description=f"Reflog shows rebase: {rebase_refs[old_sha][:80]}",
                    affected_commits=[old_sha],
                    detected_at=datetime.now(timezone.utc),
                    forensic_details={
                        "reflog_message": rebase_refs[old_sha],
                        "sha": old_sha,
                    },
                    geological_metaphor="Older layers were truncated and fresh strata were deposited against the cut face.",
                )
            )

    return events
