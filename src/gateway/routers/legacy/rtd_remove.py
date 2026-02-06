"""Auto-generated FastAPI router for Flask route group: rtd_remove

This module contains contract-first route definitions that proxy to the legacy Flask service.
Routes are grouped by blueprint or path segment.

Generated from: artifacts/flask_routes.json
DO NOT EDIT MANUALLY - Regenerate using: python legacy/scripts/generate_fastapi_routers.py
"""

from __future__ import annotations

from fastapi import APIRouter, Request
from starlette.responses import Response

from gateway.proxy.endpoint import proxy_to_upstream

router = APIRouter(tags=["Legacy: rtd_remove"])
@router.get("/rtd_remove")
async def rtd_remove(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: rtd_remove
    Original path: /rtd_remove
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/rtd_remove")
