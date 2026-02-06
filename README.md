# Gateway API

OAuth2 Gateway API built with FastAPI, Python 3.14, and uv.

## Overview

This service provides OAuth2 authorization server functionality, migrated from the Flask-based implementation in the legacy `api` project.

## Features

- **OAuth2 Authorization Code Flow** with PKCE support
- **Refresh Token Grant** for token renewal
- **Token Revocation** (RFC 7009)
- **Reverse Proxy** to upstream API with transparent forwarding
- **Canary Routing** for controlled traffic splitting to new upstream versions
- Pure SQLAlchemy models (no Flask-SQLAlchemy dependency)
- FastAPI with async support
- Authlib integration for OAuth2 compliance

## Requirements

- Python 3.14+
- uv (package manager)

## Quick Start

### 1. Install uv (if not already installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Set up the project

```bash
cd ~/fundbox/new_api/gateway

# Create virtual environment and install dependencies
uv sync

# Or with development dependencies
uv sync --dev
```

### 3. Configure environment

Create a `.env` file or set environment variables:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/gateway

# Optional: Enable SQL logging
SQL_ECHO=false

# Upstream API (required for proxy functionality)
UPSTREAM_BASE_URL=https://current-api.internal

# Optional: Canary upstream API (enables canary routing)
UPSTREAM_CANARY_BASE_URL=https://canary-api.internal

# Optional: Canary config file path (defaults to canary_config.json)
CANARY_CONFIG_PATH=canary_config.json

# Optional: Enable debug headers (X-Gateway-Upstream)
GATEWAY_DEBUG_PROXY=false
```

### 4. Run the development server

```bash
./run_dev.sh

# Or manually:
uv run uvicorn gateway.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Access the API

- API docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/health

## Project Structure

```
gateway/
├── pyproject.toml          # Project configuration (uv/pip)
├── run_dev.sh              # Development server script
├── src/
│   └── gateway/
│       ├── __init__.py
│       ├── main.py         # FastAPI application entry point
│       ├── db/
│       │   ├── base.py     # SQLAlchemy declarative base
│       │   ├── context.py  # DB context for request scope
│       │   └── session.py  # Session management
│       ├── errors/
│       │   ├── exceptions.py
│       │   └── handlers.py
│       ├── middleware/
│       │   └── db/
│       │       └── db_session.py
│       ├── models/
│       │   ├── oauth2_client.py
│       │   ├── oauth2_token.py
│       │   └── oauth2_authorization_code.py
│       ├── oauth2/
│       │   ├── __init__.py
│       │   ├── asgi_request.py        # ASGI/Authlib adapter
│       │   ├── authorization_code_grant.py
│       │   ├── oauth2_manager.py      # Client management
│       │   ├── refresh_token_grant.py
│       │   ├── router.py              # OAuth2 endpoints
│       │   ├── server.py              # Authorization server config
│       │   ├── storage.py             # Token/client storage
│       │   └── token_router.py        # External auth service endpoints
│       ├── routers/
│       │   └── debug.py
│       └── templates/
│           └── authorize.html
└── tests/
```

## OAuth2 Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/oauth/authorize` | GET | Display authorization consent page |
| `/oauth/authorize` | POST | Process user consent, issue auth code |
| `/oauth/token` | POST | Exchange auth code for tokens |
| `/oauth/revoke` | POST | Revoke access or refresh token |
| `/oauth/external/token` | POST | Token via external auth service |
| `/oauth/external/revoke` | POST | Revoke via external auth service |

## Development

### Running tests

```bash
uv run pytest
```

### Linting

```bash
uv run ruff check src/
uv run ruff format src/
```

### Adding dependencies

```bash
# Add a runtime dependency
uv add <package>

# Add a dev dependency
uv add --dev <package>
```

## Reverse Proxy & Canary Routing

The gateway acts as a reverse proxy to the upstream API service, forwarding all requests that don't match gateway-specific routes (like `/health`, `/debug/*`, `/partners/{partner}/docs`).

### Configuration

**Required:**
- `UPSTREAM_BASE_URL`: Base URL for the legacy/current upstream API (e.g., `https://current-api.internal`)

**Optional:**
- `UPSTREAM_CANARY_BASE_URL`: Base URL for canary upstream API. If unset, canary routing is disabled.
- `CANARY_CONFIG_PATH`: Path to canary configuration file (defaults to `canary_config.json`)
- `GATEWAY_DEBUG_PROXY`: Set to `true` to add `X-Gateway-Upstream` header to responses

### Canary Configuration

Canary routing allows you to gradually route traffic to a new upstream version. Create a `canary_config.json` file:

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
      "partner": "intuit",
      "endpoint_pattern": "^/api/v1/.*",
      "method": "GET",
      "percentage": 5
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

**Rule Fields:**
- `partner`: Partner ID to match (optional, matches all if omitted)
- `endpoint_pattern`: Path pattern - supports prefix (e.g., `/api/v1/leads`) or regex (e.g., `^/api/v1/.*`)
- `method`: HTTP method (optional, matches all if omitted)
- `percentage`: Percentage of traffic to route to canary (0-100, GET/HEAD only)
- `require_idempotency`: Require idempotency key header for non-GET methods (default: false)

**Safety Rules:**
- Default: All traffic goes to `UPSTREAM_BASE_URL`
- Canary routing only works when `UPSTREAM_CANARY_BASE_URL` is set
- Percentage-based routing applies **only** to GET/HEAD requests (idempotent)
- For POST/PUT/PATCH/DELETE: Canary routing requires explicit rule match AND idempotency key header (if `require_idempotency: true`)

**Example:**
```bash
# Copy example config
cp canary_config.json.example canary_config.json

# Edit as needed
vim canary_config.json
```

### Request Forwarding

The proxy forwards:
- HTTP method, path, query parameters, and request body
- Request headers (excluding hop-by-hop headers)
- Adds `X-Request-ID` (from `X-Correlation-Id` or generates new)
- Adds `X-Forwarded-For`, `X-Forwarded-Proto`, `X-Forwarded-Host`
- Adds gateway context headers: `X-Partner-Id`, `X-API-Profile`, `X-Client-Id`, `X-User-Id` (if available)

### Local Testing

To test the proxy locally:

```bash
# Set upstream to a test server
export UPSTREAM_BASE_URL=http://localhost:8001

# Run gateway
uv run uvicorn gateway.main:app --reload --host 0.0.0.0 --port 8000

# Test proxy forwarding
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/test
```

## Migration from Flask

This project was migrated from the Flask-based `api/src/oauth2` module. Key changes:

1. **Flask-SQLAlchemy → Pure SQLAlchemy**: Models use `DeclarativeBase` and `mapped_column`
2. **Flask routes → FastAPI routers**: Using `APIRouter` with Pydantic validation
3. **Werkzeug → secrets**: Using stdlib `secrets` module for token generation
4. **Request handling**: Custom `ASGIOAuthRequest` adapter for Authlib compatibility
5. **Context-based sessions**: Using `contextvars` for request-scoped DB sessions
6. **Reverse proxy**: Added transparent proxy with canary routing support

# Build and Run 
docker build -t gateway-fastapi .
docker rm -f gateway-fastapi 2>/dev/null || true
docker run -d \
  --name gateway-fastapi \
  -p 8002:8001 \
  gateway-fastapi
