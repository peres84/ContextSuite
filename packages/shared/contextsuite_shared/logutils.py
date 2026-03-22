"""Shared console logging helpers for ContextSuite services."""

from __future__ import annotations

import logging
import sys
from datetime import datetime

LEVEL_STYLES = {
    logging.DEBUG: "\x1b[38;5;245m",
    logging.INFO: "\x1b[38;5;81m",
    logging.WARNING: "\x1b[38;5;214m",
    logging.ERROR: "\x1b[38;5;203m",
    logging.CRITICAL: "\x1b[1;38;5;196m",
}
RESET = "\x1b[0m"


def _short_logger_name(name: str) -> str:
    for prefix in (
        "contextsuite_agent.",
        "contextsuite_cli.",
        "contextsuite_shared.",
    ):
        if name.startswith(prefix):
            name = name[len(prefix) :]
            break
    return name.replace("workflow.nodes.", "workflow.")


class ContextSuiteFormatter(logging.Formatter):
    """Compact single-line formatter with optional ANSI color."""

    def __init__(self, service: str, *, use_color: bool) -> None:
        super().__init__()
        self.service = service
        self.use_color = use_color

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")
        level = record.levelname[:4].upper()
        logger_name = _short_logger_name(record.name)
        message = record.getMessage()

        if self.use_color:
            level = f"{LEVEL_STYLES.get(record.levelno, '')}{level}{RESET}"
            service = f"\x1b[38;5;122m[{self.service}]{RESET}"
            logger_name = f"\x1b[38;5;250m{logger_name}{RESET}"
        else:
            service = f"[{self.service}]"

        output = f"{timestamp} {level} {service} {logger_name} {message}"
        if record.exc_info:
            output = f"{output}\n{self.formatException(record.exc_info)}"
        return output


def configure_logging(*, service: str, level: str = "INFO") -> None:
    """Configure process-wide console logging for a service."""
    stream = sys.stderr
    use_color = bool(getattr(stream, "isatty", lambda: False)())

    handler = logging.StreamHandler(stream)
    handler.setFormatter(ContextSuiteFormatter(service, use_color=use_color))

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level.upper())
    root.addHandler(handler)

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

