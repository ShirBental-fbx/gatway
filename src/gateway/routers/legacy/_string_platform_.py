"""Auto-generated FastAPI router for Flask route group: _string_platform_

This module contains contract-first route definitions that proxy to the legacy Flask service.
Routes are grouped by blueprint or path segment.

Generated from: artifacts/flask_routes.json
DO NOT EDIT MANUALLY - Regenerate using: python legacy/scripts/generate_fastapi_routers.py
"""

from __future__ import annotations

from fastapi import APIRouter, Request
from starlette.responses import Response

from gateway.proxy.endpoint import proxy_to_upstream

router = APIRouter(tags=["Legacy: _string_platform_"])
@router.get("/{platform:str}/account/{platform_unique_id:str}")
async def account_status(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: account_status
    Original path: /<string:platform>/account/<string:platform_unique_id>
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/<string:platform>/account/<string:platform_unique_id>")

@router.get("/{platform:str}/account/{platform_unique_id:str}/invoice/{invoice_id_at_platform:str}")
async def invoice_status(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: invoice_status
    Original path: /<string:platform>/account/<string:platform_unique_id>/invoice/<string:invoice_id_at_platform>
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/<string:platform>/account/<string:platform_unique_id>/invoice/<string:invoice_id_at_platform>")

@router.get("/{platform:str}/account/{platform_unique_id:str}/send_verification_email")
async def send_verification_email(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: send_verification_email
    Original path: /<string:platform>/account/<string:platform_unique_id>/send_verification_email
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/<string:platform>/account/<string:platform_unique_id>/send_verification_email")
