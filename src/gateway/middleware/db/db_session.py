from __future__ import annotations

from starlette.requests import Request

from gateway.db.session import SessionLocal
from gateway.db.context import set_db

async def db_session_middleware(request: Request, call_next):
    db = SessionLocal()
    try:
        set_db(db)
        return await call_next(request)
    finally:
        db.close()
