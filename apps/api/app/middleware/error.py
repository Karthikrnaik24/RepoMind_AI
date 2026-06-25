"""Unhandled error middleware."""

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.logging import get_logger
from app.interfaces.api.schemas.responses.base import failure_response
from app.middleware.request_id import REQUEST_ID_HEADER


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Return a safe response for unexpected unhandled exceptions."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            return await call_next(request)
        except Exception:
            request_id = getattr(request.state, "request_id", None)
            get_logger("repomind.api.error").exception(
                "unhandled_request_error",
                extra={"path": request.url.path, "method": request.method},
            )
            response = JSONResponse(
                status_code=500,
                content=failure_response(
                    code="internal_error",
                    message="An unexpected error occurred.",
                ),
            )
            if request_id:
                response.headers[REQUEST_ID_HEADER] = request_id
            return response
