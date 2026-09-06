#!/usr/bin/env bash
set -euo pipefail

CONTAINER="openproject_local"
DB_NAME="openproject"
BACKUP_DIR="$(cd "$(dirname "$0")" && pwd)/backups"
LOG="$BACKUP_DIR/backup.log"

mkdir -p "$BACKUP_DIR"
log() { echo "[$(date '+%F %T')] $1" >> "$LOG"; }
trap 'log "ERRO: backup falhou (linha $LINENO)"' ERR

log "Iniciando backup..."

docker exec "$CONTAINER" su postgres -c "pg_dump -Fc $DB_NAME" > "$BACKUP_DIR/openproject.dump.tmp"
docker exec "$CONTAINER" tar czf - -C /var/openproject assets files > "$BACKUP_DIR/openproject_files.tar.gz.tmp"

mv "$BACKUP_DIR/openproject.dump.tmp" "$BACKUP_DIR/openproject.dump"
mv "$BACKUP_DIR/openproject_files.tar.gz.tmp" "$BACKUP_DIR/openproject_files.tar.gz"

log "Backup concluído com sucesso ($(du -h "$BACKUP_DIR/openproject.dump" | cut -f1) + $(du -h "$BACKUP_DIR/openproject_files.tar.gz" | cut -f1))."
