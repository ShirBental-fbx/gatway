from __future__ import annotations

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from .exceptions import FundboxAPIException
from .types import ErrorStruct


def _payload(status: int, message: str, quiet: bool = False) -> dict:
    return {"status": status, "message": message, "quiet": quiet}


def fundbox_error_payload(exc: FundboxAPIException) -> dict:
    return _payload(
        status=exc.error.error_code,
        message=exc.error.format_message(*exc.message_formatting),
        quiet=exc.error.quiet,
    ) | ({"detail": exc.detail} if exc.detail else {})


async def fundbox_exception_handler(request: Request, exc: FundboxAPIException) -> JSONResponse:
    return JSONResponse(status_code=exc.error.http_status_code, content=fundbox_error_payload(exc))


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    # NOTE: choose whatever "status" mapping your legacy gateway used for these cases.
    # Safe default: use HTTP code as status for non-Fundbox errors.
    return JSONResponse(
        status_code=exc.status_code,
        content=_payload(status=exc.status_code, message=str(exc.detail), quiet=False),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    # Keep message string similar to your legacy: short + readable.
    # If you want 100% deterministic ordering: sort by ("loc", "msg").
    parts: list[str] = []
    for e in exc.errors():
        loc = ".".join(str(x) for x in e.get("loc", []) if x != "body")
        msg = e.get("msg", "Invalid value")
        parts.append(f"{loc}: {msg}" if loc else msg)

    message = "Bad request: " + "; ".join(parts) if parts else "Bad request"
    return JSONResponse(
        status_code=422,
        content=_payload(status=422, message=message, quiet=False),
    )
