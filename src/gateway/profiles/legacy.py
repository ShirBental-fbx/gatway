from __future__ import annotations

from pydantic import BaseModel, Field

from gateway.context.request_context import RequestContext
from gateway.profiles.base import ApiProfile


class LegacyLeadCreateRequest(BaseModel):
    businessId: str
    email: str
    requestedAmount: str = Field(min_length=1)


class LegacyLeadCreateResponse(BaseModel):
    id: str
    state: str


class LegacyProfile(ApiProfile):
    name = "legacy"

    def lead_create_request_model(self):
        return LegacyLeadCreateRequest

    def lead_create_response_model(self):
        return LegacyLeadCreateResponse

    def map_lead_create_to_canonical(self, ctx: RequestContext, req: LegacyLeadCreateRequest) -> dict:
        return {
            "business_id": req.businessId,
            "email": req.email,
            "amount": int(req.requestedAmount),
        }

    def shape_lead_create_response(self, ctx: RequestContext, domain_resp: dict) -> LegacyLeadCreateResponse:
        return LegacyLeadCreateResponse(
            id=domain_resp["lead_id"],
            state=domain_resp["status"],
        )
