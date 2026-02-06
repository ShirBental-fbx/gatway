"""Auto-generated FastAPI router for Flask route group: api

This module contains contract-first route definitions that proxy to the legacy Flask service.
Routes are grouped by blueprint or path segment.

Generated from: artifacts/flask_routes.json
DO NOT EDIT MANUALLY - Regenerate using: python legacy/scripts/generate_fastapi_routers.py
"""

from __future__ import annotations

from fastapi import APIRouter, Request
from starlette.responses import Response

from gateway.proxy.endpoint import proxy_to_upstream

router = APIRouter(tags=["Legacy: api"])
@router.get("/api/v1/authenticate")
async def _api_v1_authenticate(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: /api/v1/authenticate
    Original path: /api/v1/authenticate
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/api/v1/authenticate")

@router.get("/api/v1/refresh_token")
async def _api_v1_refresh_token(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: /api/v1/refresh_token
    Original path: /api/v1/refresh_token
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/api/v1/refresh_token")

@router.get("/api/v1/reporting/{lead_id:str}")
async def _api_v1_reporting_get_current_state(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: /api/v1/reporting/get_current_state
    Original path: /api/v1/reporting/<string:lead_id>
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/api/v1/reporting/<string:lead_id>")

@router.get("/api/v1/reporting/registered_webhook_url")
async def _api_v1_registered_webhook_url(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: /api/v1/registered_webhook_url
    Original path: /api/v1/reporting/registered_webhook_url
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/api/v1/reporting/registered_webhook_url")

@router.get("/api/v1/reporting/test_webhook_url")
async def _api_v1_test_webhook_url(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: /api/v1/test_webhook_url
    Original path: /api/v1/reporting/test_webhook_url
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/api/v1/reporting/test_webhook_url")
