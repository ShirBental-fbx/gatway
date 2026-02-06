"""Auto-generated FastAPI router for Flask route group: mailhouse_round_delivered_notification

This module contains contract-first route definitions that proxy to the legacy Flask service.
Routes are grouped by blueprint or path segment.

Generated from: artifacts/flask_routes.json
DO NOT EDIT MANUALLY - Regenerate using: python legacy/scripts/generate_fastapi_routers.py
"""

from __future__ import annotations

from fastapi import APIRouter, Request
from starlette.responses import Response

from gateway.proxy.endpoint import proxy_to_upstream

router = APIRouter(tags=["Legacy: mailhouse_round_delivered_notification"])
@router.get("/mailhouse_round_delivered_notification")
async def mailhouse_delivered_notification(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: mailhouse_delivered_notification
    Original path: /mailhouse_round_delivered_notification
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/mailhouse_round_delivered_notification")
