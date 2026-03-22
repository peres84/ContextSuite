"""Supabase data access layer."""

from contextsuite_agent.persistence.approvals import ApprovalsRepo
from contextsuite_agent.persistence.client import get_supabase
from contextsuite_agent.persistence.documents import DocumentsRepo
from contextsuite_agent.persistence.prompts import PromptsRepo
from contextsuite_agent.persistence.runs import RunsRepo

__all__ = [
    "ApprovalsRepo",
    "DocumentsRepo",
    "PromptsRepo",
    "RunsRepo",
    "get_supabase",
]
