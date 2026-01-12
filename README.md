# Gateway – FastAPI

Gateway service built with **FastAPI**, responsible for OAuth2 flows and shared
infrastructure such as database session handling, middleware, and core models.

---

## Tech Stack

- Python 3.14
- FastAPI
- Uvicorn
- SQLAlchemy
- Authlib
- uv (dependency & runtime management)

---

## Repository Structure


---

## Local Development

### Install dependencies

uv pip install -r requirements.txt --index-strategy unsafe-best-match

yaml
Copy code

Package indexes (internal and public) are configured in `uv.toml`.

---

### Run the service locally

uv run python -m uvicorn gateway.main:app
--reload
--port 8001
--app-dir src

arduino
Copy code

Service will be available at:

http://127.0.0.1:8001

yaml
Copy code

---

## OAuth2 Support

The gateway implements OAuth2 endpoints using **Authlib**, including:

- Authorization Code Grant
- Refresh Token Grant
- Token issuance
- Token revocation

OAuth2 data is persisted using SQLAlchemy models.

Integration with external authentication services (SDK or direct HTTP)
is intentionally decoupled and can be adapted per environment.

---

## Dependency Management

Source dependencies are defined in:

- `requirements.in`
- `requirements-fundbox.in` (optional / internal)

Locked dependencies are generated into:

- `requirements.txt`

To regenerate dependencies:

uv pip compile requirements.in -o requirements.txt --index-strategy unsafe-best-match

yaml
Copy code

---

## Development Guidelines

- Always use `uv run python` (do not use system Python)
- `.venv/` and IDE files are ignored by Git
- Keep commits small and scoped (scaffold, oauth2, db, config)

---

## Status

Work in progress.  
FastAPI migration and OAuth2 infrastructure are actively under development.
