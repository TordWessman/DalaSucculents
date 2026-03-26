#!/usr/bin/env python3
"""
Baserow → SQLite Export Script

Fetches all rows from a Baserow cloud table via REST API
and exports them into a SQLite database, auto-creating the
target table based on the Baserow field schema.

Requirements: requests, python-dotenv
"""

import os
import re
import sys
import json
import sqlite3

import requests
from dotenv import load_dotenv

load_dotenv()

BASEROW_API_TOKEN = os.environ.get("BASEROW_API_TOKEN")
BASEROW_TABLE_ID = os.environ.get("BASEROW_TABLE_ID")
BASEROW_API_URL = os.environ.get("BASEROW_API_URL", "https://api.baserow.io")

SQLITE_DB = os.environ.get("SQLITE_DB", "baserow_export.db")
SQLITE_TABLE = os.environ.get("SQLITE_TABLE", f"baserow_table_{BASEROW_TABLE_ID}")


def check_config():
    missing = []
    if not BASEROW_API_TOKEN:
        missing.append("BASEROW_API_TOKEN")
    if not BASEROW_TABLE_ID:
        missing.append("BASEROW_TABLE_ID")
    if missing:
        print(f"Error: Missing required environment variables: {', '.join(missing)}")
        print("Copy .env.example to .env and fill in your values.")
        sys.exit(1)


def sanitize_column_name(name):
    """Convert a Baserow field name into a valid SQLite column name."""
    name = name.strip().lower()
    name = re.sub(r"[^a-z0-9_]", "_", name)
    name = re.sub(r"_+", "_", name)
    name = name.strip("_")
    if not name or name[0].isdigit():
        name = "col_" + name
    return name


def fetch_fields(table_id, headers):
    """Fetch field metadata for the table."""
    url = f"{BASEROW_API_URL}/api/database/fields/table/{table_id}/"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()


def fetch_all_rows(table_id, headers):
    """Fetch all rows from a Baserow table, handling pagination."""
    rows = []
    url = f"{BASEROW_API_URL}/api/database/rows/table/{table_id}/"
    params = {"user_field_names": "true", "size": 200}

    while url:
        resp = requests.get(url, headers=headers, params=params)
        resp.raise_for_status()
        data = resp.json()
        rows.extend(data.get("results", []))
        url = data.get("next")
        params = {}  # next URL already includes query params
        print(f"  Fetched {len(rows)} rows so far...")

    return rows


def map_field_to_sqlite(field):
    """Map a Baserow field type to a SQLite column type."""
    ftype = field.get("type", "text")

    if ftype in ("text", "long_text", "url", "email", "phone_number"):
        return "TEXT"
    elif ftype == "number":
        decimal_places = field.get("number_decimal_places", 0)
        if decimal_places and decimal_places > 0:
            return "REAL"
        return "INTEGER"
    elif ftype == "boolean":
        return "INTEGER"
    elif ftype == "date":
        return "TEXT"
    elif ftype in ("single_select", "rating"):
        return "TEXT"
    elif ftype in ("file", "multiple_select", "link_row", "multiple_collaborators"):
        return "TEXT"  # stored as JSON string
    else:
        return "TEXT"


def build_column_map(fields):
    """Build a list of (baserow_field_name, sqlite_col_name, sqlite_type) tuples."""
    columns = []
    seen = set()
    for field in fields:
        br_name = field["name"]
        col = sanitize_column_name(br_name)
        base = col
        i = 2
        while col in seen:
            col = f"{base}_{i}"
            i += 1
        seen.add(col)
        sqlite_type = map_field_to_sqlite(field)
        columns.append((br_name, col, sqlite_type))
    return columns


def create_table(cursor, table_name, columns):
    """Drop and recreate the SQLite table."""
    col_defs = ['"baserow_id" INTEGER PRIMARY KEY']
    for _, col_name, col_type in columns:
        col_defs.append(f'"{col_name}" {col_type}')

    cursor.execute(f'DROP TABLE IF EXISTS "{table_name}"')
    create_sql = f'CREATE TABLE "{table_name}" (\n  ' + ",\n  ".join(col_defs) + "\n)"
    cursor.execute(create_sql)
    print(f'Created table "{table_name}" with {len(columns) + 1} columns.')


def serialize_value(value):
    """Serialize a value for SQLite insertion."""
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return json.dumps(value)
    if isinstance(value, bool):
        return int(value)
    return value


def insert_rows(cursor, table_name, columns, rows):
    """Batch-insert rows into SQLite."""
    if not rows:
        print("No rows to insert.")
        return

    col_names = ['"baserow_id"'] + [f'"{c}"' for _, c, _ in columns]
    placeholders = ", ".join(["?"] * len(col_names))
    sql = f'INSERT INTO "{table_name}" ({", ".join(col_names)}) VALUES ({placeholders})'

    batch = []
    for row in rows:
        values = [row.get("id")]
        for br_name, _, _ in columns:
            val = row.get(br_name)
            # single_select comes as {"id": ..., "value": "...", "color": "..."}
            if isinstance(val, dict) and "value" in val and "id" in val and "color" in val:
                val = val["value"]
            values.append(serialize_value(val))
        batch.append(tuple(values))

    cursor.executemany(sql, batch)
    print(f"  Inserted {len(batch)} rows.")


def main():
    check_config()

    headers = {"Authorization": f"Token {BASEROW_API_TOKEN}"}

    # Fetch schema
    print(f"Fetching fields for table {BASEROW_TABLE_ID}...")
    fields = fetch_fields(BASEROW_TABLE_ID, headers)
    columns = build_column_map(fields)
    print(f"Found {len(columns)} fields.")

    # Fetch rows
    print(f"Fetching rows from table {BASEROW_TABLE_ID}...")
    rows = fetch_all_rows(BASEROW_TABLE_ID, headers)
    print(f"Fetched {len(rows)} total rows.")

    if not rows:
        print("No rows found. Exiting.")
        return

    # Confirm before dropping
    print(f'\nThis will DROP and recreate "{SQLITE_TABLE}" in {SQLITE_DB}.')
    answer = input("Continue? [y/N] ").strip().lower()
    if answer != "y":
        print("Aborted.")
        return

    # Connect to SQLite and export
    conn = sqlite3.connect(SQLITE_DB)
    cursor = conn.cursor()

    try:
        create_table(cursor, SQLITE_TABLE, columns)
        insert_rows(cursor, SQLITE_TABLE, columns, rows)
        conn.commit()
        print(f'\nDone! Exported {len(rows)} rows to {SQLITE_DB} → "{SQLITE_TABLE}".')
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
