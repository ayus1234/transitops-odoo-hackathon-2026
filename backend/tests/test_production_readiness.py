"""
Unit tests for Milestone 1 Production Readiness (Structured Logging, Rate Limiting, Observability).
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint_response():
    """Verify health check endpoint returns 200 OK with expected structure."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "environment" in data


def test_structured_logging_and_request_id_middleware():
    """Verify LoggingMiddleware injects x-request-id correlation header."""
    response = client.get("/health")
    assert response.status_code == 200
    assert "x-request-id" in response.headers
    assert len(response.headers["x-request-id"]) > 10


def test_root_endpoint_metadata():
    """Verify root API metadata endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["health"] == "/health"
