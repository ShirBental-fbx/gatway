"""Auto-generated FastAPI router for Flask route group: v1

This module contains contract-first route definitions that proxy to the legacy Flask service.
Routes are grouped by blueprint or path segment.

Generated from: artifacts/flask_routes.json
DO NOT EDIT MANUALLY - Regenerate using: python legacy/scripts/generate_fastapi_routers.py
"""

from __future__ import annotations

from fastapi import APIRouter, Request
from starlette.responses import Response

from gateway.proxy.endpoint import proxy_to_upstream

router = APIRouter(tags=["Legacy: v1"])
@router.get("/v1/loan/agreements/{token:str}")
async def get_agreement_url(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: get_agreement_url
    Original path: /v1/loan/agreements/<string:token>
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/v1/loan/agreements/<string:token>")

@router.get("/v1/partners/{partner_name:str}/application_review_started")
async def application_review_started(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: application_review_started
    Original path: /v1/partners/<string:partner_name>/application_review_started
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/v1/partners/<string:partner_name>/application_review_started")

@router.get("/v1/partners/{partner_name:str}/cancel_partner_application")
async def cancel_partner_application(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: cancel_partner_application
    Original path: /v1/partners/<string:partner_name>/cancel_partner_application
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/v1/partners/<string:partner_name>/cancel_partner_application")

@router.get("/v1/partners/{partner_name:str}/cancel_partner_offer_creation")
async def cancel_partner_offer_creation(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: cancel_partner_offer_creation
    Original path: /v1/partners/<string:partner_name>/cancel_partner_offer_creation
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/v1/partners/<string:partner_name>/cancel_partner_offer_creation")

@router.get("/v1/partners/{partner_name:str}/change_bank_account")
async def change_bank_account(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: change_bank_account
    Original path: /v1/partners/<string:partner_name>/change_bank_account
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/v1/partners/<string:partner_name>/change_bank_account")

@router.get("/v1/partners/{partner_name:str}/complete_lead_advance_pre_qual")
async def complete_lead_advance_pre_qual(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: complete_lead_advance_pre_qual
    Original path: /v1/partners/<string:partner_name>/complete_lead_advance_pre_qual
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/v1/partners/<string:partner_name>/complete_lead_advance_pre_qual")

@router.get("/v1/partners/{partner_name:str}/create_partner_application")
async def create_partner_application(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: create_partner_application
    Original path: /v1/partners/<string:partner_name>/create_partner_application
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/v1/partners/<string:partner_name>/create_partner_application")

@router.get("/v1/partners/{partner_name:str}/create_partner_offer")
async def create_partner_offer(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: create_partner_offer
    Original path: /v1/partners/<string:partner_name>/create_partner_offer
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/v1/partners/<string:partner_name>/create_partner_offer")

@router.get("/v1/partners/{partner_name:str}/echo")
async def stripe_incoming_fundbox_echo(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: stripe_incoming_fundbox_echo
    Original path: /v1/partners/<string:partner_name>/echo
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/v1/partners/<string:partner_name>/echo")

@router.get("/v1/partners/{partner_name:str}/send_payment_notification")
async def send_payment_notification(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: send_payment_notification
    Original path: /v1/partners/<string:partner_name>/send_payment_notification
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/v1/partners/<string:partner_name>/send_payment_notification")

@router.get("/v1/partners/{partner_name:str}/send_report")
async def send_report(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: send_report
    Original path: /v1/partners/<string:partner_name>/send_report
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/v1/partners/<string:partner_name>/send_report")

@router.get("/v1/partners/{partner_name:str}/submit_lead")
async def create_generic_business_lead(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: create_generic_business_lead
    Original path: /v1/partners/<string:partner_name>/submit_lead
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/v1/partners/<string:partner_name>/submit_lead")

@router.get("/v1/partners/{partner_name:str}/submit_lead_advance_pre_qual")
async def submit_lead_advance_pre_qual(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: submit_lead_advance_pre_qual
    Original path: /v1/partners/<string:partner_name>/submit_lead_advance_pre_qual
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/v1/partners/<string:partner_name>/submit_lead_advance_pre_qual")

@router.get("/v1/partners/{partner_name:str}/submit_lead_with_pre_qual")
async def create_generic_business_lead_with_pre_qual(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: create_generic_business_lead_with_pre_qual
    Original path: /v1/partners/<string:partner_name>/submit_lead_with_pre_qual
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/v1/partners/<string:partner_name>/submit_lead_with_pre_qual")

@router.get("/v1/partners/{partner_name:str}/submit_partner_application")
async def submit_partner_application(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: submit_partner_application
    Original path: /v1/partners/<string:partner_name>/submit_partner_application
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/v1/partners/<string:partner_name>/submit_partner_application")

@router.get("/v1/partners/loc/{partner_name:str}/calculate_account_outstanding_balance")
async def calculate_account_outstanding_balance(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: calculate_account_outstanding_balance
    Original path: /v1/partners/loc/<string:partner_name>/calculate_account_outstanding_balance
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/v1/partners/loc/<string:partner_name>/calculate_account_outstanding_balance")

@router.get("/v1/partners/loc/{partner_name:str}/calculate_account_payoff")
async def calculate_account_payoff(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: calculate_account_payoff
    Original path: /v1/partners/loc/<string:partner_name>/calculate_account_payoff
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/v1/partners/loc/<string:partner_name>/calculate_account_payoff")

@router.get("/v1/partners/loc/{partner_name:str}/calculate_custom_amount_payment")
async def calculate_custom_amount_payment(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: calculate_custom_amount_payment
    Original path: /v1/partners/loc/<string:partner_name>/calculate_custom_amount_payment
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/v1/partners/loc/<string:partner_name>/calculate_custom_amount_payment")

@router.get("/v1/partners/loc/{partner_name:str}/calculate_draw_outstanding_balance")
async def calculate_draw_outstanding_balance(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: calculate_draw_outstanding_balance
    Original path: /v1/partners/loc/<string:partner_name>/calculate_draw_outstanding_balance
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/v1/partners/loc/<string:partner_name>/calculate_draw_outstanding_balance")

@router.get("/v1/partners/loc/{partner_name:str}/calculate_draw_payoff")
async def calculate_draw_payoff(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: calculate_draw_payoff
    Original path: /v1/partners/loc/<string:partner_name>/calculate_draw_payoff
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/v1/partners/loc/<string:partner_name>/calculate_draw_payoff")

@router.get("/v1/partners/loc/{partner_name:str}/calculate_overdue_balance_payment")
async def calculate_overdue_balance_payment(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: calculate_overdue_balance_payment
    Original path: /v1/partners/loc/<string:partner_name>/calculate_overdue_balance_payment
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/v1/partners/loc/<string:partner_name>/calculate_overdue_balance_payment")

@router.get("/v1/partners/loc/{partner_name:str}/execute_draw_payoff")
async def execute_draw_payoff(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: execute_draw_payoff
    Original path: /v1/partners/loc/<string:partner_name>/execute_draw_payoff
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/v1/partners/loc/<string:partner_name>/execute_draw_payoff")

@router.get("/v1/partners/loc/{partner_name:str}/get_draws")
async def get_draws(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: get_draws
    Original path: /v1/partners/loc/<string:partner_name>/get_draws
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/v1/partners/loc/<string:partner_name>/get_draws")

@router.get("/v1/partners/loc/{partner_name:str}/retrieve_payment_method")
async def retrieve_payment_method(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: retrieve_payment_method
    Original path: /v1/partners/loc/<string:partner_name>/retrieve_payment_method
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/v1/partners/loc/<string:partner_name>/retrieve_payment_method")

@router.get("/v1/partners/loc/{partner_name:str}/start_application")
async def start_application(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: start_application
    Original path: /v1/partners/loc/<string:partner_name>/start_application
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/v1/partners/loc/<string:partner_name>/start_application")

@router.get("/v1/partners/loc/{partner_name:str}/submit_application")
async def submit_application(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: submit_application
    Original path: /v1/partners/loc/<string:partner_name>/submit_application
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/v1/partners/loc/<string:partner_name>/submit_application")

@router.get("/v1/partners/loc/{partner_name:str}/submit_draw")
async def submit_draw(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: submit_draw
    Original path: /v1/partners/loc/<string:partner_name>/submit_draw
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/v1/partners/loc/<string:partner_name>/submit_draw")
