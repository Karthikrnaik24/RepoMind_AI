from app.core.exceptions import AuthorizationException, ResourceNotFoundException
from app.main import create_app
from fastapi import Query
from httpx import ASGITransport, AsyncClient


async def test_application_exception_handler_returns_standard_failure_response() -> None:
    app = create_app()

    @app.get("/test/not-found")
    def raise_not_found() -> None:
        raise ResourceNotFoundException("Missing test resource.")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/test/not-found")

    assert response.status_code == 404
    assert response.json() == {
        "success": False,
        "error": {
            "code": "resource_not_found",
            "message": "Missing test resource.",
        },
    }


async def test_request_validation_handler_returns_standard_failure_response() -> None:
    app = create_app()

    @app.get("/test/validation")
    def require_integer(value: int = Query(...)) -> dict[str, int]:
        return {"value": value}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/test/validation", params={"value": "not-an-int"})
    payload = response.json()

    assert response.status_code == 422
    assert payload["success"] is False
    assert payload["error"]["code"] == "validation_error"
    assert payload["error"]["message"] == "The request is invalid."
    assert "errors" in payload["error"]["details"]


async def test_authorization_exception_handler_returns_standard_403_response() -> None:
    app = create_app()

    @app.get("/test/forbidden")
    def raise_forbidden() -> None:
        raise AuthorizationException("Forbidden test action.")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/test/forbidden")

    assert response.status_code == 403
    assert response.json() == {
        "success": False,
        "error": {
            "code": "authorization_error",
            "message": "Forbidden test action.",
        },
    }
