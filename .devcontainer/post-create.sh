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

# npm cache may be persisted from previous runs as root-owned files.
# Ensure npm can create cache and log directories before npm ci.
fix_npm_cache_permissions() {
  local npm_cache_dir="${NPM_CONFIG_CACHE:-$HOME/.npm}"

  if [[ ! -e "${npm_cache_dir}" ]]; then
    return
  fi

  if [[ -w "${npm_cache_dir}" ]]; then
    return
  fi

  echo "Fixing ownership for npm cache at ${npm_cache_dir}..."
  if command -v sudo >/dev/null 2>&1; then
    sudo chown -R "$(id -u):$(id -g)" "${npm_cache_dir}"
  else
    echo "sudo is unavailable; using a local npm cache for this run"
    export NPM_CONFIG_CACHE="$PWD/.npm-cache"
    mkdir -p "${NPM_CONFIG_CACHE}"
  fi
}

fix_uv_cache_permissions() {
  local uv_cache_dir="${UV_CACHE_DIR:-$HOME/.cache/uv}"

  if [[ ! -e "${uv_cache_dir}" ]]; then
    return
  fi

  if [[ -w "${uv_cache_dir}" ]]; then
    return
  fi

  echo "Fixing ownership for uv cache at ${uv_cache_dir}..."
  if command -v sudo >/dev/null 2>&1; then
    sudo chown -R "$(id -u):$(id -g)" "${uv_cache_dir}"
  else
    echo "sudo is unavailable; using a local uv cache for this run"
    export UV_CACHE_DIR="$PWD/.uv-cache"
    mkdir -p "${UV_CACHE_DIR}"
  fi
}

if [[ -f package-lock.json ]]; then
  fix_npm_cache_permissions
  fix_node_modules_permissions
  npm ci
  npm run build
fi

fix_uv_cache_permissions
uv sync --all-extras

# Keep Scan-o-Matic developer data in-repo for easy persistence and inspection.
som_data_dir="${SCANOMATIC_DATA:-$PWD/.scan-o-matic}"
if [[ "$som_data_dir" == *'${'* ]]; then
  # Guard against unresolved devcontainer placeholders (e.g. ${workspaceFolder}).
  som_data_dir="$PWD/.scan-o-matic"
fi
som_projects_root="$PWD/somprojects"
mkdir -p "$som_data_dir/config" "$som_projects_root"

# Ensure the app's settings model points projects to the in-repo location.
SCANOMATIC_DATA="$som_data_dir" uv run python - <<'PY'
import os
from scanomatic.io.app_config import Config

cfg = Config()
cfg.paths.projects_root = os.path.abspath("somprojects")
cfg.save_current_settings()
PY

echo "Devcontainer is ready."
echo "Run backend checks: uvx --with tox-uv tox -e lint,unit,integration"
echo "Run system tests: xvfb-run -a uvx --with tox-uv tox -e system"
echo "Run frontend checks: npm run lint && npm test"
