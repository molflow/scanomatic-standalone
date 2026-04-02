#!/usr/bin/env bash
set -euo pipefail

CONFIG_SRC="/workspaces/scanomatic-standalone/data/config"
CONFIG_DST="${SOM_SETTINGS:-/root/.scan-o-matic}/config"

mkdir -p "$CONFIG_DST"
cp -n "$CONFIG_SRC"/* "$CONFIG_DST"/ 2>/dev/null || true
mkdir -p "${SOM_PROJECTS_ROOT:-/somprojects}"
