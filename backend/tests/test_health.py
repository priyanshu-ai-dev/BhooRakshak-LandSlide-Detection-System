"""
tests/test_health.py — Unit tests for GET /api/v1/health.

These tests mock the DB ping so no live database is required.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def health_client() -> TestClient:
    from app.core.database import get_db
    from unittest.mock import MagicMock

    mock_db = MagicMock()
    mock_db.execute.return_value.scalar.return_value = 1

    def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class TestHealthEndpoint:
    def test_health_returns_200(self, health_client: TestClient) -> None:
        with patch("app.api.v1.endpoints.health.ping_db", return_value=True):
            resp = health_client.get("/api/v1/health")
        assert resp.status_code == 200

    def test_health_response_schema(self, health_client: TestClient) -> None:
        with patch("app.api.v1.endpoints.health.ping_db", return_value=True):
            data = health_client.get("/api/v1/health").json()

        required_keys = {"status", "version", "service", "phase", "db_status"}
        assert required_keys.issubset(data.keys()), (
            f"Missing keys: {required_keys - set(data.keys())}"
        )

    def test_health_status_ok(self, health_client: TestClient) -> None:
        with patch("app.api.v1.endpoints.health.ping_db", return_value=True):
            data = health_client.get("/api/v1/health").json()
        assert data["status"] == "ok"

    def test_health_phase_is_1(self, health_client: TestClient) -> None:
        with patch("app.api.v1.endpoints.health.ping_db", return_value=True):
            data = health_client.get("/api/v1/health").json()
        assert data["phase"] == "1"

    def test_health_db_unreachable_reported(self, health_client: TestClient) -> None:
        """When DB is down the endpoint still returns 200 but db_status = 'unreachable'."""
        with patch("app.api.v1.endpoints.health.ping_db", return_value=False):
            resp = health_client.get("/api/v1/health")
        assert resp.status_code == 200
        assert resp.json()["db_status"] == "unreachable"
