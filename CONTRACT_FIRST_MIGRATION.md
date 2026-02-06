# Contract-First Migration Guide

## Overview

The FastAPI Gateway uses a **contract-first** approach where all endpoints are explicitly defined with Pydantic schemas, while runtime implementation proxies to the legacy Flask service.

## Principles

1. **Explicit Route Definitions**: Every endpoint must be defined in FastAPI with path, method, and schemas
2. **Pydantic Models**: Request/response schemas defined using Pydantic for validation and OpenAPI docs
3. **Proxy Implementation**: Endpoint handlers forward requests to upstream Flask service
4. **OpenAPI Generation**: FastAPI automatically generates OpenAPI spec from route definitions
5. **Partner Policy Filtering**: PartnerPolicy filters work on explicitly defined routes
6. **Catch-All Fallback**: Undefined routes fall back to catch-all proxy (for gradual migration)

## Pattern

### Basic Proxy Endpoint

```python
from fastapi import APIRouter, Request
from pydantic import BaseModel
from starlette.responses import Response
from gateway.proxy.endpoint import proxy_to_upstream

router = APIRouter()

class MyRequest(BaseModel):
    field: str

class MyResponse(BaseModel):
    result: str

# IMPORTANT: Set tags, summary, response_model on the decorator
@router.post(
    "/api/v1/my-endpoint",
    tags=["MyTag"],
    summary="My endpoint",
    description="Endpoint description for OpenAPI docs",
    response_model=MyResponse,
)
async def my_endpoint(request: Request, body: MyRequest) -> Response:
    """Endpoint implementation."""
    response = await proxy_to_upstream(
        request=request,
        upstream_path="/api/v1/my-endpoint",
    )
    return response
```

### Key Points

1. **Request Validation**: FastAPI validates request body against `MyRequest` schema before proxying
2. **Response Schema**: `response_model=MyResponse` is for OpenAPI docs only; actual response comes from upstream
3. **Proxy Function**: `proxy_to_upstream()` is a thin wrapper over `proxy_handler()` - reuses same implementation and shared httpx client
4. **Tags**: Use tags for PartnerPolicy filtering (e.g., `tags=["Leads"]`)

### Important Tradeoff: Pydantic Models vs Byte-Preservation

**With Pydantic Models (Validation Enabled):**
```python
@router.post("/api/v1/leads", response_model=LeadResponse)
async def create_lead(request: Request, body: LeadCreateRequest) -> Response:
    return await proxy_to_upstream(request, "/api/v1/leads")
```
- ✅ Request validation before proxying
- ✅ Type safety and better error messages
- ❌ Body is parsed and re-serialized via `model_dump()`
- ❌ Byte representation may differ (key ordering, formatting, whitespace)

**Without Pydantic Models (Byte-Preserving):**
```python
@router.post("/api/v1/leads")
async def create_lead(request: Request) -> Response:
    return await proxy_to_upstream(request, "/api/v1/leads")
```
- ✅ Body forwarded byte-for-byte exactly as received
- ✅ No parsing/re-serialization overhead
- ❌ No request validation
- ❌ No type safety

**Recommendation**: Use Pydantic models unless you have a specific requirement for byte-preservation (e.g., signed payloads, exact formatting requirements).

## Migration Strategy

### Phase 1: Define High-Priority Endpoints
- Start with most-used endpoints
- Define schemas based on actual request/response patterns
- Add to appropriate router modules

### Phase 2: Gradual Expansion
- Add endpoints as they're needed
- Use catch-all proxy for undefined routes
- Monitor which routes hit catch-all to prioritize

### Phase 3: Complete Migration
- Eventually all routes should be explicitly defined
- Catch-all proxy becomes true fallback for edge cases

## Example: Leads Endpoint

See `src/gateway/routers/example_proxy.py` for a complete example.

## Benefits

1. **OpenAPI Documentation**: Automatic API docs from code
2. **Request Validation**: Invalid requests rejected before reaching upstream
3. **Type Safety**: Pydantic models provide type hints and validation
4. **Partner Filtering**: PartnerPolicy can filter by tags
5. **Gradual Migration**: Can migrate endpoints one at a time
6. **Contract as Code**: API contract is version-controlled code

## File Organization

```
src/gateway/
├── routers/
│   ├── leads.py          # Lead-related endpoints
│   ├── webhooks.py       # Webhook endpoints
│   └── ...
├── models/
│   ├── leads.py          # Lead Pydantic models
│   └── ...
└── proxy/
    ├── endpoint.py       # proxy_to_upstream helper
    └── ...
```

## Best Practices

1. **Group Related Endpoints**: Use separate router files per domain
2. **Reuse Models**: Define shared Pydantic models in `models/` directory
3. **Document Schemas**: Add Field descriptions for better OpenAPI docs
4. **Use Tags**: Tag endpoints for PartnerPolicy filtering
5. **Validate Early**: Let FastAPI validate before proxying
6. **Keep Proxy Simple**: Don't add business logic in proxy endpoints
