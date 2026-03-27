# Database Tables (dala.db)

SQLite database used by the API server. Schema defined in `db/schema.sql`, seeded by `db/init_db.py`.

## genera

Plant genera with family classification.

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique genus ID |
| name | TEXT | NOT NULL UNIQUE | Genus name (e.g. "Echeveria") |
| family | TEXT | NOT NULL | Family name (e.g. "Crassulaceae") |
| slug | TEXT | NOT NULL UNIQUE | URL-safe identifier |

**Used by**: `GET /api/plants` (joined), `GET /api/plants/:slug` (joined)

## countries

ISO 3166-1 country records for geographic distribution.

| Column | Type | Constraints | Description |
|---|---|---|---|
| alpha3 | TEXT | PRIMARY KEY | ISO 3166-1 alpha-3 code (e.g. "ZAF") |
| name | TEXT | NOT NULL | Country name |
| alpha2 | TEXT | NOT NULL | ISO 3166-1 alpha-2 code (e.g. "ZA") |

**Used by**: `GET /api/plants/:slug` (via plant_countries join)

## plants

Core entity — one row per botanical taxon with cultivation and conservation data.

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique plant ID |
| baserow_id | TEXT | UNIQUE | Source Baserow row ID |
| slug | TEXT | NOT NULL UNIQUE | URL-safe identifier |
| genus_id | INTEGER | NOT NULL, FK genera(id) | Reference to genus |
| species | TEXT | NOT NULL | Species epithet |
| subspecies | TEXT | | Subspecies epithet |
| variety | TEXT | | Variety epithet |
| form | TEXT | | Form epithet |
| cultivar | TEXT | | Cultivar name |
| field_number | TEXT | | Collector's field number |
| field_location | TEXT | | Collection locality |
| author_citation | TEXT | | Taxonomic author citation |
| vegetation_period | TEXT | | Summer \| Winter |
| substrate | TEXT | | Substrate preference |
| winter_temp_range | TEXT | | Minimum winter temperature range |
| watering | TEXT | | Watering level (emoji scale) |
| exposure | TEXT | | Light exposure preference |
| red_list_status | TEXT | | IUCN Red List category |
| red_list_url | TEXT | | Link to IUCN assessment |
| cites_listing | TEXT | | CITES appendix (None/I/II/III) |
| llifle_url | TEXT | | Link to LLIFLE page |
| notes | TEXT | | General notes |
| sort_order | INTEGER | DEFAULT 0 | Display order (ascending) |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Row creation time |

**Used by**: `GET /api/plants`, `GET /api/plants/:slug`

## plant_countries

Many-to-many relationship between plants and countries of origin.

| Column | Type | Constraints | Description |
|---|---|---|---|
| plant_id | INTEGER | NOT NULL, FK plants(id) ON DELETE CASCADE | Reference to plant |
| country_alpha3 | TEXT | NOT NULL, FK countries(alpha3) | Reference to country |

**Primary key**: (plant_id, country_alpha3)

**Used by**: `GET /api/plants/:slug`

## specimens

Individual plant specimens linked to a taxon. May be for sale or collection-only.

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique specimen ID |
| plant_id | INTEGER | NOT NULL, FK plants(id) ON DELETE CASCADE | Reference to parent plant |
| specimen_code | TEXT | UNIQUE | Unique specimen identifier |
| specimen_suffix | TEXT | | Suffix for specimen variants |
| for_sale | INTEGER | DEFAULT 0 | 1 = available for purchase |
| price | REAL | | Price in EUR |
| notes | TEXT | | Specimen-specific notes |
| propagation_date | TEXT | | Date of propagation |
| propagation_method | TEXT | | Seed, cutting, graft, etc. |
| specimen_origin | TEXT | | Where this specimen came from |
| source_material_origin | TEXT | | Origin of source material |
| provenance | TEXT | | Provenance chain |
| image_url | TEXT | | Specimen photo URL |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Row creation time |

**Used by**: `GET /api/plants/:slug` (nested), shop mode

## cart_items

Session-based shopping cart. No login required.

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique cart item ID |
| session_id | TEXT | NOT NULL | Browser session identifier |
| specimen_id | INTEGER | NOT NULL, FK specimens(id) ON DELETE CASCADE | Reference to specimen |
| quantity | INTEGER | NOT NULL DEFAULT 1 | Quantity in cart |
| added_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Time added to cart |

**Unique constraint**: (session_id, specimen_id)

**Used by**: `GET /api/cart`, `POST /api/cart`, `DELETE /api/cart/:id`

## users

Google-authenticated user accounts with role-based access. **Local only** — not migrated to D1.

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique user ID |
| google_id | TEXT | NOT NULL UNIQUE | Google account ID from ID token |
| email | TEXT | NOT NULL UNIQUE | User's Google email |
| name | TEXT | | Display name from Google profile |
| picture_url | TEXT | | Google profile avatar URL |
| role | TEXT | NOT NULL DEFAULT 'user' | `user` or `admin` |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Account creation time |
| last_login | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last login time |

**Seed data**: None (users created via Google Sign-In).

**Used by**: `POST /api/auth/login`, `GET /api/auth/me`
