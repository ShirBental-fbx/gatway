from __future__ import annotations

from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool


async def _as_dict(obj: Any) -> dict:
    if obj is None:
        return {}
    if isinstance(obj, dict):
        return obj
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "dict"):
        return obj.dict()
    if hasattr(obj, "__dict__"):
        return dict(obj.__dict__)
    return {}


async def _pick_first(data: dict, keys: list[str]) -> Any:
    for k in keys:
        if k in data and data[k] is not None:
            return data[k]
    return None


async def _bool_or_none(v: Any) -> bool | None:
    if v is None:
        return None
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        if v.lower() in {"true", "1", "yes"}:
            return True
        if v.lower() in {"false", "0", "no"}:
            return False
    return None


async def verify_access_token(token: str, db: Session) -> dict:
    try:
        from fundbox.sdk.authentication.client import get_authentication_service_api_client
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="External authentication service not configured",
        )

    client = get_authentication_service_api_client()

    candidate_methods = [
        "introspect_oauth2_token",
        "introspect_token",
        "validate_oauth2_token",
        "validate_access_token",
        "verify_access_token",
    ]

    method = next((getattr(client, n) for n in candidate_methods if hasattr(client, n)), None)
    if method is None:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Authentication service client does not support token validation",
        )

    try:
        result = await run_in_threadpool(method, token)
    except HTTPException:
        raise
    except Exception as ex:
        msg = str(ex)
        if ("invalid token" in msg.lower()) or ("token" in msg.lower() and "invalid" in msg.lower()):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=msg)

    data = _as_dict(result)

    active = _bool_or_none(_pick_first(data, ["active", "is_active", "valid", "is_valid"]))
    if active is False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    partner_id = _pick_first(data, ["partner_id", "partnerId", "partner", "tenant_id", "tenantId"])
    api_profile = _pick_first(data, ["api_profile", "apiProfile", "profile", "api_type", "apiType"])
    client_id = _pick_first(data, ["client_id", "clientId"])
    sub = _pick_first(data, ["sub", "user_id", "userId", "fbbid"])

    if partner_id is None or api_profile is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing required claims",
        )

    return {
        "partner_id": str(partner_id),
        "api_profile": str(api_profile),
        "client_id": str(client_id) if client_id is not None else None,
        "sub": str(sub) if sub is not None else None,
        "raw": data,
    }
