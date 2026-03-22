"""Rich terminal output for the ContextSuite CLI."""

from __future__ import annotations

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

console = Console()
CONTEXT_AGENT_STYLE = "dark_orange3"
CODER_AGENT_STYLE = "bright_blue"


def _print_agent_label(name: str, subtitle: str, *, style: str):
    console.print()
    console.print(f"[bold {style}]{name}[/bold {style}] [dim]{subtitle}[/dim]")


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


def _render_saved_memory(saved_memory: dict):
    if not saved_memory:
        return

    if not saved_memory.get("saved"):
        print_step("memory", f"Skipped - {saved_memory.get('reason', '')}", style="dim")
        return

    issue_refs = saved_memory.get("issue_refs", [])
    constraint_refs = saved_memory.get("constraint_refs", [])
    lines = [saved_memory.get("reason", "Saved issue-related memory")]

    if issue_refs:
        lines.append("")
        lines.append("Issues:")
        lines.extend(f"- {ref.get('id', '')}: {ref.get('title', '')}" for ref in issue_refs[:5])

    if constraint_refs:
        lines.append("")
        lines.append("Constraints:")
        lines.extend(
            f"- {ref.get('id', '')}: {ref.get('title', '')}" for ref in constraint_refs[:5]
        )

    if saved_memory.get("document_ids"):
        lines.append("")
        lines.append(f"Stored records: {len(saved_memory['document_ids'])}")
        lines.append(f"Vector stored: {'yes' if saved_memory.get('vector_stored') else 'no'}")

    console.print()
    console.print(
        Panel(
            "\n".join(lines),
            title=f"Context Agent Memory - {saved_memory.get('title', 'Saved Memory')}",
            border_style=CONTEXT_AGENT_STYLE,
            padding=(1, 2),
        )
    )


def _render_agent_interaction(result: dict):
    assistant = result.get("assistant") or "coder"
    risk = result.get("risk", {})
    approval = result.get("approval", {})
    execution = result.get("execution") or {}
    task_id = (result.get("task_id") or "")[:8]
    task_label = task_id or "pending-id"

    risk_level = risk.get("level", "unknown")
    risk_color = {"low": "green", "medium": "yellow", "high": "red"}.get(risk_level, "white")

    lines = [
        "[bold dark_orange3]Context Agent[/bold dark_orange3] -> [bold]User[/bold]: "
        f"reviewed the prompt and classified it as [{risk_color}]{risk_level}[/{risk_color}]."
    ]

    approval_status = approval.get("status", "rejected")
    reviewer = approval.get("reviewer") or "policy"
    if approval_status == "approved":
        lines.append(
            "[bold dark_orange3]Context Agent[/bold dark_orange3] -> [bold]User[/bold]: "
            f"approved the run ({reviewer})."
        )
        lines.append(
            "[bold dark_orange3]Context Agent[/bold dark_orange3] -> "
            f"[bold bright_blue]Coder Agent ({assistant})[/bold bright_blue]: "
            f"dispatched task {task_label} for execution."
        )
    elif approval_status == "escalated":
        lines.append(
            "[bold dark_orange3]Context Agent[/bold dark_orange3] -> [bold]User[/bold]: "
            "requested human approval before dispatch."
        )
        if execution:
            lines.append(
                "[bold dark_orange3]Context Agent[/bold dark_orange3] -> "
                f"[bold bright_blue]Coder Agent ({assistant})[/bold bright_blue]: "
                f"dispatched task {task_label} after approval."
            )
    else:
        lines.append(
            "[bold dark_orange3]Context Agent[/bold dark_orange3] -> [bold]User[/bold]: "
            f"rejected the run ({approval.get('reason', 'policy blocked')})."
        )

    if execution:
        state = execution.get("state", "unknown")
        state_color = "green" if state == "completed" else "red"
        lines.append(
            f"[bold bright_blue]Coder Agent ({assistant})[/bold bright_blue] -> "
            "[bold dark_orange3]Context Agent[/bold dark_orange3]: "
            f"returned [{state_color}]{state}[/{state_color}] to the workflow."
        )
        if execution.get("summary"):
            lines.append(f"[dim]{execution['summary']}[/dim]")

    console.print()
    console.print(
        Panel(
            "\n".join(lines),
            title="Agent Interaction",
            border_style="yellow",
            padding=(1, 2),
        )
    )


def print_result(result: dict):
    """Print the full workflow result."""
    console.print()
    assistant = result.get("assistant") or "coder"

    _print_agent_label(
        "Context Agent",
        "retrieval, risk review, approval, and packaging",
        style=CONTEXT_AGENT_STYLE,
    )

    risk = result.get("risk", {})
    risk_level = risk.get("level", "unknown")
    risk_color = {"low": "green", "medium": "yellow", "high": "red"}.get(risk_level, "white")
    print_step("risk", f"[{risk_color}]{risk_level}[/{risk_color}]")
    if risk.get("signals"):
        for signal in risk["signals"]:
            console.print(f"           [dim]- {signal}[/dim]")

    approval = result.get("approval", {})
    approval_status = approval.get("status", "rejected")
    if approval_status == "approved":
        print_step("approve", f"[green]Approved[/green] ({approval.get('reviewer', '')})")
    elif approval_status == "escalated":
        print_step(
            "approve",
            f"[yellow]Human approval required[/yellow] - {approval.get('reason', '')}",
        )
    else:
        print_step("approve", f"[red]Rejected[/red] - {approval.get('reason', '')}")

    plan = result.get("plan")
    if plan:
        console.print()
        console.print(
            Panel(
                Markdown(plan),
                title="Context Agent Plan",
                border_style=CONTEXT_AGENT_STYLE,
                padding=(1, 2),
            )
        )

    _render_agent_interaction(result)

    execution = result.get("execution")
    if execution:
        _print_agent_label(
            f"Coder Agent ({assistant})",
            "execution result from the local coding assistant",
            style=CODER_AGENT_STYLE,
        )
        console.print()
        state = execution.get("state", "unknown")
        state_color = "green" if state == "completed" else "red"
        duration = execution.get("duration_seconds")
        dur_str = f" in {duration:.1f}s" if duration else ""

        console.print(
            Panel(
                f"[{state_color}]{state}[/{state_color}]{dur_str}\n\n"
                f"{execution.get('summary', '')}",
                title=f"Coder Agent Execution ({assistant})",
                border_style=CODER_AGENT_STYLE if state == "completed" else state_color,
                padding=(1, 2),
            )
        )

        output = execution.get("output")
        if output and output.strip():
            console.print()
            console.print(
                Panel(
                    output[:3000],
                    title=f"Coder Agent Output ({assistant})",
                    border_style=CODER_AGENT_STYLE,
                    padding=(0, 1),
                )
            )

    _render_saved_memory(result.get("saved_memory"))

    status = result.get("status", "unknown")
    if status in ("completed", "ready"):
        print_success(f"Run {result.get('run_id', '')[:8]}... completed")
    elif status == "pending_human_approval":
        print_warning(f"Run {result.get('run_id', '')[:8]}... waiting for human approval")
    elif approval_status == "rejected":
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
    console.print(
        Panel(
            truncated,
            title="Context Agent Context",
            border_style=CONTEXT_AGENT_STYLE,
            padding=(0, 1),
        )
    )


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
