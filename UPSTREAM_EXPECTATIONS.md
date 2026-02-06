# Upstream API Expectations

**Source**: Analysis of upstream API codebase (`api__backup_20260114_1349/src/`)

## Authentication

### OAuth2 (Primary Method)
- **Location**: `src/oauth2/__init__.py`
- **Implementation**: Uses Authlib's `ResourceProtector` with bearer token validator
- **Header Format**: `Authorization: Bearer <token>`
- **Code Reference**: 
  - Line 20: `require_oauth2 = ResourceProtector()`
  - Line 37-38: `bearer_cls = create_bearer_token_validator(api_db.session, OAuth2Token); require_oauth2.register_token_validator(bearer_cls())`
- **Usage**: Decorator `@require_oauth2()` applied to protected endpoints

### Partnership Authentication (Alternative)
- **Location**: `src/partnership/authentication_decorator.py`
- **Header Format**: `access_token: <token>` (NOT Authorization header)
- **Code Reference**: Line 33: `access_token = request.headers.get('access_token')`
- **Usage**: `Authenticator` class used as method decorator

### Basic Auth (Webhook Endpoints)
- **Location**: `src/webhooks/leads/authorization/authorization.py`
- **Header Format**: `Authorization: <base64_encoded_username:password>`
- **Code Reference**: Line 29: `auth_header = request.headers.get("Authorization", "")`
- **Usage**: `authorize_request()` decorator for partner-specific webhook endpoints

## Request ID / Correlation ID

### Header Name
- **Exact Header**: `request-id` (lowercase, hyphenated)
- **Location**: `src/common/FrontendAPI.py`
- **Code Reference**: Line 37: `headers = {"request-id": get_request_id()}`
- **Source Function**: `get_request_id()` from `fundbox.common.session.request_metadata`

### Automatic Generation
- **Location**: `src/Core.py`
- **Code Reference**: Line 47-48: `@app.before_request; def set_request_id_for_api_requests(): set_new_request_id()`
- **Source Function**: `set_new_request_id()` from `fundbox.common.session.request_metadata`
- **Behavior**: Request ID is automatically generated for every request via Flask before_request hook

### Gateway Compatibility Behavior
The gateway implements request ID bridging for compatibility:
- If incoming request has `x-request-id` (uppercase) but not `request-id` (lowercase), the gateway copies it to `request-id`
- If incoming request has `X-Correlation-Id` but neither `request-id` nor `x-request-id`, the gateway uses it as `request-id`
- If none of the above exist, the gateway generates a new `request-id` (UUID)
- The gateway always forwards `request-id` in upstream format (lowercase, hyphenated)

**Note**: The upstream API generates its own request ID automatically if missing. The gateway bridges common request ID header formats to the upstream format.

## Context Headers

### NOT FOUND IN UPSTREAM CODE
The following headers were NOT found in upstream codebase analysis:
- `X-Partner-Id` - **NOT FOUND**
- `X-API-Profile` - **NOT FOUND**
- `X-Client-Id` - **NOT FOUND**
- `X-User-Id` - **NOT FOUND**
- `X-Correlation-Id` - **NOT FOUND** (only `request-id` is used)

**Conclusion**: Gateway should NOT add these headers unless explicitly required by specific endpoints. Forward only headers that exist in the incoming request.

## Idempotency

### NOT FOUND IN UPSTREAM CODE
- Search for "idempotency" or "Idempotency" returned **ZERO matches** in upstream codebase
- No idempotency key headers found (`Idempotency-Key`, `X-Idempotency-Key`, etc.)
- **Conclusion**: Upstream API does NOT implement idempotency mechanisms. Canary routing for non-GET methods (POST/PUT/PATCH/DELETE) should be **BLOCKED** unless explicitly safe.

## Standard Proxy Headers

### X-Forwarded-* Headers
- **Location**: `src/fastapi_app/middleware/proxy_fix.py` (incomplete migration)
- **Original**: `src/common/utils/ECSFlaskProxyFix.py` (referenced but not in backup)
- **Behavior**: Upstream expects standard proxy headers for correct host/port/protocol detection
- **Code Reference**: `Core.py` line 51-55 shows `HTTP_HOST` and `SERVER_PORT` are set from request headers

## Response Headers

### No Special Requirements Found
- No specific response headers that must be preserved were found in upstream code
- Standard HTTP response headers should be forwarded as-is

## Streaming & Large Payloads

### NOT EXPLICITLY FOUND
- No explicit streaming endpoint patterns found in codebase analysis
- File uploads may exist but patterns not identified in this analysis
- **Recommendation**: Support streaming responses generically (do not buffer large payloads)

## Endpoint Patterns

### Webhook Endpoints
- **Location**: `src/webhooks/*/`
- **Pattern**: Various webhook handlers with partner-specific authentication
- **Example**: `src/webhooks/leads/BusinessLeads.py` uses `authorize_request()` decorator

### OAuth2 Endpoints
- **Location**: `src/oauth2/OAuth2API.py` (referenced in `FundboxAPI.py` line 8)
- **Pattern**: Standard OAuth2 authorization code flow endpoints

### Partner API Endpoints
- **Location**: `src/PartnerAPI.py` (referenced in `FundboxAPI.py` line 6)
- **Pattern**: Partner-specific resources with OAuth1 or partnership authentication

## Timeout-Sensitive Endpoints

### NOT EXPLICITLY FOUND
- No specific timeout requirements identified in codebase analysis
- Default HTTP client timeouts should be sufficient

## Summary

### Required Headers (Proven in Code)
1. **OAuth2**: `Authorization: Bearer <token>` (for OAuth2 protected endpoints)
   - Reference: `src/oauth2/__init__.py:20,37-38`
2. **Partnership**: `access_token: <token>` (for partnership endpoints)
   - Reference: `src/partnership/authentication_decorator.py:33`
3. **Request ID**: `request-id: <id>` (forwarded, but upstream generates if missing)
   - Reference: `src/common/FrontendAPI.py:37`, `src/Core.py:47-48`

### Headers NOT Found (Do NOT Add)
- `X-Partner-Id` - NOT FOUND
- `X-API-Profile` - NOT FOUND
- `X-Client-Id` - NOT FOUND
- `X-User-Id` - NOT FOUND
- `X-Correlation-Id` - NOT FOUND (use `request-id` instead)
- Any idempotency headers - NOT FOUND

### Idempotency
- **Status**: NOT IMPLEMENTED in upstream
- **Implication**: Canary routing for POST/PUT/PATCH/DELETE should be BLOCKED (no safe retry mechanism)
