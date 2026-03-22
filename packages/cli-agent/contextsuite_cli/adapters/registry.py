"""Adapter registry — maps assistant names to adapter implementations."""

from __future__ import annotations

import logging

from contextsuite_cli.adapters.base import BaseAdapter

logger = logging.getLogger(__name__)

_registry: dict[str, type[BaseAdapter]] = {}


def register_adapter(name: str, adapter_cls: type[BaseAdapter]) -> None:
    """Register an adapter class for a coding assistant name."""
    _registry[name] = adapter_cls
    logger.info("register_adapter: registered '%s'", name)


def get_adapter(name: str) -> BaseAdapter | None:
    """Get an adapter instance by assistant name. Returns None if not found."""
    cls = _registry.get(name)
    if cls is None:
        return None
    return cls()


def list_adapters() -> list[str]:
    """List registered adapter names."""
    return list(_registry.keys())
