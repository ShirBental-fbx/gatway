#!/usr/bin/env bash
set -euo pipefail

PYTHON_VERSION="${PYTHON_VERSION:-3.14.2}"
PORT="${PORT:-8001}"

exec uv run --python "$PYTHON_VERSION" python -m uvicorn gateway.main:app \
  --reload --port "$PORT" --app-dir src
