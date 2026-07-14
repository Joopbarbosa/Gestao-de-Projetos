#!/bin/bash
# Controla toda a infraestrutura (OpenProject + Nextcloud + Postgres + Redis) a partir da raiz.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

case "${1:-}" in
  up)
    echo "Subindo toda a infraestrutura..."
    docker compose up -d
    ;;
  down)
    echo "Parando toda a infraestrutura..."
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
