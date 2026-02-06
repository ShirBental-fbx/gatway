"""Auto-generated FastAPI router for Flask route group: _string_original_platform_

This module contains contract-first route definitions that proxy to the legacy Flask service.
Routes are grouped by blueprint or path segment.

Generated from: artifacts/flask_routes.json
DO NOT EDIT MANUALLY - Regenerate using: python legacy/scripts/generate_fastapi_routers.py
"""

from __future__ import annotations

from fastapi import APIRouter, Request
from starlette.responses import Response

from gateway.proxy.endpoint import proxy_to_upstream

router = APIRouter(tags=["Legacy: _string_original_platform_"])
@router.get("/{original_platform:str}/account/{original_platform_unique_id:str}/migrate_user_to_platform")
async def migrate_user_to_platform(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: migrate_user_to_platform
    Original path: /<string:original_platform>/account/<string:original_platform_unique_id>/migrate_user_to_platform
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/<string:original_platform>/account/<string:original_platform_unique_id>/migrate_user_to_platform")
