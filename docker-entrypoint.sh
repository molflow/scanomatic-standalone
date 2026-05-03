#!/bin/sh
set -e

python /opt/setup_config.py
exec "$@"