from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy import text
from sqlalchemy.orm import Session

from gateway.db.deps import get_db
from gateway.oauth2.asgi_request import ASGIOAuthRequest

router = APIRouter(prefix="/debug", tags=["debug"])


@router.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@router.get("/db")
async def db_check(db: Session = Depends(get_db)) -> dict:
    # SQLite-friendly, works everywhere
    value = db.execute(text("SELECT 1")).scalar_one()
    return {"db": "ok", "select_1": value}


@router.post("/oauth-request")
async def oauth_request_echo(request: Request) -> dict:
    oreq = await ASGIOAuthRequest.from_starlette(request)
    return {
        "method": oreq.method,
        "uri": oreq.uri,
        "args": oreq.args,
        "headers_has_content_type": "content-type" in oreq.headers,
        "form": oreq.form,
        "body_len": len(oreq.body),
    }
