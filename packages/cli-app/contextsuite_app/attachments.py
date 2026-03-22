"""Handle file and image attachments from the terminal."""

from __future__ import annotations

import base64
import mimetypes
import os
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Attachment:
    """A file or image attached to a prompt."""

    path: str
    content: str  # text content or base64 for images
    mime_type: str = "text/plain"
    is_image: bool = False
    name: str = ""

    def __post_init__(self):
        if not self.name:
            self.name = os.path.basename(self.path)


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg"}


def is_image_path(path: str) -> bool:
    """Check if a path points to an image file."""
    return Path(path).suffix.lower() in IMAGE_EXTENSIONS


def read_file_attachment(path: str, project_dir: str) -> Attachment | None:
    """Read a file and return an Attachment. Returns None if file doesn't exist."""
    # Resolve relative to project dir
    full_path = Path(project_dir) / path if not os.path.isabs(path) else Path(path)

    if not full_path.exists():
        return None

    mime_type = mimetypes.guess_type(str(full_path))[0] or "text/plain"

    if is_image_path(str(full_path)):
        with open(full_path, "rb") as f:
            content = base64.b64encode(f.read()).decode("ascii")
        return Attachment(
            path=str(full_path),
            content=content,
            mime_type=mime_type,
            is_image=True,
        )
    else:
        try:
            content = full_path.read_text(encoding="utf-8", errors="replace")
            # Truncate very large files
            if len(content) > 50000:
                content = content[:50000] + "\n\n... (truncated, file too large)"
            return Attachment(
                path=str(full_path),
                content=content,
                mime_type=mime_type,
            )
        except Exception:
            return None


def parse_references(text: str, project_dir: str) -> tuple[str, list[Attachment]]:
    """Parse @file references and #image:path references from text.

    Supported formats:
      @path/to/file.py — attach file content
      #image:path/to/screenshot.png — attach image

    Returns (cleaned_prompt, attachments).
    """
    attachments: list[Attachment] = []

    # Parse #image:path references
    image_pattern = re.compile(r"#image:(\S+)")
    for match in image_pattern.finditer(text):
        path = match.group(1)
        att = read_file_attachment(path, project_dir)
        if att:
            attachments.append(att)

    text = image_pattern.sub("", text)

    # Parse @file references
    file_pattern = re.compile(r"@(\S+\.\w+)")
    for match in file_pattern.finditer(text):
        path = match.group(1)
        att = read_file_attachment(path, project_dir)
        if att and not att.is_image:
            attachments.append(att)

    text = file_pattern.sub("", text).strip()

    return text, attachments


def format_prompt_with_attachments(prompt: str, attachments: list[Attachment]) -> str:
    """Combine prompt text with file attachment contents."""
    parts = [prompt]

    file_attachments = [a for a in attachments if not a.is_image]
    if file_attachments:
        parts.append("\n\n## Referenced Files\n")
        for att in file_attachments:
            parts.append(f"### {att.name}\n```\n{att.content}\n```\n")

    return "\n".join(parts)
