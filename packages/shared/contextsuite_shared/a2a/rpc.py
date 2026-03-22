"""JSON-RPC and A2A request models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from contextsuite_shared.a2a.task import Message


class JSONRPCRequest(BaseModel):
    """Generic JSON-RPC 2.0 request envelope."""

    jsonrpc: str = "2.0"
    method: str
    params: dict[str, Any] | None = None
    id: str | int | None = None


class JSONRPCError(BaseModel):
    """JSON-RPC 2.0 error payload."""

    code: int
    message: str
    data: Any | None = None


class JSONRPCSuccessResponse(BaseModel):
    """JSON-RPC 2.0 success envelope."""

    jsonrpc: str = "2.0"
    id: str | int | None
    result: Any


class JSONRPCErrorResponse(BaseModel):
    """JSON-RPC 2.0 error envelope."""

    jsonrpc: str = "2.0"
    id: str | int | None
    error: JSONRPCError


class MessageSendConfiguration(BaseModel):
    """Configuration for an A2A message/send request."""

    accepted_output_modes: list[str] | None = Field(default=None, alias="acceptedOutputModes")
    history_length: int | None = Field(default=None, alias="historyLength")
    push_notification_config: dict[str, Any] | None = Field(
        default=None,
        alias="pushNotificationConfig",
    )
    blocking: bool | None = None

    model_config = ConfigDict(populate_by_name=True)


class MessageSendParams(BaseModel):
    """Parameters for the A2A message/send method."""

    message: Message
    configuration: MessageSendConfiguration | None = None
    metadata: dict[str, Any] | None = None

    model_config = ConfigDict(populate_by_name=True)


class TaskQueryParams(BaseModel):
    """Parameters for the A2A tasks/get method."""

    id: str
    history_length: int | None = Field(default=None, alias="historyLength")
    metadata: dict[str, Any] | None = None

    model_config = ConfigDict(populate_by_name=True)


JSONRPC_PARSE_ERROR = -32700
JSONRPC_INVALID_REQUEST = -32600
JSONRPC_METHOD_NOT_FOUND = -32601
JSONRPC_INVALID_PARAMS = -32602
JSONRPC_INTERNAL_ERROR = -32603

A2A_TASK_NOT_FOUND = -32001
A2A_TASK_NOT_RESUMABLE = -32002
