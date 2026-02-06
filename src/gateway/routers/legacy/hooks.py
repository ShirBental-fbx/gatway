"""Auto-generated FastAPI router for Flask route group: hooks

This module contains contract-first route definitions that proxy to the legacy Flask service.
Routes are grouped by blueprint or path segment.

Generated from: artifacts/flask_routes.json
DO NOT EDIT MANUALLY - Regenerate using: python legacy/scripts/generate_fastapi_routers.py
"""

from __future__ import annotations

from fastapi import APIRouter, Request
from starlette.responses import Response

from gateway.proxy.endpoint import proxy_to_upstream

router = APIRouter(tags=["Legacy: hooks"])
@router.get("/hooks/{partner_name:str}/{loan_app_id:str}")
async def generic_hook(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: generic_hook
    Original path: /hooks/<string:partner_name>/<string:loan_app_id>
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/hooks/<string:partner_name>/<string:loan_app_id>")

@router.get("/hooks/{partner_name:str}/lead")
async def create_business_lead(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: create_business_lead
    Original path: /hooks/<string:partner_name>/lead
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/hooks/<string:partner_name>/lead")

@router.get("/hooks/{partner_name:str}/leads")
async def create_business_leads(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: create_business_leads
    Original path: /hooks/<string:partner_name>/leads
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/hooks/<string:partner_name>/leads")

@router.get("/hooks/alloy/journey")
async def alloy_journey_application_status_change_message(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: alloy_journey_application_status_change_message
    Original path: /hooks/alloy/journey
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/hooks/alloy/journey")

@router.get("/hooks/alloy/journey/v2")
async def alloy_journey_application_status_change_message_v2(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: alloy_journey_application_status_change_message_v2
    Original path: /hooks/alloy/journey/v2
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/hooks/alloy/journey/v2")

@router.get("/hooks/baselayer/search")
async def _hooks_baselayer_search(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: /hooks/baselayer/search
    Original path: /hooks/baselayer/search
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/hooks/baselayer/search")

@router.get("/hooks/docusign/")
async def docusign_hook(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: docusign_hook
    Original path: /hooks/docusign/
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/hooks/docusign/")

@router.get("/hooks/fundera/lead")
async def create_fundera_business_lead(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: create_fundera_business_lead
    Original path: /hooks/fundera/lead
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/hooks/fundera/lead")

@router.get("/hooks/inscribe/collect_session")
async def _hooks_inscribe_collect_session(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: /hooks/inscribe/collect_session
    Original path: /hooks/inscribe/collect_session
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/hooks/inscribe/collect_session")

@router.get("/hooks/inscribe/customer_approval")
async def _hooks_inscribe_customer_approval(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: /hooks/inscribe/customer_approval
    Original path: /hooks/inscribe/customer_approval
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/hooks/inscribe/customer_approval")

@router.get("/hooks/inscribe/doc_state")
async def _hooks_inscribe_doc_state(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: /hooks/inscribe/doc_state
    Original path: /hooks/inscribe/doc_state
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/hooks/inscribe/doc_state")

@router.get("/hooks/lendio/{webhook_subtype:str}/")
async def lendio_hook(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: lendio_hook
    Original path: /hooks/lendio/<string:webhook_subtype>/
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/hooks/lendio/<string:webhook_subtype>/")

@router.get("/hooks/lendio/v2/lead")
async def create_lendio_business_lead(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: create_lendio_business_lead
    Original path: /hooks/lendio/v2/lead
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/hooks/lendio/v2/lead")

@router.get("/hooks/ocrolus")
async def ocrolus_events(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: ocrolus_events
    Original path: /hooks/ocrolus
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/hooks/ocrolus")

@router.get("/hooks/plaid")
async def plaid_hook(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: plaid_hook
    Original path: /hooks/plaid
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/hooks/plaid")

@router.get("/hooks/pre_qual_augmented_underwriting")
async def pre_qual_augmented_underwriting(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: pre_qual_augmented_underwriting
    Original path: /hooks/pre_qual_augmented_underwriting
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/hooks/pre_qual_augmented_underwriting")

@router.get("/hooks/qbf/{loan_app_id:str}")
async def qbf_hook(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: qbf_hook
    Original path: /hooks/qbf/<string:loan_app_id>
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/hooks/qbf/<string:loan_app_id>")

@router.get("/hooks/stripe/fundbox/message")
async def stripe_incoming_fundbox_message(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: stripe_incoming_fundbox_message
    Original path: /hooks/stripe/fundbox/message
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/hooks/stripe/fundbox/message")

@router.get("/hooks/stripe/pimco/message")
async def stripe_incoming_pimco_message(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: stripe_incoming_pimco_message
    Original path: /hooks/stripe/pimco/message
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/hooks/stripe/pimco/message")

@router.get("/hooks/twilio/message")
async def twilio_incoming_message(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: twilio_incoming_message
    Original path: /hooks/twilio/message
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/hooks/twilio/message")

@router.get("/hooks/twilio/message_status_update")
async def twilio_message_status_update(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: twilio_message_status_update
    Original path: /hooks/twilio/message_status_update
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/hooks/twilio/message_status_update")

@router.get("/hooks/twilio/user_prefs")
async def twilio_user_prefs_update(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: twilio_user_prefs_update
    Original path: /hooks/twilio/user_prefs
    Methods: GET
    
    """
    return await proxy_to_upstream(request, upstream_path="/hooks/twilio/user_prefs")
