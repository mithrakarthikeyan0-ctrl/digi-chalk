#!/usr/bin/env bash
# script/backup_db.sh
# Performs a pg_dump on the Digichalk PostgreSQL database.
# Ensure you have docker-compose running.

set -e

BACKUP_DIR="./backups"
mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/digichalk_backup_${TIMESTAMP}.sql"

echo "Creating backup: ${BACKUP_FILE}"

# Execute pg_dump inside the running db container
docker-compose exec -T db pg_dump -U postgres digichalk > "$BACKUP_FILE"

echo "Backup completed successfully."
