#!/usr/bin/env bash
set -euo pipefail

cd /workspaces/scanomatic-standalone

export PYTHONPATH="/workspaces/scanomatic-standalone${PYTHONPATH:+:$PYTHONPATH}"
export PATH="/workspaces/scanomatic-standalone/scripts${PATH:+:$PATH}"

exec python3.9 scripts/scan-o-matic \
  --host 0.0.0.0 \
  --port 5000 \
  --no-browser
