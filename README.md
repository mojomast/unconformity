# Unconformity

**Git forensics for what's MISSING.**

Every git tool shows what EXISTS. Unconformity shows what's MISSING — the gaps, deletions, overwrites, and absences in git history, classified using geological unconformity metaphors.

## Unconformity Types

| Type | Git Event | Geological Metaphor |
|------|-----------|-------------------|
| **Angular Unconformity** | Force-pushes | Tilted older layers overlain by flat newer ones |
| **Disconformity** | Squash merges | Parallel layers with missing intermediary |
| **Nonconformity** | Deleted branches | Igneous intrusion that eroded away |
| **Paraconformity** | Time gaps | Apparent continuity but missing time |
| **Buttress Unconformity** | Rebases | Younger layers against older truncated ones |

## Installation

```bash
pip install -e .
```

## Usage

```bash
# Scan a repository for unconformities
unconformity scan /path/to/repo

# Generate a detailed report
unconformity report /path/to/repo

# Visualize geological layers
unconformity timeline /path/to/repo

# Monitor for new unconformities
unconformity watch /path/to/repo
```

## Options

### scan
- `-t, --types` — Filter by unconformity types
- `-s, --severity` — Minimum severity threshold (low, medium, high, critical)
- `-S, --since` — Only scan commits since this date
- `-U, --until` — Only scan commits until this date
- `-b, --branch` — Only scan specific branch
- `--json` — Output as JSON
- `-v, --verbose` — Show detailed forensic information

### report
- `-o, --output` — Output file path
- `-f, --format` — Report format (text, markdown, html, json)
- `-t, --threshold` — Minimum severity to include

### timeline
- `-w, --width` — Timeline width in characters
- `-b, --branch` — Branch to visualize
- `-c, --color` — Color mode (auto, always, never)

### watch
- `-i, --interval` — Polling interval in seconds (default: 30)
- `-w, --webhook` — Webhook URL to POST new unconformities to

## Development

```bash
pip install -e ".[dev]"
pytest
```

## License

MIT
