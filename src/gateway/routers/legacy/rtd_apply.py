"""Auto-generated FastAPI router for Flask route group: rtd_apply

This module contains contract-first route definitions that proxy to the legacy Flask service.
Routes are grouped by blueprint or path segment.

Generated from: artifacts/flask_routes.json
DO NOT EDIT MANUALLY - Regenerate using: python legacy/scripts/generate_fastapi_routers.py
"""

from __future__ import annotations

from fastapi import APIRouter, Request
from starlette.responses import Response

from gateway.proxy.endpoint import proxy_to_upstream

router = APIRouter(tags=["Legacy: rtd_apply"])
@router.get("/rtd_apply")
async def rtd_apply(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: rtd_apply
    Original path: /rtd_apply
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/rtd_apply")
