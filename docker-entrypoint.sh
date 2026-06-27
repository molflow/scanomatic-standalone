#!/bin/sh
set -e

mkdir -p /root/.scan-o-matic/config
# Copy default config recursively without overwriting existing user config
cp -an /tmp/data/config/. /root/.scan-o-matic/config/

exec "$@"