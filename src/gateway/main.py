from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from gateway.errors.exceptions import FundboxAPIException
from gateway.errors.handlers import (
    fundbox_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from gateway.middleware.db.db_session import db_session_middleware
from gateway.oauth2.token_router import router as token_router
from gateway.routers.debug import router as debug_router
from gateway.routers.leads import router as leads_router
import os


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield
ROOT_PATH = os.getenv("GATEWAY_ROOT_PATH", "")

app = FastAPI(
    title="API Gateway",
    description="OAuth2 Gateway API using FastAPI",
    version="0.1.0",
    lifespan=lifespan,
    root_path=ROOT_PATH,
)

_disable_db_mw = os.getenv("DISABLE_DB_MIDDLEWARE", "").lower() in {"1", "true", "yes"}
if not _disable_db_mw:
    app.middleware("http")(db_session_middleware)

app.add_exception_handler(FundboxAPIException, fundbox_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(debug_router)

app.include_router(token_router)
app.include_router(leads_router)

@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/")
async def root():
    return {
        "name": "API Gateway",
        "version": "0.1.0",
        "docs": "/docs",
    }
