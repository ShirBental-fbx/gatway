from __future__ import annotations

from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from gateway.context.request_context import RequestContext, get_request_context
from gateway.domain.leads_service import LeadsService
from gateway.profiles.registry import ProfileRegistry, get_profile_registry
from gateway.proxy.endpoint import proxy_to_upstream

router = APIRouter(prefix="/leads", tags=["Leads"])

bearer_scheme = HTTPBearer(auto_error=False)


@router.post("/", summary="Create Lead")
async def create_lead(
    request: Request,
    raw: dict = Body(...),
    creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    ctx: RequestContext = Depends(get_request_context),
    registry: ProfileRegistry = Depends(get_profile_registry),
):
    """
    Create a new lead.
    
    This endpoint validates the request using profile-specific models,
    then proxies to the upstream Flask service for actual processing.
    """
    token = creds.credentials if creds else None  # TODO: use token or remove
    profile = registry.get(ctx.api_profile)
    ReqModel = profile.lead_create_request_model()

    try:
        req_obj = ReqModel.model_validate(raw)
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ex),
        )

    # For now, use existing domain service
    # TODO: Migrate to proxy_to_upstream once upstream endpoint is ready
    canonical = profile.map_lead_create_to_canonical(ctx, req_obj)
    domain_resp = await LeadsService().create_lead(canonical)
    resp_obj = profile.shape_lead_create_response(ctx, domain_resp)
    return resp_obj


# Example: Contract-first proxy endpoint pattern
# Uncomment and adapt when ready to proxy to upstream Flask
#
# @router.post("/proxy-example", summary="Create Lead (Proxy)")
# async def create_lead_proxy(
#     request: Request,
#     body: dict = Body(...),
# ):
#     """
#     Create a new lead via upstream Flask service.
#     
#     This is an example of the contract-first proxy pattern.
#     """
#     response = await proxy_to_upstream(
#         request=request,
#         upstream_path="/api/v1/leads",
#     )
#     return response
