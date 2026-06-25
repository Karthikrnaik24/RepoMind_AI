"""FastAPI exception handlers for standard API failures."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions.types import BaseAppException
from app.interfaces.api.schemas.responses.base import failure_response


async def app_exception_handler(_: Request, exc: BaseAppException) -> JSONResponse:
    """Convert expected application exceptions to the standard failure envelope."""

    return JSONResponse(
        status_code=exc.status_code,
        content=failure_response(
            code=exc.code,
            message=exc.message,
            details=exc.details or None,
        ),
    )


async def request_validation_exception_handler(
    _: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Convert FastAPI request validation failures to the standard envelope."""

    return JSONResponse(
        status_code=422,
        content=failure_response(
            code="validation_error",
            message="The request is invalid.",
            details={"errors": exc.errors()},
        ),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register application-wide exception handlers."""

    app.add_exception_handler(BaseAppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
