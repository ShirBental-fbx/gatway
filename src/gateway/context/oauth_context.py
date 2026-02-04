from __future__ import annotations

from dataclasses import dataclass
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from gateway.db import get_db

@dataclass(frozen=True)
class OAuthClientContext:
    client_id: str
    partner_id: str
    api_profile: str

async def resolve_partner_id_from_client(client) -> str:
    meta = getattr(client, "client_metadata", {}) or {}
    return str(meta.get("partner_id") or client.client_id)

async def resolve_profile_from_client(client) -> str:
    meta = getattr(client, "client_metadata", {}) or {}
    return str(meta.get("api_profile") or "standard")

async def get_oauth_client_context(
    client_id: str,
    db: Session = Depends(get_db),
) -> OAuthClientContext:
    client = None

    if not client:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid client_id",
        )

    return OAuthClientContext(
        client_id=client_id,
        partner_id=resolve_partner_id_from_client(client),
        api_profile=resolve_profile_from_client(client),
    )
