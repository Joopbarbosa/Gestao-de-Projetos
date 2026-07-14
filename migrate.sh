#!/bin/bash
# Migração segura: OpenProject standalone (./OpenProject) -> stack unificada na raiz.
# Faz backup lógico do banco do OpenProject, para o container antigo, move
# ./OpenProject/data para ./data preservando pgdata/assets/files, cria as pastas
# novas (nextcloud_pgdata, nextcloud) e sobe a stack unificada.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OLD_DATA_DIR="$ROOT_DIR/OpenProject/data"
NEW_DATA_DIR="$ROOT_DIR/data"
BACKUP_DIR="$ROOT_DIR/backups"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"

cd "$ROOT_DIR"

echo "== Migração: OpenProject standalone -> Infraestrutura unificada =="
echo "Diretório raiz: $ROOT_DIR"
read -r -p "Isso vai parar o container openproject_local e mover os dados. Continuar? [s/N] " CONFIRM
if [[ ! "$CONFIRM" =~ ^[sS]$ ]]; then
  echo "Abortado."
  exit 1
fi

# 1) Backup lógico do banco do OpenProject (se o container ainda estiver rodando)
mkdir -p "$BACKUP_DIR"
if docker ps --format '{{.Names}}' | grep -qx 'openproject_local'; then
  echo "-> Fazendo backup lógico do banco do OpenProject..."
  docker exec openproject_local bash -c \
    'PGPASSWORD=openproject pg_dump -h 127.0.0.1 -U openproject -d openproject' \
    > "$BACKUP_DIR/openproject_${TIMESTAMP}.sql"
  echo "   Backup salvo em: $BACKUP_DIR/openproject_${TIMESTAMP}.sql"
else
  echo "-> Container openproject_local não está rodando; pulando backup lógico."
fi

# 2) Parar/remover o container antigo (dados no bind mount continuam intactos em disco)
if docker ps -a --format '{{.Names}}' | grep -qx 'openproject_local'; then
  echo "-> Parando container openproject_local..."
  docker stop openproject_local >/dev/null
  docker rm openproject_local >/dev/null
fi

# 3) Mover os dados de OpenProject/data para data/ na raiz (precisa de sudo por causa do pgdata)
if [ -d "$NEW_DATA_DIR" ]; then
  echo "-> $NEW_DATA_DIR já existe, pulando etapa de mudança de pasta."
elif [ -d "$OLD_DATA_DIR" ]; then
  echo "-> Movendo $OLD_DATA_DIR para $NEW_DATA_DIR (peço sudo aqui, pgdata pertence ao container)..."
  sudo mv "$OLD_DATA_DIR" "$NEW_DATA_DIR"
  sudo chown "$(id -u):$(id -g)" "$NEW_DATA_DIR"
else
  echo "ERRO: nem $OLD_DATA_DIR nem $NEW_DATA_DIR existem. Abortando." >&2
  exit 1
fi

# 4) Garantir estrutura de pastas completa
echo "-> Garantindo estrutura de pastas em $NEW_DATA_DIR..."
mkdir -p "$NEW_DATA_DIR/files" "$NEW_DATA_DIR/pgdata" "$NEW_DATA_DIR/assets"
mkdir -p "$NEW_DATA_DIR/nextcloud_pgdata" "$NEW_DATA_DIR/nextcloud"

# 5) Subir a stack unificada
echo "-> Subindo a stack unificada (docker compose up -d)..."
docker compose up -d

# 6) Esperar os serviços responderem
wait_http() {
  local url="$1" name="$2"
  echo "-> Aguardando $name responder em $url..."
  for _ in $(seq 1 30); do
    if curl -sf "$url" >/dev/null; then
      echo "   $name OK."
      return 0
    fi
    sleep 5
  done
  echo "   AVISO: $name não respondeu a tempo. Verifique 'docker compose logs'." >&2
}
wait_http "http://localhost:8090" "OpenProject"
wait_http "http://localhost:8091" "Nextcloud"

# 7) Configurar o Nextcloud para indexar os arquivos do OpenProject (external storage local)
echo "-> Configurando integração Nextcloud <-> arquivos do OpenProject..."
docker exec --user www-data nextcloud_app php occ app:enable files_external >/dev/null 2>&1 || true
if ! docker exec --user www-data nextcloud_app php occ files_external:list --output=json 2>/dev/null | grep -q "OpenProject Files"; then
  docker exec --user www-data nextcloud_app php occ files_external:create \
    "OpenProject Files" local null::null -c datadir=/mnt/openproject_files || \
    echo "   AVISO: não foi possível criar o external storage automaticamente. Configure manualmente em Configurações > Armazenamentos externos." >&2
fi

echo ""
echo "== Migração concluída =="
echo "OpenProject: http://localhost:8090"
echo "Nextcloud:   http://localhost:8091 (usuário: $(grep NEXTCLOUD_ADMIN_USER .env | cut -d= -f2))"
echo "Backup do banco (se gerado): $BACKUP_DIR/openproject_${TIMESTAMP}.sql"
