#!/bin/bash
# Sobe toda a infraestrutura e abre o navegador no OpenProject quando estiver pronto.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
URL="http://localhost:8090"

"$ROOT_DIR/start.sh" up

echo "Aguardando OpenProject responder em $URL..."
for _ in $(seq 1 60); do
  if curl -sf "$URL" >/dev/null; then
    break
  fi
  sleep 2
done

echo "Abrindo navegador em $URL..."
if command -v xdg-open >/dev/null 2>&1; then
  xdg-open "$URL" >/dev/null 2>&1 &
elif command -v open >/dev/null 2>&1; then
  open "$URL"
else
  echo "Não encontrei xdg-open/open. Acesse manualmente: $URL"
fi
