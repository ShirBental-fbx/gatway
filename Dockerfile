# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_PROGRESS_BAR=off \
    GATEWAY_DEV_AUTH=true \
    GATEWAY_ROOT_PATH=/gateway/fastapi \
    PORT=8001

WORKDIR /app

# Disable broken APT post-invoke scripts in RDE
RUN set -eux; \
    rm -f /etc/apt/apt.conf.d/docker-clean /etc/apt/apt.conf.d/99no-postinvoke 2>/dev/null || true; \
    printf 'APT::Update::Post-Invoke { };\nAPT::Update::Post-Invoke-Success { };\nDPkg::Post-Invoke { };\nDPkg::Post-Invoke-Success { };\n' \
      > /etc/apt/apt.conf.d/99disable-postinvoke

RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Install uv (fast installer + lock support)
RUN python -m pip install --upgrade pip \
 && python -m pip install uv

# Copy dependency metadata first (better cache)
COPY pyproject.toml uv.lock README.md ./

# Install locked deps (system site-packages)
# --frozen: fail if lock doesn't match pyproject
# --no-dev: exclude dev group
RUN uv pip install --system -r requirements.txt

# Copy source
COPY src ./src

# Install the project itself into the environment
# --no-deps because deps already installed by uv sync
RUN uv pip install --system --no-deps .

EXPOSE 8001

CMD python -m uvicorn gateway.main:app \
  --host 0.0.0.0 --port ${PORT} \
  --proxy-headers --forwarded-allow-ips "*" \
  --root-path ${GATEWAY_ROOT_PATH}
