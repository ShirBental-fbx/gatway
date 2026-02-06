"""Auto-generated FastAPI router for Flask route group: fetch_credit_report

This module contains contract-first route definitions that proxy to the legacy Flask service.
Routes are grouped by blueprint or path segment.

Generated from: artifacts/flask_routes.json
DO NOT EDIT MANUALLY - Regenerate using: python legacy/scripts/generate_fastapi_routers.py
"""

from __future__ import annotations

from fastapi import APIRouter, Request
from starlette.responses import Response

from gateway.proxy.endpoint import proxy_to_upstream

router = APIRouter(tags=["Legacy: fetch_credit_report"])
@router.get("/fetch_credit_report")
async def fetch_credit_report(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: fetch_credit_report
    Original path: /fetch_credit_report
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/fetch_credit_report")
