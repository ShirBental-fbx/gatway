from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from gateway.main import app
from gateway.context.request_context import RequestContext, get_request_context


def _ctx_standard():
    return RequestContext(
        partner_id="p1",
        api_profile="standard",
        correlation_id="t1",
        client_id="c1",
        user_id=None,
    )


def _ctx_legacy():
    return RequestContext(
        partner_id="p1",
        api_profile="legacy",
        correlation_id="t1",
        client_id="c1",
        user_id=None,
    )


@pytest.fixture(autouse=True)
def _override_ctx_standard():
    async def override():
        return _ctx_standard()

    app.dependency_overrides[get_request_context] = override
    yield
    app.dependency_overrides.clear()


def test_create_lead_standard_success():
    client = TestClient(app)

    resp = client.post(
        "/leads",
        json={"business_id": "b1", "email": "a@b.com", "amount": 100},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["lead_id"] == "ld_123"
    assert body["status"] == "created"


def test_create_lead_standard_validation_error():
    client = TestClient(app)

    resp = client.post(
        "/leads",
        json={"business_id": "b1", "email": "a@b.com", "amount": 0},
    )

    assert resp.status_code == 400 or resp.status_code == 422

def test_create_lead_legacy_success():
    async def override():
        return _ctx_legacy()

    app.dependency_overrides[get_request_context] = override

    client = TestClient(app)
    resp = client.post(
        "/leads",
        json={"businessId": "b1", "email": "a@b.com", "requestedAmount": "100"},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == "ld_123"
    assert body["state"] == "created"

