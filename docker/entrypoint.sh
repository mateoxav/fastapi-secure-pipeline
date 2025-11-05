#!/usr/bin/env bash
set -euo pipefail

if [[ "${AUTO_MIGRATE:-false}" == "true" ]]; then
  echo "[entrypoint] Applying DB migrations..."
  python scripts/migrate.py
fi

exec "$@"