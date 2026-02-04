from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field

from gateway.context.request_context import RequestContext
from gateway.profiles.base import ApiProfile


class StandardLeadCreateRequest(BaseModel):
    business_id: str
    email: EmailStr
    amount: int = Field(ge=1)


class StandardLeadCreateResponse(BaseModel):
    lead_id: str
    status: str


class StandardProfile(ApiProfile):
    name = "standard"

    def lead_create_request_model(self):
        return StandardLeadCreateRequest

    def lead_create_response_model(self):
        return StandardLeadCreateResponse

    def map_lead_create_to_canonical(self, ctx: RequestContext, req: StandardLeadCreateRequest) -> dict:
        return {
            "business_id": req.business_id,
            "email": str(req.email),
            "amount": req.amount,
        }

    def shape_lead_create_response(self, ctx: RequestContext, domain_resp: dict) -> StandardLeadCreateResponse:
        return StandardLeadCreateResponse(**domain_resp)
