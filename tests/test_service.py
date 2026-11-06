import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient  # noqa: E402
from service.app import app, validate_schema  # noqa: E402
import service.app as app_module  # noqa: E402


@pytest.fixture
def client():
    # Use TestClient with context manager to ensure startup/lifespan runs or mock readiness
    with TestClient(app) as test_client:
        yield test_client


def test_validate_schema_valid():
    """Test schema validation succeeds for well-formed 4-key JSON."""
    valid_payload = '{"intent": "alarm_set", "date": "tomorrow", "time": "seven am", "place": null}'
    res = validate_schema(valid_payload)
    assert res is not None
    assert res["intent"] == "alarm_set"
    assert res["date"] == "tomorrow"
    assert res["time"] == "seven am"
    assert res["place"] is None


def test_validate_schema_invalid_keys():
    """Test schema validation rejects objects missing keys or with extra keys."""
    # Missing place
    invalid_1 = '{"intent": "weather_query", "date": null, "time": null}'
    assert validate_schema(invalid_1) is None

    # Extra key
    invalid_2 = '{"intent": "weather_query", "date": null, "time": null, "place": "london", "extra": 123}'
    assert validate_schema(invalid_2) is None

    # Invalid intent
    invalid_3 = '{"intent": "unknown_action", "date": null, "time": null, "place": null}'
    assert validate_schema(invalid_3) is None

    # Not JSON
    assert validate_schema("not json") is None
    assert validate_schema("{truncated") is None


def test_healthz_endpoint(client):
    """Liveness probe test: GET /healthz returns 200 and status ok."""
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_readyz_endpoint(client):
    """Readiness probe test: GET /readyz returns 200 when ready, 503 otherwise."""
    app_module.is_model_ready = True
    resp = client.get("/readyz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ready"}

    app_module.is_model_ready = False
    resp2 = client.get("/readyz")
    assert resp2.status_code == 503
    assert resp2.json() == {"status": "loading"}
    app_module.is_model_ready = True


def test_fault_injection(client):
    """Test FAULT_INJECT=1 returns HTTP 500 and exact error body {"error": "invalid_model_output"}."""
    os.environ["FAULT_INJECT"] = "1"
    app_module.is_model_ready = True

    resp = client.post("/parse", json={"text": "set an alarm for 7 am"})
    assert resp.status_code == 500
    assert resp.json() == {"error": "invalid_model_output"}
    assert "X-Model-Version" in resp.headers
    assert "X-Served-By" in resp.headers

    # Reset
    os.environ["FAULT_INJECT"] = "0"
