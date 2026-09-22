#!/usr/bin/env bash
# Consistent SQLite snapshot into /var/lib/c2c/backups/, keeping the last 30.
# Run by c2c-backup.timer (nightly) or manually as the c2c user.
set -euo pipefail

DB="${C2C_DB:-/var/lib/c2c/c2c.sqlite}"
BACKUP_DIR=/var/lib/c2c/backups
KEEP=30

mkdir -p "$BACKUP_DIR"
stamp=$(date +%Y%m%d-%H%M%S)
sqlite3 "$DB" ".backup '$BACKUP_DIR/c2c-$stamp.sqlite'"
ln -sf "c2c-$stamp.sqlite" "$BACKUP_DIR/latest.sqlite"

# prune, oldest first
ls -1t "$BACKUP_DIR"/c2c-*.sqlite | tail -n +$((KEEP + 1)) | xargs -r rm --
echo "backup ok: $BACKUP_DIR/c2c-$stamp.sqlite"
