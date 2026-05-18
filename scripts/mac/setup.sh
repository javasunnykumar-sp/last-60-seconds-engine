#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

echo "== Last 60 Seconds Engine: macOS setup =="

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 is not installed or not on PATH."
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "ERROR: npm is not installed or not on PATH. Install Node.js first."
  exit 1
fi

echo "-- Setting up backend virtual environment"
cd "$BACKEND_DIR"
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "-- Creating backend .env if missing"
if [ ! -f "$BACKEND_DIR/.env" ]; then
  cat > "$BACKEND_DIR/.env" <<'ENV'
LM_STUDIO_BASE_URL=http://localhost:1234/v1
LM_STUDIO_API_KEY=lm-studio
MODEL_NAME=gemma-4
USE_MOCK_ANALYZE=False
ENV
  echo "Created backend/.env. Update MODEL_NAME if your LM Studio model id is different."
else
  echo "backend/.env already exists. Leaving it unchanged."
fi

echo "-- Installing frontend dependencies"
cd "$FRONTEND_DIR"
npm install

echo "-- Creating frontend .env if missing"
if [ ! -f "$FRONTEND_DIR/.env" ]; then
  cat > "$FRONTEND_DIR/.env" <<'ENV'
VITE_API_BASE_URL=http://127.0.0.1:8000
ENV
  echo "Created frontend/.env."
else
  echo "frontend/.env already exists. Leaving it unchanged."
fi

echo "Setup complete."
echo "Next: start LM Studio local server, then run: scripts/mac/run-all.sh"
