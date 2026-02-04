from __future__ import annotations

import os
from dataclasses import dataclass
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from gateway.db import get_db
from gateway.oauth2.token_verifier import verify_access_token


bearer_scheme = HTTPBearer(auto_error=False)
@dataclass(frozen=True)
class RequestContext:
    partner_id: str
    api_profile: str
    correlation_id: str
    client_id: str | None = None
    user_id: str | None = None


async def _extract_bearer_token(request: Request) -> str:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )
    token = auth.removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )
    return token


async def get_request_context(
    request: Request,
    db: Session = Depends(get_db),
    creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> RequestContext:
    token = creds.credentials if creds else None
    correlation_id = request.headers.get("X-Correlation-Id", "na")

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")


    if _is_true(os.getenv("GATEWAY_DEV_AUTH")):
        if token == "standard":
            claims = {"partner_id": "dev", "api_profile": "standard", "client_id": None, "sub": None}
        elif token == "legacy":
            claims = {"partner_id": "dev", "api_profile": "legacy", "client_id": None, "sub": None}
        else:
            claims = {"partner_id": "dev", "api_profile": request.headers.get("X-Api-Profile", "standard")}
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid dev token")
    else:
        claims = await verify_access_token(token=token, db=db)

    return RequestContext(
            partner_id=str(claims["partner_id"]),
            api_profile=str(claims["api_profile"]),
            correlation_id=correlation_id,
            client_id=str(claims["client_id"]) if claims.get("client_id") else None,
            user_id=str(claims["sub"]) if claims.get("sub") else None,
    )

def _is_true(v: str | None) -> bool:
    return (v or "").strip().lower() in {"1", "true", "yes", "y", "on"}
