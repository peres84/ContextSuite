"""Rich terminal output for the ContextSuite CLI."""

from __future__ import annotations

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

console = Console()


def print_banner():
    """Print the ContextSuite banner."""
    console.print()
    console.print(
        Panel(
            "[bold cyan]ContextSuite[/bold cyan]\n"
            "[dim]Context, governance, and memory layer for AI coding workflows[/dim]",
            border_style="cyan",
            padding=(1, 2),
        )
    )
    console.print()


def print_step(name: str, message: str, style: str = "blue"):
    """Print a pipeline step."""
    console.print(f"  [{style}][{name}][/{style}] {message}")


def print_success(message: str):
    console.print(f"  [green][ok][/green] {message}")


def print_error(message: str):
    console.print(f"  [red][error][/red] {message}")


def print_warning(message: str):
    console.print(f"  [yellow][warn][/yellow] {message}")


def print_result(result: dict):
    """Print the full workflow result."""
    console.print()

    # Risk
    risk = result.get("risk", {})
    risk_level = risk.get("level", "unknown")
    risk_color = {"low": "green", "medium": "yellow", "high": "red"}.get(risk_level, "white")
    print_step("risk", f"[{risk_color}]{risk_level}[/{risk_color}]")
    if risk.get("signals"):
        for s in risk["signals"]:
            console.print(f"           [dim]- {s}[/dim]")

    # Approval
    approval = result.get("approval", {})
    if approval.get("approved"):
        print_step("approve", f"[green]Approved[/green] ({approval.get('reviewer', '')})")
    else:
        print_step("approve", f"[red]Rejected[/red] — {approval.get('reason', '')}")

    # Plan
    plan = result.get("plan")
    if plan:
        console.print()
        console.print(Panel(Markdown(plan), title="Plan", border_style="cyan", padding=(1, 2)))

    # Execution result
    execution = result.get("execution")
    if execution:
        console.print()
        state = execution.get("state", "unknown")
        state_color = "green" if state == "completed" else "red"
        duration = execution.get("duration_seconds")
        dur_str = f" in {duration:.1f}s" if duration else ""

        console.print(
            Panel(
                f"[{state_color}]{state}[/{state_color}]{dur_str}\n\n"
                f"{execution.get('summary', '')}",
                title="Execution",
                border_style=state_color,
                padding=(1, 2),
            )
        )

        output = execution.get("output")
        if output and output.strip():
            console.print()
            console.print(Panel(output[:3000], title="Output", border_style="dim", padding=(0, 1)))

    # Status
    status = result.get("status", "unknown")
    if status in ("completed", "ready"):
        print_success(f"Run {result.get('run_id', '')[:8]}... completed")
    elif approval.get("approved") is False:
        print_warning(f"Run {result.get('run_id', '')[:8]}... rejected")
    else:
        print_error(f"Run {result.get('run_id', '')[:8]}... {status}")

    console.print()


def print_context_summary(summary: str, max_lines: int = 15):
    """Print a truncated context summary."""
    lines = summary.split("\n")
    if len(lines) > max_lines:
        truncated = "\n".join(lines[:max_lines]) + f"\n... ({len(lines) - max_lines} more)"
    else:
        truncated = summary
    console.print(Panel(truncated, title="Retrieved Context", border_style="dim", padding=(0, 1)))


def print_attachments(attachments: list):
    """Print attached files/images."""
    if not attachments:
        return
    for att in attachments:
        kind = "image" if att.is_image else "file"
        console.print(f"  [dim][{kind}][/dim] {att.name}")


def print_help():
    """Print help for the interactive session."""
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style="cyan")
    table.add_column()
    table.add_row("@file.py", "Attach a file to the prompt")
    table.add_row("#image:path.png", "Attach an image to the prompt")
    table.add_row("/image path.png", "Attach an image (alternative)")
    table.add_row("/assistant codex", "Switch coding assistant (codex, claude, cursor)")
    table.add_row("/context", "Show last retrieved context")
    table.add_row("/status", "Show session info")
    table.add_row("/help", "Show this help")
    table.add_row("/quit", "Exit")
    console.print()
    console.print(Panel(table, title="Commands", border_style="cyan"))
    console.print()
