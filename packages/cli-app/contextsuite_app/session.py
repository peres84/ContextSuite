"""Interactive session manager — handles the chat loop and API calls."""

from __future__ import annotations

import json
import os
from pathlib import Path

import httpx

from contextsuite_app.attachments import (
    Attachment,
    format_prompt_with_attachments,
    parse_references,
    read_file_attachment,
)
from contextsuite_app.renderer import (
    console,
    print_attachments,
    print_error,
    print_help,
    print_step,
    print_warning,
)

CONFIG_FILE = ".contextsuite.json"


class Session:
    """Manages state for an interactive ContextSuite session."""

    def __init__(
        self,
        project_dir: str,
        assistant: str = "codex",
        agent_url: str = "http://127.0.0.1:8000",
        repository: str | None = None,
    ):
        self.project_dir = os.path.abspath(project_dir)
        self.assistant = assistant
        self.agent_url = agent_url
        self.repository = repository
        self.last_context: str | None = None
        self.last_result: dict | None = None
        self.pending_images: list[Attachment] = []

        # Load project config if exists
        config_path = Path(self.project_dir) / CONFIG_FILE
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
            self.repository = config.get("repository", self.repository)
            self.assistant = config.get("assistant", self.assistant)
            self.agent_url = config.get("agent_url", self.agent_url)

    def handle_command(self, line: str) -> bool:
        """Handle a /command. Returns True if the session should continue."""
        parts = line.strip().split(maxsplit=1)
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        if cmd in ("/quit", "/exit", "/q"):
            return False

        elif cmd == "/help":
            print_help()

        elif cmd == "/assistant":
            if arg in ("codex", "claude", "cursor"):
                self.assistant = arg
                print_step("config", f"Switched to [bold]{arg}[/bold]")
            else:
                print_warning("Usage: /assistant codex|claude|cursor")

        elif cmd == "/image":
            if not arg:
                print_warning("Usage: /image path/to/image.png")
            else:
                att = read_file_attachment(arg, self.project_dir)
                if att and att.is_image:
                    self.pending_images.append(att)
                    print_step("image", f"Attached {att.name}")
                elif att:
                    print_warning(f"{arg} is not an image file")
                else:
                    print_error(f"File not found: {arg}")

        elif cmd == "/context":
            if self.last_context:
                console.print(self.last_context)
            else:
                print_warning("No context retrieved yet")

        elif cmd == "/status":
            console.print(f"  Project:   {self.project_dir}")
            console.print(f"  Repository: {self.repository or '(not set)'}")
            console.print(f"  Assistant:  {self.assistant}")
            console.print(f"  Agent URL:  {self.agent_url}")
            if self.pending_images:
                console.print(f"  Images:     {len(self.pending_images)} pending")

        else:
            print_warning(f"Unknown command: {cmd}. Type /help for available commands.")

        return True

    def send_prompt(self, raw_input: str) -> dict | None:
        """Parse input, build request, and send to the Context Agent."""
        # Parse @file and #image references
        prompt, attachments = parse_references(raw_input, self.project_dir)

        # Add any pending images from /image command
        attachments.extend(self.pending_images)
        self.pending_images = []

        if not prompt.strip():
            print_warning("Empty prompt. Type your prompt or /help for commands.")
            return None

        # Show attachments
        if attachments:
            print_attachments(attachments)

        # Build full prompt with file contents
        full_prompt = format_prompt_with_attachments(prompt, attachments)

        # Build image data for the request
        images = [
            {"name": a.name, "data": a.content, "mime_type": a.mime_type}
            for a in attachments
            if a.is_image
        ]

        print_step("send", f"Sending to Context Agent ({self.assistant})...")

        try:
            response = httpx.post(
                f"{self.agent_url}/tasks/send",
                json={
                    "prompt": full_prompt,
                    "repository": self.repository,
                    "assistant": self.assistant,
                    "images": images if images else None,
                },
                timeout=360.0,
            )
            response.raise_for_status()
            result = response.json()

            self.last_result = result
            self.last_context = result.get("context_summary")

            return result

        except httpx.ConnectError:
            print_error(
                f"Cannot connect to Context Agent at {self.agent_url}\n"
                "  Start it with: uv run context-agent"
            )
            return None

        except httpx.HTTPStatusError as e:
            print_error(f"Context Agent error: {e.response.status_code}")
            try:
                detail = e.response.json()
                console.print(f"  [dim]{detail}[/dim]")
            except Exception:
                pass
            return None

        except Exception as e:
            print_error(f"Request failed: {e}")
            return None


def init_project(project_dir: str, repository: str | None, assistant: str):
    """Initialize a project directory for ContextSuite."""
    config = {
        "repository": repository,
        "assistant": assistant,
        "agent_url": "http://127.0.0.1:8000",
        "workspace": project_dir,
    }

    config_path = Path(project_dir) / CONFIG_FILE
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    return config_path
