#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

echo "== Running backend validation =="
cd "$BACKEND_DIR"
source venv/bin/activate
python -m compileall .
pytest || true

echo "== Running frontend validation =="
cd "$FRONTEND_DIR"
npm run build

echo "Validation complete."
