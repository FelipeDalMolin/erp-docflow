"""Contract tests for the API healthcheck."""

from fastapi.testclient import TestClient

from erp_docflow_api.main import app

client = TestClient(app)


def test_health_returns_expected_contract() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {
        "status": "ok",
        "service": "erp-docflow-api",
    }


def test_automatic_documentation_is_not_exposed() -> None:
    for path in ("/docs", "/redoc", "/openapi.json"):
        assert client.get(path).status_code == 404
