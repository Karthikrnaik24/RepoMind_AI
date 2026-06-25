"""Standard API response envelopes."""

from typing import Any

from pydantic import BaseModel, Field


class ApiError(BaseModel):
    """Standard API error body."""

    code: str
    message: str
    details: dict[str, Any] | None = None


class ApiSuccessResponse[DataT](BaseModel):
    """Standard success response envelope."""

    success: bool = True
    data: DataT
    meta: dict[str, Any] = Field(default_factory=dict)


class ApiFailureResponse(BaseModel):
    """Standard failure response envelope."""

    success: bool = False
    error: ApiError


def success_response(data: BaseModel | dict[str, Any], meta: dict[str, Any] | None = None) -> dict:
    """Return a serializable success response envelope."""

    resolved_data = data.model_dump(mode="json") if isinstance(data, BaseModel) else data
    return {"success": True, "data": resolved_data, "meta": meta or {}}


def failure_response(
    *,
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> dict:
    """Return a serializable failure response envelope."""

    error: dict[str, Any] = {"code": code, "message": message}
    if details is not None:
        error["details"] = details
    return {"success": False, "error": error}
