"""CLI entry point."""

from __future__ import annotations

import json
import sys

import click
from rich.console import Console
from rich.table import Table

from .reporter import render_report, write_report
from .scanner import scan_repository
from .timeline import render_timeline
from .watcher import watch_repository


console = Console()


@click.group()
def cli() -> None:
    """Unconformity CLI."""


@cli.command()
@click.argument("repo_path")
@click.option("--types", "types_", "-t", multiple=True)
@click.option("--severity", "-s")
@click.option("--since", "-S")
@click.option("--until", "-U")
@click.option("--branch", "-b")
@click.option("--json", "as_json", is_flag=True)
@click.option("--verbose", "-v", is_flag=True)
def scan(
    repo_path: str,
    types_: tuple[str, ...],
    severity: str | None,
    since: str | None,
    until: str | None,
    branch: str | None,
    as_json: bool,
    verbose: bool,
) -> None:
    result = scan_repository(
        repo_path,
        types=types_,
        min_severity=severity,
        since=since,
        until=until,
        branch=branch,
    )
    if as_json:
        click.echo(render_report(result, fmt="json"))
        return
    table = Table(title="Unconformities")
    table.add_column("Type")
    table.add_column("Severity")
    table.add_column("Description")
    table.add_column("Affected Commits")
    table.add_column("Detected At")
    for item in result.unconformities:
        table.add_row(
            item.type.value,
            item.severity.value,
            item.description,
            ", ".join(item.affected_commits),
            item.detected_at.isoformat(),
        )
        if verbose:
            console.print(f"[bold]{item.type.value}[/bold] {item.forensic_details}")
    console.print(table)


@cli.command()
@click.argument("repo_path")
@click.option("--output", "-o")
@click.option("--format", "fmt", "-f", default="text")
@click.option("--threshold", "-t")
def report(repo_path: str, output: str | None, fmt: str, threshold: str | None) -> None:
    result = scan_repository(repo_path)
    content = render_report(result, fmt=fmt, threshold=threshold)
    write_report(output, content)


@cli.command()
@click.argument("repo_path")
@click.option("--width", "-w", type=int)
@click.option("--branch", "-b")
@click.option("--color", "-c", default="auto")
def timeline(repo_path: str, width: int | None, branch: str | None, color: str) -> None:
    result = scan_repository(repo_path, branch=branch)
    click.echo(render_timeline(result, width=width or 80))


@cli.command()
@click.argument("repo_path")
@click.option("--interval", "-i", type=float, default=30.0)
@click.option("--webhook", "-w")
def watch(repo_path: str, interval: float, webhook: str | None) -> None:
    for event in watch_repository(
        repo_path, interval=interval, webhook=webhook, iterations=1
    ):
        click.echo(json.dumps(event, indent=2))


if __name__ == "__main__":
    cli()
