#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"

cd "$BACKEND_DIR"

if [ ! -d "venv" ]; then
  echo "Backend virtualenv not found. Run scripts/mac/setup.sh first."
  exit 1
fi

source venv/bin/activate

echo "Starting FastAPI backend on http://127.0.0.1:8000"
uvicorn main:app --reload --host 127.0.0.1 --port 8000
