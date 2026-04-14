# disconformitussy — Git Forensics for What's Missing

> Part of the **[ussyverse](https://github.com/mojomast)** ecosystem.

## Vision

Every git tool shows what EXISTS. `disconformitussy` shows what's MISSING — the gaps, deletions, overwrites, and absences in git history. It maps geological unconformity types to git events, providing a unique forensic perspective on repository health.

## Core Concept

In geology, an **unconformity** is a missing layer in the rock record — evidence that something was erased, compressed, or never deposited. The same patterns exist in git repositories. `disconformitussy` detects and classifies these missing layers.

## Unconformity Type Mappings

### 1. Angular Unconformity — Force-pushes
**Geology**: Tilted older rock layers overlain by flat younger layers, indicating erosion and tilting between deposition periods.
**Git**: Force-pushes that overwrite history. The old commit chain is "tilted" (divergent), and the new chain is "flat" (replacing it). Detected via reflog entries showing missing SHAs and dangling objects.

**Detection**:
- Scan ALL refs in reflog (not just default branch)
- Check for non-fast-forward ref updates (old SHA is not an ancestor of new SHA)
- Severity: CRITICAL on main/master/trunk, HIGH on all other branches

### 2. Disconformity — Squash Merges
**Geology**: Parallel rock layers with a missing intermediary layer, indicating a gap in deposition.
**Git**: Squash merges that compress parallel work (multiple commits on a branch) into a single commit on the target branch. The intermediary commits are "eroded away" — they exist in the repo but not in the main history chain.

**Detection**:
- Primary signal: single-parent commit whose tree SHA matches an unreachable commit tip (tree match = definitive squash proof)
- Secondary signal (opt-in): single-parent commit with unusually large diff (>15 files changed)
- Severity driven by hidden commit count: LOW <4, MEDIUM 4–10, HIGH >10

### 3. Nonconformity — Deleted Branches
**Geology**: Igneous intrusion that was eroded away, leaving only the surrounding sedimentary rock.
**Git**: Deleted branches that never merged. The branch existed (leaving dangling commits) but was removed without merging — the work simply vanished.

**Detection**:
- Find dangling commit trees not reachable from any ref (via `git fsck --unreachable`)
- Cross-reference reflog to recover the deleted branch name
- Attach earliest/latest commit timestamps to forensic details
- Severity: LOW <4 commits, MEDIUM 4–10, HIGH >10

### 4. Paraconformity — Time Gaps
**Geology**: Apparent continuity between rock layers but missing time — the layers look conformable but represent a significant time gap.
**Git**: Time gaps between commits. The commit chain looks continuous but has significant temporal gaps.

**Detection**:
- Compute business-time gap (excludes weekends) between consecutive commits
- Flag if gap >= threshold (default: 14 days) OR statistical outlier (>2σ above mean)
- Configurable: `max_commits`, `gap_threshold_seconds`, `zscore_threshold`
- Severity: LOW < 28 days, MEDIUM >= 28 days

### 5. Buttress Unconformity — Rebases
**Geology**: Younger rock layers deposited against older truncated layers, where the older layers were cut off.
**Git**: Rebases that rewrite history. The original commits are "truncated" (their SHAs change), and new commits are deposited against the new base.

**Detection**:
- Primary signal: reflog entries with "rebase" in the message where pre-rebase SHA is now unreachable
- Secondary signal: commits with author_date ↔ committer_date delta > 6h
- Severity: MEDIUM for reflog-confirmed, LOW for date-delta-only

## Technical Stack

- **Language**: Python 3.9+
- **CLI Framework**: Click (with rich-click integration)
- **Git Integration**: GitPython
- **Terminal Output**: Rich (tables, trees, progress bars, panels)
- **Color Palette**: Geological — sediment browns (#8B4513, #D2691E), igneous reds (#DC143C, #FF4500), metamorphic blues (#4169E1, #6A5ACD), time whites (#F5F5DC, #FFFAF0)
- **Packaging**: pip-installable with pyproject.toml
- **Testing**: pytest with fixtures for test git repositories

## Project Structure

```
disconformitussy/
├── SPEC.md
├── README.md
├── pyproject.toml
├── src/
│   └── unconformity/
│       ├── __init__.py
│       ├── cli.py              # Click CLI entry point (command: disconformitussy)
│       ├── scanner.py          # Core scanning engine
│       ├── detectors/
│       │   ├── __init__.py     # detect_all() convenience function
│       │   ├── angular.py      # Force-push detection
│       │   ├── disconformity.py # Squash merge detection
│       │   ├── nonconformity.py # Deleted branch detection
│       │   ├── paraconformity.py # Time gap detection
│       │   └── buttress.py     # Rebase detection
│       ├── models.py           # Data models (UnconformityEvent, Severity, etc.)
│       ├── reporter.py         # Report generation
│       ├── timeline.py         # Timeline visualization
│       ├── watcher.py          # Real-time monitoring
│       └── palette.py          # Geological color palette
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Shared fixtures (test repos)
│   ├── test_angular.py
│   ├── test_disconformity.py
│   ├── test_nonconformity.py
│   ├── test_paraconformity.py
│   ├── test_buttress.py
│   ├── test_scanner.py
│   ├── test_reporter.py
│   └── test_timeline.py
└── .gitignore
```

## CLI Commands

### `disconformitussy scan <repo-path>`
Scan a git repository and classify all unconformities.

Options: `--types`, `--severity`, `--since`, `--until`, `--branch`, `--json`, `--verbose`

Output: Rich table with columns: Type, Severity, Description, Affected Commits, Detected At

### `disconformitussy report <repo-path>`
Generate a detailed report with severity scores and analysis.

Options: `--output`, `--format` (text/markdown/html/json), `--threshold`

### `disconformitussy timeline <repo-path>`
Visualize the geological layers of git history in the terminal.

Options: `--width`, `--branch`, `--color`

### `disconformitussy watch <repo-path>`
Monitor a repository for new unconformities in real-time.

Options: `--interval`, `--webhook`

## Data Models

```python
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

class UnconformityType(Enum):
    ANGULAR = "angular"           # Force-push
    DISCONFORMITY = "disconformity"  # Squash merge
    NONCONFORMITY = "nonconformity"  # Deleted branch
    PARACONFORMITY = "paraconformity" # Time gap
    BUTTRESS = "buttress"         # Rebase

class Severity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class UnconformityEvent:
    type: UnconformityType
    severity: Severity
    description: str
    affected_commits: List[str]
    detected_at: datetime
    forensic_details: dict
    geological_metaphor: str

@dataclass
class ScanResult:
    repo_path: str
    unconformities: List[UnconformityEvent]
    scan_time: datetime
    duration_seconds: float
    total_commits_scanned: int
```

## Severity Scoring

- **Critical**: Force-pushes to main/master/trunk
- **High**: Force-pushes to other branches; deleted branches with >10 commits
- **Medium**: Squash merges (>3 hidden commits); rebases (reflog-confirmed); deleted branches 4–10 commits
- **Low**: Time gaps; small rebases (date-delta only); small orphaned chains (<4 commits)

## Ussyverse Integration

`disconformitussy` is designed to plug into the ussyverse agent ecosystem:

- **Webhook output** from `watch` can pipe into ussybot or any Discord/Slack channel
- **JSON output** from `scan --json` is consumable by openclawssy agents for automated repo auditing
- **Report generation** can be triggered by CI/CD pipelines on push events

## Implementation Notes

1. **GitPython Usage**: Use `git.Repo` for all git operations. Access reflog via `ref.log()`, dangling objects via `repo.git.fsck()`, commit history via `repo.iter_commits()`.
2. **Performance**: Use generators and lazy evaluation for large repos. `paraconformity` and `buttress` detectors accept `max_commits` to bound scan time.
3. **Error Handling**: Gracefully handle non-git directories, bare repos, shallow clones, and repos with no history.
4. **`detect_all()`**: The `detectors/__init__.py` exports a `detect_all(repo)` function that runs all detectors, swallows individual exceptions, and returns severity-sorted results.
5. **Test Fixtures**: Create temporary git repos in `conftest.py` simulating each unconformity type.

## Success Criteria

1. `pip install -e .` installs the `disconformitussy` command
2. `disconformitussy scan <any-git-repo>` detects and classifies unconformities
3. `disconformitussy report <any-git-repo>` generates a formatted report
4. `disconformitussy timeline <any-git-repo>` shows a visual timeline
5. All detector modules have corresponding tests
6. Output uses the geological color palette consistently
