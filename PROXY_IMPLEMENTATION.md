# Proxy Implementation Summary

## Overview

This implementation adds a reverse proxy with canary routing capabilities to the FastAPI Gateway. The proxy transparently forwards requests to an upstream API service while supporting controlled traffic splitting to a canary version.

## Implementation Details

### Phase 0: Transparent Pipe (Reverse Proxy)

**Files Created:**
- `src/gateway/proxy/__init__.py` - Module exports
- `src/gateway/proxy/client.py` - HTTP client management with httpx
- `src/gateway/proxy/handler.py` - Request forwarding logic
- `src/gateway/proxy/router.py` - FastAPI router with catch-all route
- `src/gateway/proxy/canary.py` - Canary routing configuration and logic

**Key Features:**
1. **Environment Variables:**
   - `UPSTREAM_BASE_URL` (required): Base URL for legacy/current upstream API
   - `UPSTREAM_CANARY_BASE_URL` (optional): Base URL for canary upstream API
   - `CANARY_CONFIG_PATH` (optional): Path to canary config file (default: `canary_config.json`)
   - `GATEWAY_DEBUG_PROXY` (optional): Enable debug headers in responses

2. **Request Forwarding:**
   - Preserves HTTP method, path, query parameters, and request body
   - Forwards request headers (excluding hop-by-hop headers)
   - Adds `X-Request-ID` (from `X-Correlation-Id` or generates new)
   - Adds `X-Forwarded-For`, `X-Forwarded-Proto`, `X-Forwarded-Host`
   - Adds gateway context headers: `X-Partner-Id`, `X-API-Profile`, `X-Client-Id`, `X-User-Id` (if available)

3. **HTTP Client:**
   - Uses `httpx.AsyncClient` with connection pooling
   - Explicit timeouts (connect: 10s, read: 30s, write: 10s, pool: 5s)
   - No retries by default (especially not for POST)
   - Supports streaming responses

### Phase 1: Controlled Canary Routing

**Canary Configuration:**
- File-based JSON configuration (`canary_config.json`)
- Rules support:
  - Partner matching (optional)
  - Endpoint pattern matching (prefix or regex)
  - HTTP method matching (optional)
  - Percentage-based routing (0-100, GET/HEAD only)
  - Idempotency requirement for non-GET methods

**Safety Rules:**
1. Default: All traffic goes to `UPSTREAM_BASE_URL`
2. Canary routing only enabled when `UPSTREAM_CANARY_BASE_URL` is set
3. Percentage-based routing applies **only** to GET/HEAD requests
4. POST/PUT/PATCH/DELETE require explicit rule match AND idempotency key (if `require_idempotency: true`)

**Example Config:**
```json
{
  "enabled": true,
  "rules": [
    {
      "partner": "nav",
      "endpoint_pattern": "/api/v1/leads",
      "method": "GET",
      "percentage": 10
    },
    {
      "partner": "nav",
      "endpoint_pattern": "/api/v1/webhooks",
      "method": "POST",
      "require_idempotency": true
    }
  ]
}
```

### Route Registration

The proxy router is registered **LAST** in `main.py` to avoid shadowing:
- `/health`
- `/debug/*`
- `/partners/{partner}/docs`
- `/partners/{partner}/openapi.json`

The catch-all route `/{full_path:path}` handles all other requests.

### Partner Docs Safety

- Partner Swagger UI already uses relative `openapi_url="openapi.json"` ✅
- Docs endpoints are registered before proxy router ✅
- Proxy route does not interfere with partner-specific routes ✅

## Testing

**Test Files:**
- `src/gateway/test/test_proxy.py` - Comprehensive tests for:
  - Canary routing logic
  - Config loading
  - Proxy forwarding (basic, with context, canary routing)

**Test Coverage:**
- Canary router decision logic
- Safety rules enforcement
- Config file loading (missing file, valid config)
- Proxy handler with mocked httpx client
- Request context extraction
- Header forwarding

## Documentation

**Updated Files:**
- `README.md` - Added proxy and canary routing documentation
- `UPSTREAM_EXPECTATIONS.md` - Summary of upstream API expectations
- `canary_config.json.example` - Example canary configuration

## Upstream Expectations Summary

Based on gateway codebase analysis:

**Required Headers:**
- `Authorization`: Bearer token (JWT) - forwarded as-is
- `X-Correlation-Id` or `X-Request-ID`: Request correlation identifier

**Context Headers (from Gateway JWT):**
- `X-Partner-Id`: Partner identifier
- `X-API-Profile`: API profile type (standard/legacy)
- `X-Client-Id`: OAuth client ID (if present)
- `X-User-Id`: User identifier (if present)

**Standard Proxy Headers:**
- `X-Forwarded-For`: Client IP
- `X-Forwarded-Proto`: Protocol (http/https)
- `X-Forwarded-Host`: Original host

**Idempotency:**
- Upstream may use `Idempotency-Key` or `X-Idempotency-Key` headers
- Canary routing for non-GET methods requires idempotency mechanism

## Usage

1. **Set environment variables:**
   ```bash
   export UPSTREAM_BASE_URL=https://current-api.internal
   export UPSTREAM_CANARY_BASE_URL=https://canary-api.internal  # Optional
   ```

2. **Create canary config (optional):**
   ```bash
   cp canary_config.json.example canary_config.json
   # Edit as needed
   ```

3. **Run gateway:**
   ```bash
   uv run uvicorn gateway.main:app --reload
   ```

4. **Test proxy:**
   ```bash
   curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/test
   ```

## Next Steps

- [ ] Integration testing with real upstream API
- [ ] Performance testing with high traffic
- [ ] Monitoring and alerting for canary routing
- [ ] Metrics collection (canary vs legacy traffic, latency, errors)
