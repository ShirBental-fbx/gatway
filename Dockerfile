# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_PROGRESS_BAR=off \
    PYTHONPATH=/app/src \
    GATEWAY_DEV_AUTH=true \
    GATEWAY_ROOT_PATH=/gateway/fastapi

WORKDIR /app

# If you have build-only deps (cryptography sometimes), keep this.
# If it works without, you can remove build-essential later.
# Disable broken APT post-invoke scripts in RDE
RUN set -eux; \
    rm -f /etc/apt/apt.conf.d/docker-clean /etc/apt/apt.conf.d/99no-postinvoke 2>/dev/null || true; \
    printf 'APT::Update::Post-Invoke { };\nAPT::Update::Post-Invoke-Success { };\nDPkg::Post-Invoke { };\nDPkg::Post-Invoke-Success { };\n' \
      > /etc/apt/apt.conf.d/99disable-postinvoke
RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates \
 && rm -rf /var/lib/apt/lists/*



# Install runtime deps directly (no building your project wheel)
COPY pyproject.toml ./
RUN python -m pip install --upgrade pip \
 && python -m pip install --no-cache-dir \
      "fastapi>=0.111.0" \
      "uvicorn>=0.30.0" \
      "pydantic>=2.0,<3" \
      "pydantic-settings>=2.0,<3" \
      "authlib>=1.3,<2.0" \
      "sqlalchemy>=2.0,<3.0" \
      "jinja2>=3.1.0" \
      "itsdangerous>=2.0" \
      "python-multipart>=0.0.9" \
      "email-validator>=2.0" \
      "httpx>=0.27.0"

COPY src ./src

EXPOSE 8001
CMD python -m uvicorn gateway.main:app --host 0.0.0.0 --port 8001 --proxy-headers --forwarded-allow-ips "*" --root-path /gateway/fastapi
