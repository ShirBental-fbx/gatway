"""Auto-generated FastAPI router for Flask route group: oauth2

This module contains contract-first route definitions that proxy to the legacy Flask service.
Routes are grouped by blueprint or path segment.

Generated from: artifacts/flask_routes.json
DO NOT EDIT MANUALLY - Regenerate using: python legacy/scripts/generate_fastapi_routers.py
"""

from __future__ import annotations

from fastapi import APIRouter, Request
from starlette.responses import Response

from gateway.proxy.endpoint import proxy_to_upstream

router = APIRouter(tags=["Legacy: oauth2"])
@router.get("/oauth2/revoke")
async def revoke(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: revoke
    Original path: /oauth2/revoke
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/oauth2/revoke")

@router.get("/oauth2/token")
async def token(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: token
    Original path: /oauth2/token
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/oauth2/token")
