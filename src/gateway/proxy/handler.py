"""Reverse proxy request handler."""

from __future__ import annotations

import time
import uuid
import re

import logging
from fastapi import Request, Response
from starlette.responses import StreamingResponse

from gateway.proxy.canary import CanaryRouter, load_canary_config
from gateway.proxy.client import get_proxy_client

logger = logging.getLogger(__name__)

# Hop-by-hop headers that should not be forwarded
HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "transfer-encoding",
    "upgrade",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailer",
}


def _get_request_id(request: Request) -> str:
    """
    Get or generate request-id header.
    
    Upstream uses 'request-id' (lowercase, hyphenated) as per:
    src/common/FrontendAPI.py:37 and src/Core.py:47-48
    
    Gateway compatibility behavior:
    - If incoming request has 'x-request-id' but not 'request-id', copy it to 'request-id'
    - If neither exists, generate new 'request-id'
    """
    # Check for request-id (upstream format) first
    request_id = request.headers.get("request-id")
    
    # Gateway compatibility: bridge x-request-id to request-id
    if not request_id:
        request_id = (
            request.headers.get("X-Request-ID")
            or request.headers.get("X-Correlation-Id")
        )
    
    # Generate if still not found
    if not request_id:
        request_id = str(uuid.uuid4())
    
    return request_id


def _extract_partner_from_path(path: str) -> str | None:
    """
    Extract partner ID from URL path if present.
    
    Supports patterns like:
    - /partners/{partner}/...
    - /api/v1/partners/{partner}/...
    
    Returns partner ID or None if not found.
    """
    # Match /partners/{partner}/ pattern
    match = re.search(r"/partners/([^/]+)", path)
    if match:
        return match.group(1)
    return None


def _filter_hop_by_hop_headers(headers: dict[str, str]) -> dict[str, str]:
    """Remove hop-by-hop headers from headers dict."""
    return {
        k: v
        for k, v in headers.items()
        if k.lower() not in HOP_BY_HOP_HEADERS
    }


def _get_forwarded_headers(request: Request) -> dict[str, str]:
    """
    Build headers to forward to upstream.
    
    Pure transport layer - no DB dependencies, no gateway-specific context headers.
    Only forwards existing headers and adds standard proxy headers.

    Args:
        request: FastAPI request

    Returns:
        Headers dict for upstream request
    """
    headers = dict(request.headers)

    # Remove hop-by-hop headers (but preserve Host - it's not hop-by-hop)
    # Host header will be replaced by httpx with the upstream host, but we forward
    # the original host in X-Forwarded-Host
    headers = _filter_hop_by_hop_headers(headers)

    # Ensure request-id is set (upstream format: lowercase, hyphenated)
    # Gateway compatibility: bridge x-request-id to request-id if needed
    request_id = _get_request_id(request)
    headers["request-id"] = request_id

    # Add X-Forwarded-* headers (standard proxy headers)
    # Note: We forward the original Host in X-Forwarded-Host
    # The actual Host header will be set by httpx to the upstream host
    client_host = request.headers.get("host", "")
    if client_host:
        headers["X-Forwarded-Host"] = client_host

    # Determine protocol
    proto = "https"
    if request.url.scheme:
        proto = request.url.scheme
    elif request.headers.get("x-forwarded-proto"):
        proto = request.headers.get("x-forwarded-proto")
    headers["X-Forwarded-Proto"] = proto

    # X-Forwarded-For
    forwarded_for = request.headers.get("x-forwarded-for", "")
    client_ip = request.client.host if request.client else ""
    if forwarded_for:
        headers["X-Forwarded-For"] = f"{forwarded_for}, {client_ip}"
    elif client_ip:
        headers["X-Forwarded-For"] = client_ip

    return headers


async def proxy_handler(
    request: Request,
    full_path: str,
    canary_router: CanaryRouter | None = None,
    debug_mode: bool = False,
) -> Response:
    """
    Handle reverse proxy request.
    
    Pure transport layer - no DB dependencies. Forwards requests transparently.

    Args:
        request: FastAPI request
        full_path: Full path to forward (including query string)
        canary_router: Optional canary router for traffic splitting
        debug_mode: If True, add X-Gateway-Upstream header to response

    Returns:
        Response from upstream
    """
    start_time = time.time()
    request_id = _get_request_id(request)

    # Get proxy client
    proxy_client = get_proxy_client()

    # Extract partner from URL path if needed (no DB required)
    # Supports /partners/{partner}/... pattern
    partner_id = _extract_partner_from_path(full_path.split("?")[0])

    # Determine upstream (canary or legacy)
    use_canary = False
    upstream_reason = "default"
    if canary_router and proxy_client.upstream_canary_base_url:
        # Upstream has NO idempotency mechanism (per UPSTREAM_EXPECTATIONS.md)
        # So we pass has_idempotency_key=False always
        use_canary, upstream_reason = canary_router.should_use_canary(
            partner=partner_id,
            path=full_path.split("?")[0],  # Path without query
            method=request.method,
            has_idempotency_key=False,  # Upstream has no idempotency mechanism
        )

    # Build upstream URL - ensure query string is included
    # full_path from router includes query string, but we also check request.url.query for safety
    path_without_query = full_path.split("?")[0]
    query_string = request.url.query
    if query_string:
        upstream_path = f"{path_without_query}?{query_string}"
    else:
        upstream_path = full_path
    
    upstream_url = proxy_client.get_upstream_url(upstream_path, use_canary=use_canary)

    # Build headers (pure transport - no gateway context headers)
    upstream_headers = _get_forwarded_headers(request)

    # Get request body
    body = await request.body()

    # Make upstream request with streaming support
    try:
        # Use stream=True for true streaming support
        async with proxy_client.client.stream(
            method=request.method,
            url=upstream_url,
            headers=upstream_headers,
            content=body if body else None,
        ) as upstream_response:

            # Read response status and headers
            await upstream_response.aread()  # Read headers
            
            latency_ms = int((time.time() - start_time) * 1000)

            # Log request
            logger.info(
                f"proxy_request request_id={request_id} partner={partner_id or 'none'} "
                f"method={request.method} path={path_without_query} "
                f"chosen_upstream={'canary' if use_canary else 'legacy'} "
                f"upstream_reason={upstream_reason} upstream_status={upstream_response.status_code} "
                f"latency_ms={latency_ms}"
            )

            # Build response headers (filter hop-by-hop)
            response_headers = _filter_hop_by_hop_headers(dict(upstream_response.headers))

            # Add debug header if enabled
            if debug_mode:
                response_headers["X-Gateway-Upstream"] = "canary" if use_canary else "legacy"
                response_headers["X-Gateway-Upstream-Reason"] = upstream_reason

            # Always use streaming for true streaming support
            async def stream_content():
                async for chunk in upstream_response.aiter_bytes():
                    yield chunk

            return StreamingResponse(
                stream_content(),
                status_code=upstream_response.status_code,
                headers=response_headers,
                media_type=upstream_response.headers.get("content-type"),
            )

    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        logger.error(
            f"proxy_request_failed request_id={request_id} partner={partner_id or 'none'} "
            f"method={request.method} path={path_without_query} "
            f"upstream_url={upstream_url} error={str(e)} latency_ms={latency_ms}"
        )
        
        # Import here to avoid circular dependency
        from httpx import ConnectError, TimeoutException
        
        # Return appropriate error response
        if isinstance(e, ConnectError):
            # Upstream connection failed - return 502 Bad Gateway
            return Response(
                content=f"Bad Gateway: Unable to connect to upstream at {upstream_url}",
                status_code=502,
                headers={"Content-Type": "text/plain"},
            )
        elif isinstance(e, TimeoutException):
            # Upstream timeout - return 504 Gateway Timeout
            return Response(
                content=f"Gateway Timeout: Upstream at {upstream_url} did not respond in time",
                status_code=504,
                headers={"Content-Type": "text/plain"},
            )
        else:
            # Other errors - return 502 Bad Gateway
            return Response(
                content=f"Bad Gateway: {str(e)}",
                status_code=502,
                headers={"Content-Type": "text/plain"},
            )
