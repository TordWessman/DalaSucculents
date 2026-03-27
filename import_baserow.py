#!/usr/bin/env python3
"""
Baserow → Dala Succulents Import Pipeline

Fetches all four Baserow tables (Plant index, Genus, Plant collection, Country),
resolves linked rows, and imports into the local dala.db using the new
plants/specimens/genera/countries schema.

Usage:
    python import_baserow.py          # interactive confirmation
    python import_baserow.py --yes    # skip confirmation

Requires: requests, python-dotenv
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
BASEROW_API_URL = os.environ.get("BASEROW_API_URL", "https://api.baserow.io")

# Baserow table IDs
TABLE_PLANTS = 746875
TABLE_GENUS = 747169
TABLE_COLLECTION = 748062
TABLE_COUNTRY = 753691

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dala.db")
SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db", "schema.sql")

# Placeholder image for plants without images
PLACEHOLDER_IMAGE = "https://picsum.photos/seed/succulent-placeholder/400/400"


def check_config():
    if not BASEROW_API_TOKEN:
        print("Error: Missing BASEROW_API_TOKEN in .env")
        sys.exit(1)


def fetch_all_rows(table_id, headers):
    """Fetch all rows from a Baserow table with pagination."""
    rows = []
    url = f"{BASEROW_API_URL}/api/database/rows/table/{table_id}/"
    params = {"size": 200}

    while url:
        resp = requests.get(url, headers=headers, params=params)
        resp.raise_for_status()
        data = resp.json()
        rows.extend(data.get("results", []))
        url = data.get("next")
        params = {}
    return rows


def extract_select_value(val):
    """Extract the value string from a Baserow single_select field."""
    if isinstance(val, dict) and "value" in val:
        return val["value"]
    return val


def extract_link_rows(val):
    """Extract linked row IDs and values from a link_row field."""
    if isinstance(val, list):
        return [(item["id"], item.get("value", "")) for item in val]
    return []


def extract_file_url(val):
    """Extract the first file URL from a Baserow file field."""
    if isinstance(val, list) and len(val) > 0:
        return val[0].get("url", None)
    return None


# Red List typo normalization map
RED_LIST_TYPOS = {
    "Data deficiend": "Data deficient",
    "Data deficiënt": "Data deficient",
    "Critically endangerad": "Critically endangered",
    "Critically Endangered": "Critically endangered",
    "Least Concern": "Least concern",
    "Near Threatened": "Near threatened",
    "Not Evaluated": "Not evaluated",
}


def normalize_red_list(val):
    """Normalize Red List status, fixing known Baserow typos."""
    if not val:
        return val
    return RED_LIST_TYPOS.get(val, val)


def generate_slug(genus_name, species, subspecies=None, variety=None,
                  form=None, cultivar=None, field_number=None,
                  field_location=None):
    """Generate a URL-safe slug from botanical name components."""
    parts = [genus_name, species]

    if subspecies:
        parts.extend(["ssp", subspecies])
    if variety:
        parts.extend(["var", variety])
    if form:
        parts.extend(["f", form])
    if cultivar:
        parts.append(cultivar.strip("'\""))
    if field_number:
        parts.append(field_number)
    if field_location:
        # Strip parentheses and clean up
        loc = field_location.strip("()")
        parts.append(loc)

    slug = " ".join(parts).lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    slug = slug.strip("-")
    return slug


def generate_genus_slug(genus_name):
    """Generate a slug for a genus."""
    return genus_name.lower().strip()


def import_data(db_path=DB_PATH):
    """Main import pipeline."""
    check_config()
    headers = {"Authorization": f"Token {BASEROW_API_TOKEN}"}

    # --- Fetch all tables ---
    print("Fetching Genus table...")
    genus_rows = fetch_all_rows(TABLE_GENUS, headers)
    print(f"  {len(genus_rows)} genera")

    print("Fetching Country table...")
    country_rows = fetch_all_rows(TABLE_COUNTRY, headers)
    print(f"  {len(country_rows)} countries")

    print("Fetching Plant index table...")
    plant_rows = fetch_all_rows(TABLE_PLANTS, headers)
    print(f"  {len(plant_rows)} plants")

    print("Fetching Plant collection table...")
    specimen_rows = fetch_all_rows(TABLE_COLLECTION, headers)
    print(f"  {len(specimen_rows)} specimens")

    # --- Build lookup maps ---

    # Genus: baserow_id → {name, family}
    genus_map = {}
    for row in genus_rows:
        genus_name = extract_select_value(row.get("field_6300340", ""))
        family = extract_select_value(row.get("field_6301600", ""))
        if genus_name:
            genus_map[row["id"]] = {"name": genus_name, "family": family or "Unknown"}

    # Country: baserow_id → {alpha3, name, alpha2}
    country_map = {}
    for row in country_rows:
        alpha3 = row.get("field_6365195", "")
        name = row.get("field_6365193", "")
        alpha2 = row.get("field_6365194", "")
        if alpha3:
            country_map[row["id"]] = {"alpha3": alpha3, "name": name, "alpha2": alpha2}

    # --- Create database ---
    print(f"\nCreating database at {db_path}...")
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    # Apply schema
    with open(SCHEMA_PATH) as f:
        schema_sql = f.read()
    # Filter out INSERT statements from schema (those are old seed data)
    schema_lines = []
    skip = False
    for line in schema_sql.split("\n"):
        if line.strip().startswith("INSERT"):
            skip = True
        if skip and line.strip().endswith(";"):
            skip = False
            continue
        if not skip:
            schema_lines.append(line)
    cursor.executescript("\n".join(schema_lines))

    # --- Insert genera ---
    print("Importing genera...")
    genus_db_ids = {}  # baserow_id → sqlite_id
    for br_id, g in genus_map.items():
        cursor.execute(
            "INSERT INTO genera (name, family, slug) VALUES (?, ?, ?)",
            (g["name"], g["family"], generate_genus_slug(g["name"]))
        )
        genus_db_ids[br_id] = cursor.lastrowid
    print(f"  {len(genus_db_ids)} genera inserted")

    # --- Insert countries ---
    print("Importing countries...")
    country_count = 0
    for br_id, c in country_map.items():
        try:
            cursor.execute(
                "INSERT OR IGNORE INTO countries (alpha3, name, alpha2) VALUES (?, ?, ?)",
                (c["alpha3"], c["name"], c["alpha2"])
            )
            country_count += 1
        except sqlite3.IntegrityError:
            pass
    print(f"  {country_count} countries inserted")

    # --- Insert plants ---
    print("Importing plants...")
    plant_db_ids = {}  # baserow_row_id → sqlite_id
    slug_counts = {}   # for deduplication

    for row in plant_rows:
        # Resolve genus
        genus_links = extract_link_rows(row.get("field_6313656", []))
        if not genus_links:
            print(f"  WARNING: Skipping plant row {row['id']} - no genus linked")
            continue

        genus_br_id = genus_links[0][0]
        genus_db_id = genus_db_ids.get(genus_br_id)
        if not genus_db_id:
            print(f"  WARNING: Skipping plant row {row['id']} - genus {genus_br_id} not found")
            continue

        genus_name = genus_map[genus_br_id]["name"]
        species = row.get("field_6300262", "") or ""
        subspecies = row.get("field_6300742") or None
        variety = row.get("field_6300796") or None
        form_val = row.get("field_6300798") or None
        cultivar = row.get("field_6300802") or None
        field_number = row.get("field_6331303") or None
        field_location = row.get("field_6331304") or None
        baserow_id = row.get("field_6995221") or str(row["id"])

        # Generate slug
        slug = generate_slug(genus_name, species, subspecies, variety,
                             form_val, cultivar, field_number, field_location)
        # Deduplicate slugs
        if slug in slug_counts:
            slug_counts[slug] += 1
            slug = f"{slug}-{slug_counts[slug]}"
        else:
            slug_counts[slug] = 1

        cursor.execute("""
            INSERT INTO plants (
                baserow_id, slug, genus_id, species, subspecies, variety, form,
                cultivar, field_number, field_location, author_citation,
                vegetation_period, substrate, winter_temp_range, watering,
                exposure, red_list_status, red_list_url, cites_listing,
                llifle_url, notes, sort_order
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            baserow_id,
            slug,
            genus_db_id,
            species,
            subspecies,
            variety,
            form_val,
            cultivar,
            field_number,
            field_location,
            row.get("field_6361735") or None,
            extract_select_value(row.get("field_6297766")),
            extract_select_value(row.get("field_6360415")),
            extract_select_value(row.get("field_6360425")),
            extract_select_value(row.get("field_6376724")),
            extract_select_value(row.get("field_6410605")),
            normalize_red_list(extract_select_value(row.get("field_6360427"))),
            row.get("field_6360459") or None,
            extract_select_value(row.get("field_6360475")),
            row.get("field_6360469") or None,
            row.get("field_6457140") or None,
            row.get("order", 0),
        ))
        plant_db_ids[row["id"]] = cursor.lastrowid

        # Insert plant-country relations
        country_links = extract_link_rows(row.get("field_6365077", []))
        for c_br_id, c_val in country_links:
            country_info = country_map.get(c_br_id)
            alpha3 = country_info["alpha3"] if country_info else c_val
            if alpha3:
                try:
                    cursor.execute(
                        "INSERT OR IGNORE INTO plant_countries (plant_id, country_alpha3) VALUES (?, ?)",
                        (plant_db_ids[row["id"]], alpha3)
                    )
                except sqlite3.IntegrityError:
                    pass

    print(f"  {len(plant_db_ids)} plants inserted")

    # --- Insert specimens ---
    print("Importing specimens...")
    specimen_count = 0
    for row in specimen_rows:
        # Resolve plant link
        plant_links = extract_link_rows(row.get("field_6308515", []))
        if not plant_links:
            continue

        plant_br_id = plant_links[0][0]
        plant_db_id = plant_db_ids.get(plant_br_id)
        if not plant_db_id:
            continue

        # Extract specimen ID from formula field
        spec_id_links = row.get("field_6308470", [])
        specimen_code = None
        if isinstance(spec_id_links, list) and spec_id_links:
            specimen_code = spec_id_links[0].get("value")
        elif isinstance(spec_id_links, str):
            specimen_code = spec_id_links

        image_url = extract_file_url(row.get("field_6341815", []))

        cursor.execute("""
            INSERT INTO specimens (
                plant_id, specimen_code, specimen_suffix, for_sale, notes,
                propagation_date, propagation_method, specimen_origin,
                source_material_origin, provenance, image_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            plant_db_id,
            specimen_code,
            row.get("field_6319584") or None,
            1 if row.get("field_6308472") else 0,
            row.get("field_6308471") or None,
            row.get("field_6308673") or None,
            extract_select_value(row.get("field_6309007")),
            extract_select_value(row.get("field_6309023")),
            extract_select_value(row.get("field_6309031")),
            row.get("field_6309034") or None,
            image_url,
        ))
        specimen_count += 1

    print(f"  {specimen_count} specimens inserted")

    conn.commit()

    # --- Summary ---
    cursor.execute("SELECT COUNT(*) FROM genera")
    print(f"\nDatabase summary:")
    print(f"  Genera:    {cursor.fetchone()[0]}")
    cursor.execute("SELECT COUNT(*) FROM countries")
    print(f"  Countries: {cursor.fetchone()[0]}")
    cursor.execute("SELECT COUNT(*) FROM plants")
    print(f"  Plants:    {cursor.fetchone()[0]}")
    cursor.execute("SELECT COUNT(*) FROM specimens")
    print(f"  Specimens: {cursor.fetchone()[0]}")
    cursor.execute("SELECT COUNT(*) FROM plant_countries")
    print(f"  Plant-country links: {cursor.fetchone()[0]}")
    cursor.execute("SELECT COUNT(*) FROM specimens WHERE for_sale = 1")
    print(f"  Specimens for sale:  {cursor.fetchone()[0]}")

    conn.close()
    print(f"\nDone! Database at {db_path}")


if __name__ == "__main__":
    if "--yes" not in sys.argv:
        print(f"This will DROP and recreate {DB_PATH}.")
        answer = input("Continue? [y/N] ").strip().lower()
        if answer != "y":
            print("Aborted.")
            sys.exit(0)
    import_data()
