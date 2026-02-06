"""Auto-generated FastAPI router for Flask route group: send_notification

This module contains contract-first route definitions that proxy to the legacy Flask service.
Routes are grouped by blueprint or path segment.

Generated from: artifacts/flask_routes.json
DO NOT EDIT MANUALLY - Regenerate using: python legacy/scripts/generate_fastapi_routers.py
"""

from __future__ import annotations

from fastapi import APIRouter, Request
from starlette.responses import Response

from gateway.proxy.endpoint import proxy_to_upstream

router = APIRouter(tags=["Legacy: send_notification"])
@router.get("/send_notification")
async def send_notification(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: send_notification
    Original path: /send_notification
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/send_notification")
