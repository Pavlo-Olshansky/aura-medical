#!/bin/sh
set -e

BACKUP_DIR="/backups"
KEEP_LOCAL="${BACKUP_KEEP_LOCAL:-30}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
FILENAME="medtracker_${TIMESTAMP}.dump"
FILEPATH="${BACKUP_DIR}/${FILENAME}"
START_TIME=$(date +%s)

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

notify_failure() {
    local msg="$1"
    if [ -n "$BACKUP_NOTIFY_TELEGRAM_TOKEN" ] && [ -n "$BACKUP_NOTIFY_TELEGRAM_CHAT_ID" ]; then
        curl -s -X POST "https://api.telegram.org/bot${BACKUP_NOTIFY_TELEGRAM_TOKEN}/sendMessage" \
            -d chat_id="${BACKUP_NOTIFY_TELEGRAM_CHAT_ID}" \
            -d text="<b>Backup failed</b>%0A${msg}" \
            -d parse_mode=HTML > /dev/null 2>&1 || true
    fi
}

# Step 1: Dump
log "Starting backup: ${FILENAME}"
if ! pg_dump -Fc -h "$PGHOST" -U "$PGUSER" -d "$PGDATABASE" -f "$FILEPATH"; then
    log "ERROR: pg_dump failed"
    rm -f "$FILEPATH"
    notify_failure "pg_dump failed for ${PGDATABASE}"
    exit 1
fi

FILESIZE=$(du -h "$FILEPATH" | cut -f1)
ELAPSED=$(( $(date +%s) - START_TIME ))
log "Dump complete: ${FILENAME} (${FILESIZE}, ${ELAPSED}s)"

# Step 2: Rotate local backups
TOTAL=$(ls -1 "${BACKUP_DIR}"/medtracker_*.dump 2>/dev/null | wc -l)
if [ "$TOTAL" -gt "$KEEP_LOCAL" ]; then
    DELETE_COUNT=$((TOTAL - KEEP_LOCAL))
    ls -1t "${BACKUP_DIR}"/medtracker_*.dump | tail -n "$DELETE_COUNT" | while read -r f; do
        log "Rotating old backup: $(basename "$f")"
        rm -f "$f"
    done
fi

# Step 3: S3 upload (if configured)
if [ -n "$BACKUP_S3_BUCKET" ]; then
    S3_PREFIX="${BACKUP_S3_PREFIX:-medtracker}"
    KEEP_REMOTE="${BACKUP_KEEP_REMOTE:-30}"
    S3_ARGS=""
    if [ -n "$BACKUP_S3_ENDPOINT" ]; then
        S3_ARGS="--endpoint-url ${BACKUP_S3_ENDPOINT}"
    fi

    log "Uploading to s3://${BACKUP_S3_BUCKET}/${S3_PREFIX}/${FILENAME}"
    if ! aws s3 cp "$FILEPATH" "s3://${BACKUP_S3_BUCKET}/${S3_PREFIX}/${FILENAME}" $S3_ARGS; then
        log "WARNING: S3 upload failed (local backup preserved)"
        notify_failure "S3 upload failed for ${FILENAME}"
        exit 2
    fi
    log "Upload complete"

    # Rotate remote backups
    REMOTE_FILES=$(aws s3 ls "s3://${BACKUP_S3_BUCKET}/${S3_PREFIX}/" $S3_ARGS | awk '{print $4}' | grep '^medtracker_.*\.dump$' | sort)
    REMOTE_COUNT=$(echo "$REMOTE_FILES" | grep -c . || true)
    if [ "$REMOTE_COUNT" -gt "$KEEP_REMOTE" ]; then
        DELETE_REMOTE=$((REMOTE_COUNT - KEEP_REMOTE))
        echo "$REMOTE_FILES" | head -n "$DELETE_REMOTE" | while read -r rf; do
            log "Rotating remote backup: ${rf}"
            aws s3 rm "s3://${BACKUP_S3_BUCKET}/${S3_PREFIX}/${rf}" $S3_ARGS
        done
    fi
fi

log "Backup complete: ${FILENAME}"
