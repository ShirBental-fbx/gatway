from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from gateway.main import app
import gateway.context.request_context as request_context



@pytest.fixture(autouse=True)
def _mock_verify_access_token(monkeypatch):
    async def fake_verify(token: str, db):
        if token == "standard":
            return {
                "partner_id": "p1",
                "api_profile": "standard",
                "client_id": "c1",
                "sub": None,
                "raw": {},
            }
        return {
            "partner_id": "p1",
            "api_profile": "legacy",
            "client_id": "c1",
            "sub": None,
            "raw": {},
        }

    monkeypatch.setattr(request_context, "verify_access_token", fake_verify)

def test_standard_with_bearer():
    client = TestClient(app)

    resp = client.post(
        "/leads",
        headers={"Authorization": "Bearer standard"},
        json={"business_id": "b1", "email": "a@b.com", "amount": 100},
    )

    assert resp.status_code == 200
    assert resp.json()["lead_id"] == "ld_123"


def test_legacy_with_bearer():
    client = TestClient(app)

    resp = client.post(
        "/leads",
        headers={"Authorization": "Bearer legacy"},
        json={"businessId": "b1", "email": "a@b.com", "requestedAmount": "100"},
    )

    assert resp.status_code == 200
    assert resp.json()["id"] == "ld_123"
