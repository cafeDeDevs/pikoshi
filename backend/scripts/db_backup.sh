#!/usr/bin/env bash

source .env

CURRENT_DATE=$(date +"%Y-%m-%d")

BACKUP_DIR="./db_backups"
BACKUP_FILE="${BACKUP_DIR}/pikoshi_backup_${CURRENT_DATE}.sql"

if [ ! -d "${BACKUP_DIR}" ]; then
    mkdir -p "$BACKUP_DIR"
fi

if [ -f "${BACKUP_FILE}" ]; then
    rm "${BACKUP_FILE}"
fi

docker exec -t -e POSTGRESPASSWORD="${PG_PASS}" "${PG_CONTAINER_NAME}" pg_dump -U "${PG_USER}" "${PG_DB}" >"${BACKUP_FILE}"
