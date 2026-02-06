"""Proxy router with catch-all route."""

from __future__ import annotations

from fastapi import APIRouter, Request

from gateway.proxy.handler import proxy_handler

router = APIRouter()


@router.api_route(
    "/{full_path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
    include_in_schema=False,
)
async def catch_all_proxy(request: Request, full_path: str):
    """
    Catch-all proxy route for upstream API.

    This route must be registered LAST to avoid shadowing:
    - /health
    - /debug/*
    - /partners/{partner}/docs
    - /partners/{partner}/openapi.json
    """
    from gateway.proxy.client import get_proxy_client
    
    # Get canary router and debug mode from proxy client (loaded once at startup)
    proxy_client = get_proxy_client()
    canary_router = proxy_client.canary_router
    debug_mode = proxy_client.debug_mode

    # Include query string in path
    query_string = str(request.url.query)
    if query_string:
        full_path_with_query = f"{full_path}?{query_string}"
    else:
        full_path_with_query = full_path

    return await proxy_handler(
        request=request,
        full_path=full_path_with_query,
        canary_router=canary_router,
        debug_mode=debug_mode,
    )
