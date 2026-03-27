#!/usr/bin/env bash
# Migrate local dala.db schema + data to Cloudflare D1
# Uses INSERT OR REPLACE to upsert rows — safe to re-run without data loss
set -euo pipefail

DB_NAME="dala-succulents-db"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DB_PATH="$PROJECT_DIR/dala.db"
SEED_SQL="$SCRIPT_DIR/seed_data.sql"

# Tables to skip (will not be migrated). Example: SKIP_TABLES=(orders customers)
SKIP_TABLES=(users)

if [ ! -f "$DB_PATH" ]; then
  echo "Error: $DB_PATH not found. Run: python db/init_db.py" >&2
  exit 1
fi

# Helper: check if a table is in the skip list
is_skipped() {
  local table="$1"
  for skip in "${SKIP_TABLES[@]+"${SKIP_TABLES[@]}"}"; do
    if [ "$skip" = "$table" ]; then
      return 0
    fi
  done
  return 1
}

echo "==> Applying schema to D1 (CREATE TABLE IF NOT EXISTS)..."
wrangler d1 execute "$DB_NAME" --remote --file="$SCRIPT_DIR/schema.sql"

echo "==> Exporting data from local dala.db..."
> "$SEED_SQL"  # truncate

# Tables in dependency order (parents before children)
TABLES="genera countries plants plant_countries specimens cart_items"

for TABLE in $TABLES; do
  if is_skipped "$TABLE"; then
    echo "    Skipping $TABLE (in SKIP_TABLES)"
    continue
  fi

  echo "    Exporting $TABLE..."

  # Get column names
  COLUMNS=$(sqlite3 "$DB_PATH" "PRAGMA table_info($TABLE);" | awk -F'|' '{print $2}' | paste -sd, -)

  # Export as INSERT OR REPLACE
  sqlite3 "$DB_PATH" <<EOF >> "$SEED_SQL"
.mode insert $TABLE
SELECT * FROM $TABLE ORDER BY rowid;
EOF
done

# Rewrite INSERT INTO → INSERT OR REPLACE INTO
sed -i '' 's/^INSERT INTO /INSERT OR REPLACE INTO /g' "$SEED_SQL"

if [ -s "$SEED_SQL" ]; then
  echo "==> Importing data into D1..."
  wrangler d1 execute "$DB_NAME" --remote --file="$SEED_SQL"
else
  echo "==> No data to import (all tables skipped or empty)."
fi

echo "==> Done. Verify with:"
echo "    wrangler d1 execute $DB_NAME --remote --command=\"SELECT count(*) FROM plants\""
