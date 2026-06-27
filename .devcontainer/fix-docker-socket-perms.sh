#!/usr/bin/env bash
set -euo pipefail

CURRENT_USER="$(id -un)"

# Align the container user with the mounted docker socket GID.
if [[ ! -S /var/run/docker.sock ]]; then
  echo "No docker socket mount found; skipping docker group alignment."
  exit 0
fi

SOCK_GID="$(stat -c '%g' /var/run/docker.sock)"
EXISTING_GROUP="$(getent group "${SOCK_GID}" | cut -d: -f1 || true)"
TARGET_GROUP="${EXISTING_GROUP:-dockerhost}"

if [[ -z "${EXISTING_GROUP}" ]]; then
  sudo groupadd --gid "${SOCK_GID}" "${TARGET_GROUP}"
fi

if id -nG "${CURRENT_USER}" | grep -qw "${TARGET_GROUP}"; then
  echo "User ${CURRENT_USER} already belongs to ${TARGET_GROUP}."
else
  sudo usermod -aG "${TARGET_GROUP}" "${CURRENT_USER}"
  echo "Added ${CURRENT_USER} to ${TARGET_GROUP}."
  echo "Rebuild/Reopen once more if docker commands still fail due to cached session groups."
fi
