# Database Tables (dala.db)

SQLite database used by the API server and build system. Schema defined in `db/schema.sql`, seeded by `db/init_db.py`.

## products

Plant inventory. Each row is a product listing on the site.

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique product ID |
| name | TEXT | NOT NULL | Display name (e.g. "Echeveria 'Lola'") |
| slug | TEXT | NOT NULL UNIQUE | URL-safe identifier (e.g. "echeveria-lola") |
| scientific_name | TEXT | | Genus or species name, shown in italic |
| description | TEXT | | Full product description for detail page |
| price | REAL | NOT NULL | Price in USD |
| image_url | TEXT | | Thumbnail image (400x400) |
| image_url_large | TEXT | | Detail page image (800x800) |
| sold_out | INTEGER | DEFAULT 0 | 1 = sold out, 0 = available |
| sort_order | INTEGER | DEFAULT 0 | Display order (ascending) |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Row creation time |

**Seed data**: 6 products (Echeveria 'Lola', Haworthia cooperi, Lithops karasmontana, Adenia glauca, Pachypodium lamerei, Euphorbia obesa).

**Used by**: `GET /api/products`, `GET /api/products/<slug>`, `build.py`

## carousel_slides

Hero carousel banners on the home page.

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique slide ID |
| image_url | TEXT | NOT NULL | Banner image (1200x500) |
| heading | TEXT | NOT NULL | Large overlay text |
| subheading | TEXT | | Smaller description text |
| button_text | TEXT | | CTA button label |
| button_link | TEXT | | CTA button href |
| sort_order | INTEGER | DEFAULT 0 | Display order (ascending) |

**Seed data**: 3 slides (Rare & Unusual Succulents, New Arrivals Weekly, Expert Care Guides).

**Used by**: `GET /api/carousel`, `build.py`

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
