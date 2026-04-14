# 🪨 disconformitussy

> **Git forensics for what's MISSING — ussyverse edition.**

[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status: Alpha](https://img.shields.io/badge/status-alpha-orange.svg)]()
[![ussyverse](https://img.shields.io/badge/ussyverse-%F0%9F%AA%A8-purple)](https://github.com/mojomast)

Part of the **[ussyverse](https://github.com/mojomast)** — the mojomast ecosystem of unhinged, useful software.

Every git tool shows what **exists**. `disconformitussy` shows what's **missing** — the gaps, deletions, overwrites, and erasures hiding in your repository's history.

Named after the geological phenomenon where missing rock layers reveal lost time, `disconformitussy` maps five classes of git history anomalies to their geological equivalents — giving you a forensic vocabulary for what your repo _isn't_ telling you.

---

## Why This Exists

Force-pushes erase history. Squash merges bury individual commits. Rebases silently rewrite SHA chains. Deleted branches vanish with all their work. Time gaps hint at abandoned efforts or context switches that never came back.

Standard git tools show you the surface. `disconformitussy` digs for the strata underneath.

---

## Unconformity Types

| Type | Geological Meaning | Git Event | Severity |
|------|-------------------|-----------|----------|
| 🔴 **Angular** | Tilted older layers overwritten by flat newer ones | Force-push | High / Critical |
| 🟠 **Disconformity** | Parallel layers with a missing intermediary | Squash merge | Medium |
| 🟤 **Nonconformity** | Igneous intrusion eroded away, leaving no trace | Deleted branch (unmerged) | Variable |
| ⚪ **Paraconformity** | Apparent continuity hiding a missing time span | Commit time gap | Low / Medium |
| 🔵 **Buttress** | Younger layers deposited against truncated older ones | Rebase | Medium |

---

## Quick Start

```bash
git clone https://github.com/mojomast/unconformity
cd unconformity
pip install -e .

# Scan a repo for all missing history events
disconformitussy scan /path/to/repo

# Generate a full forensic report (markdown, html, json, text)
disconformitussy report /path/to/repo --format markdown

# Visualize history as geological layers in your terminal
disconformitussy timeline /path/to/repo

# Watch a repo live and alert on new anomalies
disconformitussy watch /path/to/repo --webhook https://hooks.example.com/alert
```

---

## Sample Output

```
┌──────────────────────────────────────────────────────────────────────┐
│  disconformitussy scan — /home/user/myproject                        │
├────────────────────┬──────────┬──────────────────────────────────────┤
│  Type              │ Severity │ Description                          │
├────────────────────┼──────────┼──────────────────────────────────────┤
│  🔴 Angular        │ CRITICAL │ Force-push to main (3 SHAs lost)     │
│  🟠 Disconformity  │ MEDIUM   │ Squash merge on PR #47 (6 commits)   │
│  🔵 Buttress       │ MEDIUM   │ Rebase detected on feature/auth      │
│  ⚪ Paraconformity │ LOW      │ 18d 4h gap between commits           │
└────────────────────┴──────────┴──────────────────────────────────────┘

Risk Score: 61 / 100
```

---

## Commands

### `scan`
```
disconformitussy scan <repo-path> [OPTIONS]
```
| Flag | Description |
|------|-------------|
| `-t, --types` | Filter by type: `angular`, `disconformity`, `nonconformity`, `paraconformity`, `buttress` |
| `-s, --severity` | Minimum threshold: `low`, `medium`, `high`, `critical` |
| `-S, --since` | Only scan commits after this date |
| `-U, --until` | Only scan commits before this date |
| `-b, --branch` | Scope to a specific branch |
| `--json` | Output as JSON (pipeable) |
| `-v, --verbose` | Full forensic detail per finding |

### `report`
```
disconformitussy report <repo-path> [OPTIONS]
```
Generates a full report with executive summary, per-finding details, risk score (0–100), and recommendations.

| Flag | Description |
|------|-------------|
| `-o, --output` | Output file path (default: stdout) |
| `-f, --format` | `text`, `markdown`, `html`, `json` |
| `-t, --threshold` | Minimum severity to include |

### `timeline`
```
disconformitussy timeline <repo-path> [OPTIONS]
```
Renders a color-coded geological layer view of your commit history in the terminal. Unconformity events appear as gaps, intrusions, and truncations.

| Flag | Description |
|------|-------------|
| `-w, --width` | Timeline width in characters |
| `-b, --branch` | Branch to visualize |
| `-c, --color` | `auto`, `always`, `never` |

### `watch`
```
disconformitussy watch <repo-path> [OPTIONS]
```
Polls the repo on an interval and fires alerts when new unconformities are detected. Webhook support for Slack, Discord, or any HTTP endpoint.

| Flag | Description |
|------|-------------|
| `-i, --interval` | Poll interval in seconds (default: 30) |
| `-w, --webhook` | Webhook URL to POST events to |

---

## Architecture

```
src/unconformity/
├── cli.py              # Click CLI entry point
├── scanner.py          # Orchestrates all detectors
├── git_forensics.py    # Low-level git ops (reflog, fsck, dangling objects)
├── models.py           # UnconformityEvent, ScanResult, Severity enums
├── reporter.py         # Report generation (text/md/html/json)
├── timeline.py         # Terminal timeline visualization
├── watcher.py          # Real-time polling monitor
├── palette.py          # Geological color palette (Rich colors)
└── detectors/
    ├── angular.py        # Force-push detection
    ├── disconformity.py  # Squash merge detection
    ├── nonconformity.py  # Deleted branch detection
    ├── paraconformity.py # Time gap detection
    └── buttress.py       # Rebase detection
```

**Stack:** Python 3.9+ · [Click](https://click.palletsprojects.com/) · [GitPython](https://gitpython.readthedocs.io/) · [Rich](https://rich.readthedocs.io/)

---

## Use Cases

- **Incident response** — Something broke on main after a force-push; trace exactly what was overwritten
- **Code audit** — Verify a repo hasn't had history scrubbed before accepting a handoff
- **Team health** — Detect rebase-heavy workflows erasing collaborative commit context
- **Compliance** — Demonstrate history integrity for regulated codebases
- **OSS due diligence** — Before depending on a project, check if history has been manipulated
- **Ussyverse integration** — Wire into your agent pipelines to auto-audit repos on push

---

## Ussyverse

`disconformitussy` is part of the [ussyverse](https://github.com/mojomast) — a collection of open-source tools built by [@mojomast](https://github.com/mojomast). Check out the rest of the ecosystem:

- **[devussy](https://github.com/mojomast/devussy)** — AI dev orchestration
- **[ragussy](https://github.com/mojomast/ragussy)** — Local RAG + LLM inference stack
- **[openclawssy](https://github.com/mojomast/openclawssy)** — Agent collaboration on GitHub

---

## Development

```bash
git clone https://github.com/mojomast/unconformity
cd unconformity
pip install -e ".[dev]"
pytest
```

Tests use real temporary git repositories that simulate each unconformity type — no mocking.

---

## Roadmap

- [ ] GitHub Actions integration (scan on push / PR)
- [ ] `disconformitussy diff <before-sha> <after-sha>` for targeted comparison
- [ ] HTML report with interactive timeline
- [ ] GitLab / Gitea support
- [ ] PyPI release as `disconformitussy`
- [ ] Ussyverse dashboard integration

---

## License

MIT — dig freely.
