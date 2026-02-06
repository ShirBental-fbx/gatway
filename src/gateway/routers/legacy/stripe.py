"""Auto-generated FastAPI router for Flask route group: stripe

This module contains contract-first route definitions that proxy to the legacy Flask service.
Routes are grouped by blueprint or path segment.

Generated from: artifacts/flask_routes.json
DO NOT EDIT MANUALLY - Regenerate using: python legacy/scripts/generate_fastapi_routers.py
"""

from __future__ import annotations

from fastapi import APIRouter, Request
from starlette.responses import Response

from gateway.proxy.endpoint import proxy_to_upstream

router = APIRouter(tags=["Legacy: stripe"])
@router.get("/stripe/disconnect_user")
async def _stripe_disconnect_user(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: /stripe/disconnect_user
    Original path: /stripe/disconnect_user
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/stripe/disconnect_user")

@router.get("/stripe/get_dashboard_data")
async def stripe_get_dashboard_data(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: stripe_get_dashboard_data
    Original path: /stripe/get_dashboard_data
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/stripe/get_dashboard_data")

@router.get("/stripe/get_user_status")
async def stripe_get_user_status(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: stripe_get_user_status
    Original path: /stripe/get_user_status
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/stripe/get_user_status")

@router.get("/stripe/get_user_token")
async def _stripe_get_user_token(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: /stripe/get_user_token
    Original path: /stripe/get_user_token
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/stripe/get_user_token")

@router.get("/stripe/is_user_signed_disclosure")
async def _stripe_is_user_signed_disclosure(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: /stripe/is_user_signed_disclosure
    Original path: /stripe/is_user_signed_disclosure
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/stripe/is_user_signed_disclosure")

@router.get("/stripe/prepare_offers")
async def stripe_prepare_offers(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: stripe_prepare_offers
    Original path: /stripe/prepare_offers
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/stripe/prepare_offers")

@router.get("/stripe/request_draw")
async def stripe_request_draw(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: stripe_request_draw
    Original path: /stripe/request_draw
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/stripe/request_draw")
