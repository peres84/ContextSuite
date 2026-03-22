"""Coding assistant CLI adapters."""

from contextsuite_cli.adapters.claude_code import ClaudeCodeAdapter
from contextsuite_cli.adapters.codex import CodexAdapter
from contextsuite_cli.adapters.cursor import CursorAdapter
from contextsuite_cli.adapters.registry import get_adapter, list_adapters, register_adapter

# Register all built-in adapters
register_adapter("codex", CodexAdapter)
register_adapter("claude", ClaudeCodeAdapter)
register_adapter("cursor", CursorAdapter)

__all__ = [
    "ClaudeCodeAdapter",
    "CodexAdapter",
    "CursorAdapter",
    "get_adapter",
    "list_adapters",
    "register_adapter",
]
