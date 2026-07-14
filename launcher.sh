#!/bin/bash
# Sobe toda a infraestrutura e abre o navegador no OpenProject e Nextcloud.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OP_URL="http://localhost:8090"
NC_URL="http://localhost:8091"

"$ROOT_DIR/start.sh" up

echo "Aguardando OpenProject responder em $OP_URL..."
while [ "$(curl -sL -o /dev/null -w '%{http_code}' $OP_URL)" != "200" ]; do
    sleep 3
done
echo "OpenProject OK."

echo "Aguardando Nextcloud responder em $NC_URL..."
while [ "$(curl -sL -o /dev/null -w '%{http_code}' $NC_URL)" != "200" ]; do
    sleep 3
done
echo "Nextcloud OK."

xdg-open "$OP_URL"
sleep 1
xdg-open "$NC_URL"