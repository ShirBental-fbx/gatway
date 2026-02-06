"""Helper utilities for creating contract-first proxy endpoints."""

from __future__ import annotations

from fastapi import Request
from starlette.responses import Response

from gateway.proxy.canary import CanaryRouter
from gateway.proxy.handler import proxy_handler


async def proxy_to_upstream(
    request: Request,
    upstream_path: str,
    canary_router: CanaryRouter | None = None,
    debug_mode: bool | None = None,
) -> Response:
    """
    Thin wrapper over proxy_handler for contract-first endpoints.
    
    This helper forwards requests to upstream Flask service using the same
    proxy implementation as the catch-all route. It reuses the shared httpx
    client managed by the FastAPI lifespan.
    
    IMPORTANT TRADEOFF:
    - If endpoint uses Pydantic request models, FastAPI will parse and validate
      the body, then serialize it via model_dump(). This means the forwarded
      body may differ from the original byte-for-byte (e.g., key ordering, formatting).
    - For byte-preserving forwarding, endpoints should accept Request only and
      not use Pydantic Body() models.
    
    Args:
        request: FastAPI request object
        upstream_path: Path to forward to upstream (e.g., "/api/v1/leads")
        canary_router: Optional canary router (if None, uses get_proxy_client().canary_router)
        debug_mode: Optional debug mode (if None, uses get_proxy_client().debug_mode)
        
    Returns:
        Response from upstream (reuses shared httpx client from lifespan)
    """
    from gateway.proxy.client import get_proxy_client
    
    # Get canary router and debug mode from proxy client if not provided
    # These are loaded once at startup, avoiding per-request config loading
    proxy_client = get_proxy_client()
    if canary_router is None:
        canary_router = proxy_client.canary_router
    if debug_mode is None:
        debug_mode = proxy_client.debug_mode
    
    # Build full path with query string
    query_string = str(request.url.query)
    if query_string:
        full_path = f"{upstream_path}?{query_string}"
    else:
        full_path = upstream_path
    
    # Delegate to the same proxy_handler used by catch-all route
    # This ensures identical behavior and reuses the shared httpx client
    return await proxy_handler(
        request=request,
        full_path=full_path,
        canary_router=canary_router,
        debug_mode=debug_mode,
    )


