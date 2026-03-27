-- Dala Succulents schema
-- Plant-centric collection model: genera → plants → specimens
-- Idempotent: safe to re-run

CREATE TABLE IF NOT EXISTS genera (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    family TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS countries (
    alpha3 TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    alpha2 TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS plants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    baserow_id TEXT UNIQUE,
    slug TEXT NOT NULL UNIQUE,
    genus_id INTEGER NOT NULL REFERENCES genera(id),
    species TEXT NOT NULL,
    subspecies TEXT,
    variety TEXT,
    form TEXT,
    cultivar TEXT,
    field_number TEXT,
    field_location TEXT,
    author_citation TEXT,
    -- Cultivation
    vegetation_period TEXT,
    substrate TEXT,
    winter_temp_range TEXT,
    watering TEXT,
    exposure TEXT,
    -- Conservation
    red_list_status TEXT,
    red_list_url TEXT,
    cites_listing TEXT,
    llifle_url TEXT,
    -- Meta
    notes TEXT,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS plant_countries (
    plant_id INTEGER NOT NULL REFERENCES plants(id) ON DELETE CASCADE,
    country_alpha3 TEXT NOT NULL REFERENCES countries(alpha3),
    PRIMARY KEY (plant_id, country_alpha3)
);

CREATE TABLE IF NOT EXISTS specimens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plant_id INTEGER NOT NULL REFERENCES plants(id) ON DELETE CASCADE,
    specimen_code TEXT UNIQUE,
    specimen_suffix TEXT,
    for_sale INTEGER DEFAULT 0,
    price REAL,
    notes TEXT,
    propagation_date TEXT,
    propagation_method TEXT,
    specimen_origin TEXT,
    source_material_origin TEXT,
    provenance TEXT,
    image_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cart_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    specimen_id INTEGER NOT NULL REFERENCES specimens(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL DEFAULT 1,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(session_id, specimen_id)
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    google_id TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    name TEXT,
    picture_url TEXT,
    role TEXT NOT NULL DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
