# Contract-First Migration Guide

This document describes how to generate and maintain contract-first FastAPI route definitions from the legacy Flask service.

## Overview

The migration process extracts all routes from the Flask app's runtime `url_map` and generates FastAPI router modules that:
- Define explicit route contracts (paths, methods) in FastAPI
- Proxy requests to the legacy Flask service
- Appear in OpenAPI/Swagger documentation
- Enable gradual migration to real Pydantic schemas

## Phase 1: Contract-First Skeletons (Current)

**Status**: Proxy-only handlers with no request/response schemas.

All generated routes:
- Accept `request: Request` (no Pydantic models)
- Forward requests byte-for-byte to Flask via `proxy_to_upstream()`
- Preserve exact Flask path, methods, and behavior

## Generating Routes

### Step 1: Export Flask Routes

Extract routes from the Flask app's runtime `url_map`:

```bash
# Set minimal environment variables (for route extraction only)
export API_FLASK_SESSION_SECRET_KEY=dummy-secret-for-route-export
export API_OAUTH_ENFORCE_SSL=false
export API_SQLALCHEMY_DATABASE_URI=sqlite:///:memory:

# Run export script
python legacy/scripts/export_routes.py
```

**Outputs**:
- `artifacts/flask_routes.json` - Machine-readable route inventory
- `artifacts/flask_routes.txt` - Human-readable route table

### Step 2: Generate FastAPI Routers

Generate FastAPI router modules from the inventory:

```bash
python legacy/scripts/generate_fastapi_routers.py
```

**Outputs**:
- `src/gateway/routers/legacy/*.py` - Generated router modules (one per group)
- `src/gateway/routers/legacy/__init__.py` - Module exports

**Grouping Strategy**:
- Routes are grouped by Flask blueprint name (if available)
- Otherwise grouped by first path segment (e.g., `/api/v1/...` → `api` group)

**Collision Handling**:
- Routes that conflict with gateway-specific endpoints are skipped:
  - `/health`
  - `/`
  - `/debug/*`
  - `/partners/{partner}/docs`
  - `/partners/{partner}/openapi.json`
- Collisions are logged during generation

### Step 3: Wire Routers into Gateway

Include generated routers in the FastAPI app:

```bash
python legacy/scripts/wire_routers.py
```

This updates `src/gateway/main.py` to import and include all legacy routers **before** the catch-all proxy router.

**Manual Alternative**:
If you prefer manual control, add to `src/gateway/main.py`:

```python
# After existing routers, before proxy router
from gateway.routers.legacy import *

app.include_router(router1_router)
app.include_router(router2_router)
# ... etc
```

## Re-running Generation

When Flask routes change:

1. **Re-export routes**:
   ```bash
   python legacy/scripts/export_routes.py
   ```

2. **Regenerate routers** (overwrites existing):
   ```bash
   python legacy/scripts/generate_fastapi_routers.py
   ```

3. **Re-wire routers** (if main.py was manually edited, review changes):
   ```bash
   python legacy/scripts/wire_routers.py
   ```

**Note**: Generated router files are marked with `DO NOT EDIT MANUALLY` comments. Any manual edits will be overwritten on regeneration.

## Route Ordering

FastAPI matches routes in registration order. The gateway ensures:

1. Gateway-specific routes (`/health`, `/debug/*`, etc.)
2. Explicit gateway routers (`leads_router`, `token_router`, etc.)
3. Partner docs (`/partners/{partner}/docs`)
4. **Generated legacy routers** (contract-first definitions)
5. **Catch-all proxy router** (fallback for undefined routes)

This ensures:
- Gateway routes take precedence
- Contract-first definitions are tried before fallback proxy
- Undefined routes still proxy to Flask

## Verification

### Smoke Test

Run the smoke test to verify routes are generated and accessible:

```bash
pytest src/gateway/test/test_legacy_routes.py -v
```

The test verifies:
- At least N routes appear in OpenAPI schema
- Sample routes exist and are callable
- Routes proxy correctly to upstream

### Manual Verification

1. **Check OpenAPI schema**:
   ```bash
   curl http://localhost:8000/openapi.json | jq '.paths | keys | length'
   ```

2. **View Swagger UI**:
   ```
   http://localhost:8000/docs
   ```
   Look for routes under "Legacy: *" tags.

3. **Test a sample route**:
   ```bash
   curl -X GET http://localhost:8000/api/v1/some-endpoint
   ```

## Next Steps (Future Phases)

### Phase 2: Add Request Schemas
- Replace `request: Request` with Pydantic models
- Validate request bodies before proxying
- Document request schemas in OpenAPI

### Phase 3: Add Response Schemas
- Define Pydantic response models
- Validate responses from Flask
- Document response schemas in OpenAPI

### Phase 4: Implement Business Logic
- Replace proxy handlers with real gateway logic
- Remove dependency on Flask service
- Complete migration

## Troubleshooting

### Export Script Fails

**Error**: `Failed to import Flask app`

**Solution**: 
- Verify `api__backup_20260114_1349/src/` exists and is accessible
- Check that required environment variables are set (even dummy values)
- Ensure Flask dependencies are available in Python path

### Generated Routes Don't Appear in OpenAPI

**Check**:
1. Routers are imported in `main.py`
2. Routers are included before proxy router
3. FastAPI app is running with correct root_path

### Routes Collide with Gateway Endpoints

**Solution**: 
- Review collision log during generation
- Manually exclude problematic routes in `generate_fastapi_routers.py`
- Or adjust gateway route paths if appropriate

### Routes Proxy but Return 404

**Check**:
1. `UPSTREAM_BASE_URL` is correctly configured
2. Flask service is running and accessible
3. Route path matches Flask exactly (check `artifacts/flask_routes.json`)

## Files Reference

- `legacy/scripts/export_routes.py` - Flask route extraction script
- `legacy/scripts/generate_fastapi_routers.py` - FastAPI router generator
- `legacy/scripts/wire_routers.py` - Helper to wire routers into main.py
- `artifacts/flask_routes.json` - Route inventory (JSON)
- `artifacts/flask_routes.txt` - Route inventory (human-readable)
- `src/gateway/routers/legacy/` - Generated router modules
- `src/gateway/test/test_legacy_routes.py` - Smoke tests
