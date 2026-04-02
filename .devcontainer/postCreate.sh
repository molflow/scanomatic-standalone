#!/usr/bin/env bash
set -euo pipefail

cd /workspaces/scanomatic-standalone

python3.9 -m pip install --upgrade pip
python3.9 -m pip install -r requirements.txt

npm ci
npm run build
