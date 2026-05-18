#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

osascript <<EOF
 tell application "Terminal"
   do script "cd '$ROOT_DIR' && bash scripts/mac/check-lmstudio.sh"
   do script "cd '$ROOT_DIR' && bash scripts/mac/run-backend.sh"
   do script "cd '$ROOT_DIR' && bash scripts/mac/run-frontend.sh"
   activate
 end tell
EOF

echo "Launched LM Studio check, backend, and frontend in separate Terminal tabs/windows."
