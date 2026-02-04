from __future__ import annotations

from fastapi import Request
from starlette.responses import Response

from gateway.context.request_context import get_request_context


async def request_context_headers_middleware(request: Request, call_next):
    response: Response = await call_next(request)

    try:
        ctx = await get_request_context(request)
        response.headers["X-Partner-Id"] = ctx.partner_id
        response.headers["X-API-Profile"] = ctx.api_profile
    except Exception:
        pass

    return response
