#!/bin/bash
# Controla a stack do Nextcloud (nextcloud + nextcloud_db + nextcloud_redis).
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

case "${1:-}" in
  up)
    echo "Subindo Nextcloud..."
    docker compose up -d
    ;;
  down)
    echo "Parando Nextcloud..."
    docker compose down
    ;;
  logs)
    docker compose logs -f
    ;;
  *)
    echo "Uso: ./start.sh {up|down|logs}"
    exit 1
    ;;
esac
