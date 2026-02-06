"""Auto-generated FastAPI router for Flask route group: s3_data_upload

This module contains contract-first route definitions that proxy to the legacy Flask service.
Routes are grouped by blueprint or path segment.

Generated from: artifacts/flask_routes.json
DO NOT EDIT MANUALLY - Regenerate using: python legacy/scripts/generate_fastapi_routers.py
"""

from __future__ import annotations

from fastapi import APIRouter, Request
from starlette.responses import Response

from gateway.proxy.endpoint import proxy_to_upstream

router = APIRouter(tags=["Legacy: s3_data_upload"])
@router.get("/s3_data_upload")
async def s3_data_upload_notification(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: s3_data_upload_notification
    Original path: /s3_data_upload
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/s3_data_upload")
