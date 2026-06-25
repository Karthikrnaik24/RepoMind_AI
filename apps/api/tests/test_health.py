import app.main as app_main
from app.main import create_app
from httpx import ASGITransport, AsyncClient


async def test_testing_lifespan_skips_database_startup_check(monkeypatch) -> None:
    def fail_database_check() -> None:
        raise AssertionError("database startup check should be disabled in lightweight tests")

    monkeypatch.setattr(app_main, "check_database_connection", fail_database_check)
    app = create_app()

    async with app.router.lifespan_context(app):
        assert app.state.settings.app_environment == "testing"


async def test_health_endpoint_returns_ok() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=create_app()),
        base_url="http://test",
    ) as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_v1_health_endpoint_returns_standard_success_response() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=create_app()),
        base_url="http://test",
    ) as client:
        response = await client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "data": {"status": "ok"},
        "meta": {},
    }


async def test_v1_status_endpoint_returns_service_metadata() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=create_app()),
        base_url="http://test",
    ) as client:
        response = await client.get("/api/v1/status")

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "data": {
            "status": "ok",
            "database": "configured",
            "supabase": "configured",
            "service": "repomind-api",
            "version": "0.1.0",
        },
        "meta": {},
    }


async def test_v1_responses_include_request_id_header() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=create_app()),
        base_url="http://test",
    ) as client:
        response = await client.get("/api/v1/status", headers={"X-Request-ID": "test-request-id"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "test-request-id"
