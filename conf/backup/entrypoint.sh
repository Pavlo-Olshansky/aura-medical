#!/bin/sh
set -e

SCHEDULE="${BACKUP_SCHEDULE:-0 3 * * *}"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Backup container starting"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Schedule: ${SCHEDULE}"

# Build environment string for cron (cron doesn't inherit env)
env | grep -E '^(PG|BACKUP_|AWS_)' > /etc/backup.env

# Write crontab
echo "${SCHEDULE} . /etc/backup.env && /backup.sh >> /var/log/backup.log 2>&1" | crontab -

# Create log file
touch /var/log/backup.log

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Cron configured, starting crond"

# Run crond in foreground, tail log so docker logs works
crond -f -l 2 &
tail -f /var/log/backup.log
