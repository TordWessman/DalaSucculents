#!/usr/bin/env bash
# Migrate local dala.db schema + data to Cloudflare D1
set -euo pipefail

DB_NAME="dala-succulents-db"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DB_PATH="$PROJECT_DIR/dala.db"
SEED_SQL="$SCRIPT_DIR/seed_data.sql"

if [ ! -f "$DB_PATH" ]; then
  echo "Error: $DB_PATH not found. Run: python db/init_db.py" >&2
  exit 1
fi

SCHEMA_SQL="$SCRIPT_DIR/schema_ddl.sql"

echo "==> Extracting DDL from schema.sql (skipping seed INSERTs)..."
sed -n '/^DROP /p; /^CREATE /,/);/p' "$SCRIPT_DIR/schema.sql" > "$SCHEMA_SQL"

echo "==> Applying schema DDL to D1..."
wrangler d1 execute "$DB_NAME" --remote --file="$SCHEMA_SQL"

echo "==> Exporting data from local dala.db..."
sqlite3 "$DB_PATH" <<'EXPORT' > "$SEED_SQL"
.mode insert products
SELECT * FROM products ORDER BY sort_order;
.mode insert carousel_slides
SELECT * FROM carousel_slides ORDER BY sort_order;
EXPORT

echo "==> Importing data into D1..."
wrangler d1 execute "$DB_NAME" --remote --file="$SEED_SQL"

echo "==> Done. Verify with:"
echo "    wrangler d1 execute $DB_NAME --remote --command=\"SELECT count(*) FROM products\""
