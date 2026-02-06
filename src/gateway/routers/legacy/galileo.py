"""Auto-generated FastAPI router for Flask route group: galileo

This module contains contract-first route definitions that proxy to the legacy Flask service.
Routes are grouped by blueprint or path segment.

Generated from: artifacts/flask_routes.json
DO NOT EDIT MANUALLY - Regenerate using: python legacy/scripts/generate_fastapi_routers.py
"""

from __future__ import annotations

from fastapi import APIRouter, Request
from starlette.responses import Response

from gateway.proxy.endpoint import proxy_to_upstream

router = APIRouter(tags=["Legacy: galileo"])
@router.get("/galileo/AccountEvent")
async def account_event_api(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: account_event_api
    Original path: /galileo/AccountEvent
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/galileo/AccountEvent")

@router.get("/galileo/Authorization")
async def auhorization_event_api(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: auhorization_event_api
    Original path: /galileo/Authorization
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/galileo/Authorization")

@router.get("/galileo/Settlement")
async def settlement_event_api(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: settlement_event_api
    Original path: /galileo/Settlement
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/galileo/Settlement")

@router.get("/galileo/Transaction")
async def transaction_event_api(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: transaction_event_api
    Original path: /galileo/Transaction
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/galileo/Transaction")

@router.get("/galileo/incoming_ach_debit_transaction")
async def galileo_incoming_ach_debit_transaction(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: galileo_incoming_ach_debit_transaction
    Original path: /galileo/incoming_ach_debit_transaction
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/galileo/incoming_ach_debit_transaction")

@router.get("/galileo/incoming_debit_card_transaction/Authorization")
async def galileo_incoming_debit_card_transaction(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: galileo_incoming_debit_card_transaction
    Original path: /galileo/incoming_debit_card_transaction/Authorization
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/galileo/incoming_debit_card_transaction/Authorization")
