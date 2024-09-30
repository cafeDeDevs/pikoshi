#!/usr/bin/env bash

source .env

CURRENT_DATE=$(date +"%Y-%m-%d")
BACKUP_DIR="./db_backups"
BACKUP_FILE="./db_backups/pikoshi_backup_${CURRENT_DATE}.sql"

if [ ! -d "${BACKUP_DIR}" ]; then
    echo "Backup directory does not exist: ${BACKUP_DIR}"
    exit 1
fi

if [ ! -f "${BACKUP_FILE}" ]; then
    echo "Backup file does not exist: ${BACKUP_FILE}"
    exit 1
fi

docker exec -i "${PG_CONTAINER_NAME}" psql -U "${PG_USER}" -d "${PG_DB}" <"${BACKUP_FILE}"
