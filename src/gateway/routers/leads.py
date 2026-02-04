from __future__ import annotations

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from gateway.context.request_context import RequestContext, get_request_context
from gateway.domain.leads_service import LeadsService
from gateway.profiles.registry import ProfileRegistry, get_profile_registry

router = APIRouter(prefix="/leads", tags=["leads"])

bearer_scheme = HTTPBearer(auto_error=False)


@router.post("/")
async def create_lead(
    raw: dict = Body(...),
    creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    ctx: RequestContext = Depends(get_request_context),
    registry: ProfileRegistry = Depends(get_profile_registry),
):
    token = creds.credentials if creds else None
    profile = registry.get(ctx.api_profile)
    ReqModel = profile.lead_create_request_model()

    try:
        req_obj = ReqModel.model_validate(raw)
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ex),
        )

    canonical = profile.map_lead_create_to_canonical(ctx, req_obj)
    domain_resp = await LeadsService().create_lead(canonical)
    resp_obj = profile.shape_lead_create_response(ctx, domain_resp)
    return resp_obj
