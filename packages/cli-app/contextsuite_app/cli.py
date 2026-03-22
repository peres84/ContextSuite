"""ContextSuite CLI — main entry point."""

from __future__ import annotations

import os

import click
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory

from contextsuite_app.renderer import (
    console,
    print_banner,
    print_result,
    print_success,
)
from contextsuite_app.session import Session, init_project


@click.group(invoke_without_command=True)
@click.pass_context
@click.option("--assistant", "-a", default="codex", help="Coding assistant (codex, claude, cursor)")
@click.option("--repo", "-r", default=None, help="Repository name (e.g. acme/payments)")
@click.option("--agent-url", default="http://127.0.0.1:8000", help="Context Agent URL")
@click.option("--project", "-p", default=".", help="Project directory")
def cli(ctx, assistant, repo, agent_url, project):
    """ContextSuite — context, governance, and memory for AI coding workflows."""
    ctx.ensure_object(dict)
    ctx.obj["assistant"] = assistant
    ctx.obj["repo"] = repo
    ctx.obj["agent_url"] = agent_url
    ctx.obj["project"] = os.path.abspath(project)

    if ctx.invoked_subcommand is None:
        # Default to chat mode
        ctx.invoke(chat)


@cli.command()
@click.option("--repo", "-r", default=None, help="Repository name")
@click.option("--assistant", "-a", default="codex", help="Default coding assistant")
@click.pass_context
def init(ctx, repo, assistant):
    """Initialize a project directory for ContextSuite."""
    project_dir = ctx.obj.get("project", ".")

    if not repo:
        repo = click.prompt("Repository name (e.g. acme/payments)", default="")
        if not repo:
            repo = None

    config_path = init_project(project_dir, repo, assistant)
    print_success(f"Initialized ContextSuite in {config_path}")
    console.print(f"  Repository: {repo or '(not set)'}")
    console.print(f"  Assistant:  {assistant}")
    console.print()
    console.print("  Start a session with: [bold cyan]contextsuite chat[/bold cyan]")


@cli.command()
@click.argument("prompt", nargs=-1, required=False)
@click.pass_context
def chat(ctx, prompt):
    """Start an interactive session or run a one-shot prompt."""
    project_dir = ctx.obj.get("project", ".")
    assistant = ctx.obj.get("assistant", "codex")
    repo = ctx.obj.get("repo")
    agent_url = ctx.obj.get("agent_url", "http://127.0.0.1:8000")

    session = Session(
        project_dir=project_dir,
        assistant=assistant,
        agent_url=agent_url,
        repository=repo,
    )

    # One-shot mode: prompt provided as arguments
    if prompt:
        prompt_text = " ".join(prompt)
        result = session.send_prompt(prompt_text)
        if result:
            print_result(result)
        return

    # Interactive mode
    print_banner()
    console.print(f"  Project:   [bold]{session.project_dir}[/bold]")
    console.print(f"  Assistant: [bold]{session.assistant}[/bold]")
    if session.repository:
        console.print(f"  Repository: [bold]{session.repository}[/bold]")
    console.print()
    console.print("  Type your prompt, use @file.py to reference files,")
    console.print("  #image:path.png for images, or /help for commands.")
    console.print()

    # Set up prompt with history
    history_dir = os.path.join(project_dir, ".contextsuite")
    os.makedirs(history_dir, exist_ok=True)
    history_file = os.path.join(history_dir, "history.txt")

    prompt_session: PromptSession = PromptSession(
        history=FileHistory(history_file),
    )

    while True:
        try:
            user_input = prompt_session.prompt(
                f"[{session.assistant}] > ",
            )
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Goodbye![/dim]")
            break

        user_input = user_input.strip()
        if not user_input:
            continue

        # Handle /commands
        if user_input.startswith("/"):
            should_continue = session.handle_command(user_input)
            if not should_continue:
                console.print("[dim]Goodbye![/dim]")
                break
            continue

        # Send prompt
        result = session.send_prompt(user_input)
        if result:
            print_result(result)


@cli.command()
@click.pass_context
def status(ctx):
    """Show current project configuration."""
    project_dir = ctx.obj.get("project", ".")
    session = Session(project_dir=project_dir)

    console.print(f"  Project:    {session.project_dir}")
    console.print(f"  Repository: {session.repository or '(not set)'}")
    console.print(f"  Assistant:  {session.assistant}")
    console.print(f"  Agent URL:  {session.agent_url}")


def main():
    """Entry point for the CLI."""
    cli(obj={})


if __name__ == "__main__":
    main()
