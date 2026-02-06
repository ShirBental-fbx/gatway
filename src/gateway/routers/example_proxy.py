"""
Example router showing contract-first proxy pattern.

This demonstrates how to define explicit FastAPI endpoints with schemas
that proxy to the upstream Flask service.

IMPORTANT TRADEOFF:
- Using Pydantic models: Request body is parsed/validated, then serialized via
  model_dump(). This may change the byte representation (key ordering, formatting).
- For byte-preserving forwarding: Accept Request only, don't use Pydantic Body().
"""

from __future__ import annotations

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field
from starlette.responses import Response

from gateway.proxy.endpoint import proxy_to_upstream

router = APIRouter()


# Example: Define request/response schemas
class LeadCreateRequest(BaseModel):
    """Request schema for creating a lead."""
    business_id: str = Field(..., description="Business identifier")
    email: str = Field(..., description="Contact email")
    amount: float = Field(..., gt=0, description="Requested amount")


class LeadResponse(BaseModel):
    """Response schema for lead creation."""
    lead_id: str = Field(..., description="Created lead ID")
    status: str = Field(..., description="Lead status")


# Example 1: Endpoint WITH Pydantic validation (body may be reformatted)
@router.post(
    "/api/v1/leads",
    tags=["Example"],
    response_model=LeadResponse,
    summary="Create a new lead (with validation)",
    description=(
        "Creates a new lead with request validation. "
        "NOTE: Body is parsed and re-serialized, so byte representation may differ from original."
    ),
)
async def create_lead_with_validation(
    request: Request,
    body: LeadCreateRequest,
) -> Response:
    """
    Create a new lead with Pydantic validation.
    
    Tradeoff: Request body is validated and re-serialized, so forwarded body
    may differ byte-for-byte from original (e.g., key ordering, whitespace).
    """
    # Proxy to upstream Flask service
    # The request body has been validated and will be re-serialized by FastAPI
    response = await proxy_to_upstream(
        request=request,
        upstream_path="/api/v1/leads",
    )
    return response


# Example 2: Endpoint WITHOUT Pydantic validation (byte-preserving)
@router.post(
    "/api/v1/leads-raw",
    tags=["Example"],
    summary="Create a new lead (byte-preserving)",
    description=(
        "Creates a new lead with byte-preserving forwarding. "
        "Request body is forwarded exactly as received (no parsing/re-serialization)."
    ),
)
async def create_lead_raw(request: Request) -> Response:
    """
    Create a new lead with byte-preserving forwarding.
    
    Tradeoff: No request validation, but body is forwarded byte-for-byte.
    Use this when exact body preservation is required.
    """
    # Proxy to upstream Flask service
    # Request body is forwarded exactly as received (no Pydantic parsing)
    response = await proxy_to_upstream(
        request=request,
        upstream_path="/api/v1/leads",
    )
    return response


# Example: GET endpoint with query parameters
@router.get(
    "/api/v1/leads/{lead_id}",
    tags=["Example"],
    response_model=LeadResponse,
    summary="Get lead by ID",
)
async def get_lead(
    request: Request,
    lead_id: str,
) -> Response:
    """
    Get a lead by its ID.
    
    GET requests don't have body, so no byte-preservation tradeoff.
    """
    response = await proxy_to_upstream(
        request=request,
        upstream_path=f"/api/v1/leads/{lead_id}",
    )
    return response


# Example: Endpoint without explicit response model (for flexibility)
@router.get(
    "/api/v1/leads",
    tags=["Example"],
    summary="List all leads",
)
async def list_leads(request: Request) -> Response:
    """
    List all leads.
    
    No response_model means FastAPI won't validate response,
    but it will still appear in OpenAPI docs.
    """
    response = await proxy_to_upstream(
        request=request,
        upstream_path="/api/v1/leads",
    )
    return response
