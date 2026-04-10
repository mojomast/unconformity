# Unconformity — Git Forensics for What's Missing

## Vision

Every git tool shows what EXISTS. Unconformity shows what's MISSING — the gaps, deletions, overwrites, and absences in git history. It maps geological unconformity types to git events, providing a unique forensic perspective on repository health.

## Core Concept

In geology, an **unconformity** is a missing layer in the rock record — evidence that something was erased, compressed, or never deposited. The same patterns exist in git repositories. Unconformity detects and classifies these missing layers.

## Unconformity Type Mappings

### 1. Angular Unconformity — Force-pushes
**Geology**: Tilted older rock layers overlain by flat younger layers, indicating erosion and tilting between deposition periods.
**Git**: Force-pushes that overwrite history. The old commit chain is "tilted" (divergent), and the new chain is "flat" (replacing it). Detected via reflog entries showing missing SHAs and dangling objects.

**Detection**:
- Check reflog for entries where a ref now points to a different SHA than its previous entry
- Find dangling commits (objects not reachable from any current ref)
- Compare reflog chains for sudden SHA changes in the same ref
- Severity: High (history is literally being overwritten)

### 2. Disconformity — Squash Merges
**Geology**: Parallel rock layers with a missing intermediary layer, indicating a gap in deposition.
**Git**: Squash merges that compress parallel work (multiple commits on a branch) into a single commit on the target branch. The intermediary commits are "eroded away" — they exist in the repo but not in the main history chain.

**Detection**:
- Find merge commits (or their aftermath) where the resulting commit has only one parent but was created via `--squash`
- Detect commits that combine changes from multiple authors (co-authored-by trailers or file-level blame analysis)
- Find dangling commit trees where commits share a common base with a branch tip but aren't reachable from any ref
- Severity: Medium (information is preserved but hidden)

### 3. Nonconformity — Deleted Branches
**Geology**: Igneous intrusion that was eroded away, leaving only the surrounding sedimentary rock.
**Git**: Deleted branches that never merged. The branch existed (leaving dangling commits) but was removed without merging — the work simply vanished.

**Detection**:
- Find dangling commit trees not reachable from any ref (branches, tags)
- Use `git fsck --unreachable` to identify orphaned commits
- Cross-reference with reflog to find deleted branch tips
- Severity: Variable (could be intentional cleanup or lost work)

### 4. Paraconformity — Time Gaps
**Geology**: Apparent continuity between rock layers but missing time — the layers look conformable but represent a significant time gap.
**Git**: Time gaps between commits. The commit chain looks continuous but has significant temporal gaps (weekends don't count, but multi-week gaps do).

**Detection**:
- Compute commit timestamp deltas between consecutive commits on each branch
- Flag statistical outliers (gaps > 2 standard deviations from mean, or > configurable threshold)
- Account for business hours (configurable: skip weekends, set working hours)
- Severity: Low-Medium (may indicate stalled work, context switching, or abandoned efforts)

### 5. Buttress Unconformity — Rebases
**Geology**: Younger rock layers deposited against older truncated layers, where the older layers were cut off.
**Git**: Rebases that rewrite history. The original commits are "truncated" (their SHAs change), and new commits are deposited against the new base.

**Detection**:
- Detect commit chains with same author/message patterns but different SHAs
- Find commits in reflog that share patch content but not SHA
- Identify commits where the parent chain differs from what timestamps suggest
- Look for author date ≠ committer date patterns (common in rebases)
- Severity: Medium (history is rewritten but work is preserved)

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
Unconformity/
├── SPEC.md
├── README.md
├── pyproject.toml
├── src/
│   └── unconformity/
│       ├── __init__.py
│       ├── cli.py              # Click CLI entry point
│       ├── scanner.py          # Core scanning engine
│       ├── detectors/
│       │   ├── __init__.py
│       │   ├── angular.py      # Force-push detection
│       │   ├── disconformity.py # Squash merge detection
│       │   ├── nonconformity.py # Deleted branch detection
│       │   ├── paraconformity.py # Time gap detection
│       │   └── buttress.py     # Rebase detection
│       ├── models.py           # Data models (Unconformity, Severity, etc.)
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

### `unconformity scan <repo-path>`
Scan a git repository and classify all unconformities.

Options:
- `--types / -t`: Filter by unconformity types (angular, disconformity, nonconformity, paraconformity, buttress)
- `--severity / -s`: Minimum severity threshold (low, medium, high, critical)
- `--since / -S`: Only scan commits since this date/time
- `--until / -U`: Only scan commits until this date/time
- `--branch / -b`: Only scan specific branch
- `--json`: Output as JSON for piping
- `--verbose / -v`: Show detailed forensic information

Output: Rich table with columns: Type, Severity, Description, Affected Commits, Detected At

### `unconformity report <repo-path>`
Generate a detailed report with severity scores and analysis.

Options:
- `--output / -o`: Output file path (default: stdout)
- `--format / -f`: Report format (text, markdown, html, json)
- `--threshold / -t`: Minimum severity to include

Output: Full report with:
- Executive summary (total unconformities by type, severity distribution)
- Detailed findings per unconformity
- Risk score (0-100) based on unconformity count and severity
- Recommendations

### `unconformity timeline <repo-path>`
Visualize the geological layers of git history.

Options:
- `--width / -w`: Timeline width in characters (default: terminal width)
- `--branch / -b`: Branch to visualize
- `--color / -c`: Color mode (auto, always, never)

Output: Vertical timeline with:
- Commits as geological layers (colored by type)
- Unconformities marked as gaps/intrusions
- Legend mapping colors to unconformity types

### `unconformity watch <repo-path>`
Monitor a repository for new unconformities in real-time.

Options:
- `--interval / -i`: Polling interval in seconds (default: 30)
- `--webhook / -w`: Webhook URL to POST new unconformities to

Output: Live updating display showing new unconformities as they're detected.

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
    affected_commits: List[str]    # List of SHAs
    detected_at: datetime
    forensic_details: dict         # Type-specific details
    geological_metaphor: str       # Human-readable geological explanation

@dataclass
class ScanResult:
    repo_path: str
    unconformities: List[UnconformityEvent]
    scan_time: datetime
    duration_seconds: float
    total_commits_scanned: int
```

## Severity Scoring

- **Critical**: Force-pushes to main/master branch
- **High**: Force-pushes to other branches; deleted branches with >5 commits
- **Medium**: Squash merges; rebases; deleted branches with 1-5 commits
- **Low**: Time gaps; small rebases

## Implementation Notes

1. **GitPython Usage**: Use `git.Repo` for all git operations. Access reflog via `repo.git.reflog()`, dangling objects via `repo.git.fsck()`, and commit history via `repo.iter_commits()`.

2. **Performance**: For large repos, use generators and lazy evaluation. Don't load all commits into memory at once. Consider caching.

3. **Error Handling**: Gracefully handle non-git directories, bare repos, shallow clones, and repos with no history.

4. **Test Fixtures**: Create temporary git repositories in conftest.py that simulate each unconformity type (force-push history, squash merges, deleted branches, etc.).

5. **Watch Command**: Use polling (not filesystem events) for simplicity. Compare reflog state between polls.

6. **Color Palette**: Define in palette.py as Rich Color objects. Sediment browns for normal history, igneous reds for destructive events, metamorphic blues for transformations, time whites for gaps.

## pyproject.toml Configuration

```toml
[build-system]
requires = ["setuptools>=64", "wheel"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "unconformity"
version = "0.1.0"
description = "Git forensics tool that analyzes what's MISSING from git history"
requires-python = ">=3.9"
dependencies = [
    "click>=8.0",
    "gitpython>=3.1",
    "rich>=13.0",
    "rich-click>=1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov",
]

[project.scripts]
unconformity = "unconformity.cli:cli"

[tool.setuptools.packages.find]
where = ["src"]
```

## Success Criteria

1. `pip install -e .` works and installs the `unconformity` command
2. `unconformity scan <any-git-repo>` detects and classifies unconformities
3. `unconformity report <any-git-repo>` generates a formatted report
4. `unconformity timeline <any-git-repo>` shows a visual timeline
5. All detector modules have corresponding tests
6. Test repos properly simulate each unconformity type
7. Output uses the geological color palette consistently
