#!/usr/bin/env bash
set -euo pipefail

URL="http://localhost:1234/v1/models"

echo "Checking LM Studio local API..."

if curl -s "$URL" >/dev/null; then
  echo "LM Studio API reachable at $URL"
  curl -s "$URL"
else
  echo "ERROR: LM Studio API not reachable."
  echo "Open LM Studio and start the OpenAI-compatible local server first."
  exit 1
fi
