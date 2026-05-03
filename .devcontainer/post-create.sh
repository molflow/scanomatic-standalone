#!/usr/bin/env bash
set -euo pipefail

# Ensure npm can clean and recreate dependency artifacts even if a previous run
# left root-owned files in the workspace.
fix_node_modules_permissions() {
  if [[ ! -e node_modules ]]; then
    return
  fi

  if [[ -w node_modules/.bin ]] || [[ ! -e node_modules/.bin ]]; then
    return
  fi

  echo "Fixing ownership for node_modules..."
  if command -v sudo >/dev/null 2>&1; then
    sudo chown -R "$(id -u):$(id -g)" node_modules
  else
    echo "sudo is unavailable; removing node_modules and reinstalling dependencies"
    rm -rf node_modules
  fi
}

if [[ -f package-lock.json ]]; then
  fix_node_modules_permissions
  npm ci
fi

uv sync --all-extra

echo "Devcontainer is ready."
echo "Run backend checks: uvx --with tox-uv tox -e lint,unit,integration"
echo "Run system tests: xvfb-run -a uvx --with tox-uv tox -e system"
echo "Run frontend checks: npm run lint && npm test"
