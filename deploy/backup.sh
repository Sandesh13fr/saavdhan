#!/bin/sh
# Stop writers so the SQLite snapshot and immutable evidence belong to one maintenance window.
set -eu
cd "$(dirname "$0")"
mkdir -p backups
chmod 700 backups
chown 10001:10001 backups
trap 'docker compose --env-file production.env start app' EXIT
docker compose --env-file production.env stop app
docker compose --env-file production.env run --rm --no-deps -v "$(pwd)/backups:/backups" app python scripts/backup.py create /app/data "/backups/bakaya-$(date -u +%Y%m%dT%H%M%SZ).enc"
# Retention is bounded to this dedicated directory; never remove source evidence.
find "$(pwd)/backups" -maxdepth 1 -type f -name 'bakaya-*.enc' -mtime +14 -delete
