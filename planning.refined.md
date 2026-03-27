# Dala Succulents Website Reshape: Refined Plan

## Purpose

This plan refines `planning.draft.md` against the current code base. The main conclusion is that the current implementation is a small product storefront prototype, while the intended site is a plant collection website with two operating modes:

1. Plant profile / gallery view
2. Web shop view for individual specimens

The refined plan therefore focuses on:

- Reusing the existing React SPA, routing, auth wrapper, and API-service abstraction
- Replacing placeholder product-centric content with plant- and specimen-centric domain models
- Expanding the backend and schema to support the actual Baserow source data
- Delivering the reshape in phases so the site remains deployable throughout the transition

## Current Code Base Review

### What exists today

- React + Vite SPA in `DalaSucculents/frontend`
- Two routes only:
  - `/` in `frontend/src/pages/HomePage.jsx`
  - `/products/:slug` in `frontend/src/pages/ProductPage.jsx`
- Shared shell in `frontend/src/components/Layout.jsx`
- Header/footer/navigation already exist, but all content is placeholder and shop-oriented
- Data access is abstracted cleanly through:
  - `frontend/src/services/ApiDataService.js`
  - `frontend/src/services/D1DataService.js`
  - `frontend/src/services/DataContext.jsx`
- Local Python API exists in `DalaSucculents/api_server.py`
- Cloudflare Pages Functions exist for:
  - `GET /api/products`
  - `GET /api/products/:slug`
  - `GET /api/carousel`
- SQLite/D1 schema currently contains only:
  - `products`
  - `carousel_slides`
  - `users`
- Google auth scaffolding exists in:
  - `frontend/src/services/AuthContext.jsx`
  - `frontend/src/components/Header.jsx`
  - `api_server.py`

### What is placeholder or mismatched with the intended site

- The data model is product-based, not plant/specimen-based
- `TABLES.md` and `db/schema.sql` describe seeded sample shop data, not the Baserow collection structure
- The homepage is "Best Sellers" plus carousel, not a plant index or collection browser
- The product page is a simple shop detail page, not a plant profile page with taxonomy and cultivation data
- The header/menu does not match the intended sidebar navigation
- The footer content is marketing placeholder copy
- The current auth UI is partially wired, but equivalent Cloudflare auth endpoints are not present in `functions/api`
- The Baserow import script is generic and table-by-table; it does not yet define the full transformation pipeline from Baserow collection data into web-ready entities

### Reusable pieces

- React app structure and router
- Layout shell and component organization
- Data-service abstraction, which is a strong foundation for evolving the API without tightly coupling UI code
- Existing auth/session concepts, if admin features are needed later
- Python local server and Cloudflare deployment split

## Refined Product Vision

The site should no longer be treated as a standard e-commerce catalog with one row per sellable item. The core public object should be a **plant taxon profile**, with optional sale information attached through individual **specimens**.

### Core browsing modes

#### 1. Gallery view

Primary mode for browsing cultivated taxa.

- Each plant taxon has a profile page
- The profile page emphasizes:
  - botanical name
  - taxonomy
  - images
  - geographic distribution
  - cultivation recommendations
  - conservation/general comments
- Filtering is centered on family/genus/growth habit/type

#### 2. Web shop view

Secondary mode layered on top of the same plant data.

- Shop mode reveals saleable individual specimens
- Availability and price belong to specimens, not to the taxon profile itself
- When stock is empty, the UI should support restock-notification capture rather than an "Add to cart" button

This separation is the single most important architectural shift in the reshape.

## Key Decisions (Resolved)

1. **Landing page**: Home page first (hero section + featured plants, linking to full index)
2. **Shop mode scope**: TBD — whether to show only saleable or all collection specimens
3. **Images**: Placeholder for now; image handling added in later iterations
4. **Cultivation hover help**: All cultivation fields will have structured hover help (see Baserow field mapping below for the complete list)
5. **Production auth**: Deferred — not required for the public site reshape
6. **Cart/checkout**: Basic cart with view-only (no checkout flow). Cart page displays items but no payment/shipping.
7. **Carousel**: Remove entirely — it is product-store scaffolding

## Target Information Architecture

### Recommended top-level pages

- Home (hero + featured plants)
- Plant Index (filterable list)
- Plant Profile
- Cart (view-only)
- Shipping & Terms
- FAQ
- About
- Contact

### Routing recommendation

Suggested React routes:

- `/`
- `/plants`
- `/plants/:slug`
- `/cart`
- `/shipping-terms`
- `/faq`
- `/about`
- `/contact`

Possible later routes if needed:

- `/admin`

Recommendation: do not create a separate shop page initially if the intended interaction is a global "gallery view / shop view" toggle. Keep one plant index and one plant profile route, and let the mode change what is rendered inside them.

---

## Baserow Schema Discovery

All four Baserow tables have been inspected via API. Field IDs, types, and option values are documented below.

### Table: Plant Index (ID: 746875) — 150 rows

| Field Name | Field ID | Type | Options/Notes |
|---|---|---|---|
| Name | 6297762 | formula | Computed display name (e.g., "Adenia globosa") |
| ID | 6995221 | text | Custom ID like "0001" |
| ID__auto | 6297763 | autonumber | Internal auto-increment, not used in web |
| Species | 6300262 | text | |
| Subspecies | 6300742 | text | |
| Variety | 6300796 | text | |
| Form | 6300798 | text | |
| Cultivar | 6300802 | text | |
| Genus | 6313656 | link_row → 747169 | Links to Genus table |
| Family | 6319244 | lookup | Derived through Genus link |
| Field number | 6331303 | text | Collector field number (e.g., "AL 272") |
| Field location | 6331304 | text | Locality (e.g., "El Refugio, NL") |
| Plant collection | 6340534 | link_row → 748062 | Linked specimens |
| Vegetation period | 6297766 | single_select | Summer, Winter |
| Substrate | 6360415 | single_select | 100% mineral-based, Some organic component, Humus-rich succulent mix |
| Winter rest temp range | 6360425 | single_select | [Winter grower], >15 °C, 10-15 °C, 5-10 °C, 1-5 °C, Frost-tolerant (dry), Winter-hardy (outdoors protected) |
| Red List Assessment | 6360427 | single_select | NE, DD, LC, NT, VU, EN, CR, EW, EX |
| Red List Link | 6360459 | url | |
| LLIFLE Link | 6360469 | url | |
| CITES listing | 6360475 | single_select | None, Appendix III, Appendix II, Appendix I |
| Author citation | 6361735 | text | Taxonomic authority (e.g., "Engl.") |
| Native to country | 6365077 | link_row → 753691 | Multiple countries per plant |
| Watering (growing season) | 6376724 | single_select | 💧, 💧💧, 💧💧💧 |
| Exposure | 6410605 | single_select | Full sun, Full sun to partial shade, Partial shade, Tolerates shade |
| Notes | 6457140 | long_text | |

**Sample row** (Adenia globosa):
- Genus: Adenia → Family: Passifloraceae
- Species: globosa, Vegetation: Summer, Substrate: Humus-rich succulent mix
- Winter temp: >15 °C, Watering: 💧💧💧, Exposure: Full sun to partial shade
- Red List: Least concern (LC), CITES: None
- Native to: ETH, KEN, SOM, TZA

### Table: Genus (ID: 747169) — 54 rows

| Field Name | Field ID | Type | Notes |
|---|---|---|---|
| Genus | 6300340 | single_select | Genus name (e.g., "Ariocarpus") |
| Family | 6301600 | single_select | Family name (e.g., "Cactaceae") |
| Plant list | 6319241 | link_row → 746875 | Back-link to plants in this genus |

### Table: Plant Collection / Specimens (ID: 748062) — 191 rows

| Field Name | Field ID | Type | Notes |
|---|---|---|---|
| Specimen ID | 6308470 | formula | Computed code like "0001-26s01" |
| Notes | 6308471 | long_text | |
| For sale | 6308472 | boolean | Currently all false in database |
| Name | 6308515 | link_row → 746875 | Links specimen to plant taxon |
| Propagation date | 6308673 | date | e.g., "2026-01-04" |
| Propagation method | 6309007 | single_select | Seed, (others TBD) |
| Specimen origin | 6309023 | single_select | Country code (e.g., "SE") |
| Source material origin | 6309031 | single_select | Country code (e.g., "DE") |
| Provenance | 6309034 | text | Source name (e.g., "Kaktus Köhres") |
| Specimen suffix | 6319584 | text | e.g., "01" |
| Image | 6341815 | file | **Currently empty for all 191 rows** |

### Table: Country (ID: 753691) — 249 rows

| Field Name | Field ID | Type | Notes |
|---|---|---|---|
| English short name | 6365193 | text | |
| Alpha-2 code | 6365194 | text | |
| Alpha-3 code | 6365195 | text | Used as primary key |
| Numeric | 6365196 | text | |

### Baserow data observations

- **Images are absent**: The Image field on specimens exists but is empty for all 191 rows. No image data exists on the plant index table at all. Placeholder images will be used until this is populated.
- **No specimens are for sale**: The `For sale` boolean is false for all specimens currently.
- **Name is computed**: The Name field on the plant index is a formula field, not stored directly. The web schema should compute display names from genus + species + infraspecific parts.
- **Watering uses emoji scale**: 💧 (low), 💧💧 (moderate), 💧💧💧 (regular). The web UI should render these as visual indicators.
- **Red List has typos**: "Data deficiend" (should be "deficient"), "Critically endangerad" (should be "endangered"). The import pipeline should normalize these.

---

## Refined Data Model

### Target web schema

#### `genera`

```sql
CREATE TABLE genera (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    family TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE
);
```

#### `countries`

```sql
CREATE TABLE countries (
    alpha3 TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    alpha2 TEXT NOT NULL
);
```

#### `plants`

```sql
CREATE TABLE plants (
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
    -- Cultivation (structured columns, not free text)
    vegetation_period TEXT,      -- Summer | Winter
    substrate TEXT,              -- 3 options
    winter_temp_range TEXT,      -- 7 options
    watering TEXT,               -- emoji scale (1-3 drops)
    exposure TEXT,               -- 4 options
    -- Conservation
    red_list_status TEXT,        -- 9 IUCN categories
    red_list_url TEXT,
    cites_listing TEXT,          -- None | Appendix I/II/III
    llifle_url TEXT,
    -- Meta
    notes TEXT,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### `plant_countries` (M2M)

```sql
CREATE TABLE plant_countries (
    plant_id INTEGER NOT NULL REFERENCES plants(id) ON DELETE CASCADE,
    country_alpha3 TEXT NOT NULL REFERENCES countries(alpha3),
    PRIMARY KEY (plant_id, country_alpha3)
);
```

#### `specimens`

```sql
CREATE TABLE specimens (
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
```

#### `cart_items`

```sql
CREATE TABLE cart_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    specimen_id INTEGER NOT NULL REFERENCES specimens(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL DEFAULT 1,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(session_id, specimen_id)
);
```

#### `users` (unchanged)

Kept as-is from current schema. Not migrated to D1.

### Tables removed

- `products` — replaced by `plants` + `specimens`
- `carousel_slides` — carousel removed per decision

### Slug generation strategy

Slugs are generated from botanical name components:
- Base: `{genus}-{species}` (lowercase)
- Append infraspecific rank if present: `-ssp-{subspecies}`, `-var-{variety}`, `-f-{form}`
- Append cultivar if present: `-{cultivar}` (strip quotes)
- Append field number if present: `-{field_number}`
- Append field location if present: `-{location}` (strip parens)
- Normalize: lowercase, replace spaces with hyphens, remove special characters
- Deduplicate: append `-2`, `-3` etc. for collisions

Examples:
- "Adenia globosa" → `adenia-globosa`
- "Ariocarpus retusus AL 272 (El Refugio, NL)" → `ariocarpus-retusus-al-272-el-refugio-nl`
- "Echeveria 'Lola'" → `echeveria-lola`

---

## Backend and API Refinement

### Recommended public API surface

- `GET /api/plants` — list all plants (with genus/family joined)
- `GET /api/plants/:slug` — plant profile with cultivation, conservation, countries, specimens
- `GET /api/filters` — distinct values for family, genus, vegetation_period, etc.
- `GET /api/cart` — view cart items for session
- `POST /api/cart` — add specimen to cart
- `DELETE /api/cart/:id` — remove item from cart

Optional later endpoints:

- `POST /api/availability-notifications`
- admin-only sync/import endpoints

### Data service interface expansion

Both `ApiDataService.js` and `D1DataService.js` need new methods:

```
getPlants()              → GET /api/plants
getPlant(slug)           → GET /api/plants/:slug
getFilters()             → GET /api/filters
getCart(sessionId)       → GET /api/cart
addToCart(specimenId)    → POST /api/cart
removeFromCart(itemId)   → DELETE /api/cart/:id
```

Old methods to remove: `getProducts()`, `getProduct()`, `getCarouselSlides()`

### Cloudflare Functions to create/replace

| Current | New |
|---|---|
| `functions/api/products/index.js` | `functions/api/plants/index.js` |
| `functions/api/products/[slug].js` | `functions/api/plants/[slug].js` |
| `functions/api/carousel.js` | **Delete** |
| — | `functions/api/filters.js` |
| — | `functions/api/cart/index.js` (GET + POST) |
| — | `functions/api/cart/[id].js` (DELETE) |

### Response-shape recommendation

Plant list item (for index/cards):
```json
{
  "id": 1,
  "slug": "adenia-globosa",
  "display_name": "Adenia globosa",
  "genus": "Adenia",
  "family": "Passifloraceae",
  "vegetation_period": "Summer",
  "specimen_count": 3,
  "for_sale_count": 0,
  "image_url": null
}
```

Plant profile (for detail page):
```json
{
  "id": 1,
  "slug": "adenia-globosa",
  "display_name": "Adenia globosa",
  "genus": "Adenia",
  "family": "Passifloraceae",
  "species": "globosa",
  "author_citation": "Engl.",
  "cultivation": {
    "vegetation_period": "Summer",
    "substrate": "Humus-rich succulent mix",
    "winter_temp_range": ">15 °C",
    "watering": "💧💧💧",
    "exposure": "Full sun to partial shade"
  },
  "conservation": {
    "red_list_status": "Least concern (LC)",
    "red_list_url": "https://...",
    "cites_listing": "None",
    "llifle_url": "https://..."
  },
  "countries": ["Ethiopia", "Kenya", "Somalia", "Tanzania"],
  "notes": null,
  "specimens": [
    {
      "id": 1,
      "specimen_code": "0001-26s01",
      "for_sale": false,
      "price": null,
      "propagation_method": "Seed",
      "propagation_date": "2026-01-04",
      "image_url": null
    }
  ]
}
```

### Local and Cloudflare parity

The current code supports both local Python API and Cloudflare Functions + D1. That is worth preserving. All new endpoints need implementations in both:

- `api_server.py` (local Python)
- `functions/api/` (Cloudflare Pages Functions)

Auth endpoints remain local-only for now (per decision #5).

---

## Import Pipeline Architecture

### Overview

Replace the generic `baserow_to_mysql.py` (single-table export) with a domain-specific `import_baserow.py` that:

1. Fetches all four Baserow tables via REST API
2. Builds in-memory lookup maps for Genus and Country
3. Resolves link_row relationships
4. Extracts single_select values from `{id, value, color}` objects
5. Generates slugs from botanical name components
6. Normalizes Red List typos
7. Inserts into the new schema in dependency order: genera → countries → plants → plant_countries → specimens

### Pipeline design

Single Python script (`import_baserow.py`) with:
- `--yes` flag to skip confirmation (for CI/automation)
- Drops and recreates `dala.db` on each run
- Applies `db/schema.sql` for table creation
- Prints summary of imported counts

Runs once per data sync (not continuous). The old `baserow_to_mysql.py` is preserved for reference but superseded.

### Baserow field ID reference (for import script)

Plant index (746875):
- `field_6297762` = Name (formula), `field_6995221` = ID, `field_6300262` = Species
- `field_6300742` = Subspecies, `field_6300796` = Variety, `field_6300798` = Form, `field_6300802` = Cultivar
- `field_6313656` = Genus (link_row), `field_6319244` = Family (lookup)
- `field_6331303` = Field number, `field_6331304` = Field location
- `field_6297766` = Vegetation period, `field_6360415` = Substrate
- `field_6360425` = Winter rest temp, `field_6376724` = Watering, `field_6410605` = Exposure
- `field_6360427` = Red List, `field_6360459` = Red List URL
- `field_6360475` = CITES, `field_6360469` = LLIFLE URL
- `field_6361735` = Author citation, `field_6365077` = Native to country (link_row)
- `field_6457140` = Notes

Genus (747169):
- `field_6300340` = Genus (single_select), `field_6301600` = Family (single_select)

Plant collection (748062):
- `field_6308470` = Specimen ID (formula), `field_6308471` = Notes
- `field_6308472` = For sale (boolean), `field_6308515` = Name (link_row to plant)
- `field_6308673` = Propagation date, `field_6309007` = Propagation method
- `field_6309023` = Specimen origin, `field_6309031` = Source material origin
- `field_6309034` = Provenance, `field_6319584` = Specimen suffix, `field_6341815` = Image (file)

Country (753691):
- `field_6365193` = English short name, `field_6365194` = Alpha-2, `field_6365195` = Alpha-3

---

## Frontend Reshape Plan

### 1. Reframe the app around plants, not products

Replace the current mental model everywhere in the UI:

- `ProductPage` becomes `PlantProfilePage`
- product cards become plant cards
- related products become related taxa or related specimens
- "Best Sellers" becomes collection/index content

This is more than a rename. The rendered data hierarchy changes from one entity to two:

- plant taxon
- specimen(s)

### 2. Introduce global view mode

Add a top-level gallery/shop mode switch in the header ribbon.

Expected behavior:

- Gallery view emphasizes taxa and education
- Shop view emphasizes saleable specimens and price/availability
- The selected mode should affect:
  - plant index cards
  - plant profile CTA area
  - filtering defaults
  - wording in navigation and section labels

Recommendation:

- Store this in React context or URL query state
- Start with client-side state persisted in local storage
- All data is always fetched; mode controls what is shown (no separate API calls per mode)

### 3. Replace the current navigation with the intended sidebar menu

Current state:

- top nav plus mobile dropdown

Target state:

- menu button in header ribbon
- slide-out sidebar
- pinned by default once opened
- explicit "hide menu" control
- home closes the menu when returning there

Recommendation:

- Build a single navigation system that works on both desktop and mobile
- Treat "pinned" as responsive behavior, not just a visual state

### 4. Build the plant index experience

The plant index is likely the core page of the whole site.

Required features:

- filter by family
- filter by genus
- filter by summer growers
- filter by winter growers
- filter by cacti
- filter by other succulents
- card/list view that works in both gallery and shop mode

Recommendation:

- Start with server-delivered data and client-side filtering
- Move to server-side filtering only if data volume makes it necessary (150 plants is fine client-side)

### 5. Build the plant profile page

Target content:

- full botanical title formatting
- placeholder image (or real image when available)
- cultivation table with all 5 fields and hover popups/tooltips
- geographic distribution (country list)
- conservation status (Red List + CITES)
- external links (LLIFLE, Red List)
- general notes
- specimen list block (visible in shop mode, shows availability)

Botanical-name formatting should be treated as a dedicated rendering concern, not ad hoc string concatenation in components.

### 6. Build the cart page

- View-only cart showing selected specimens
- Session-based (no login required)
- Items persist in session storage + database
- No checkout, payment, or shipping flow

### 7. Replace placeholder static pages

Create real page shells for:

- Shipping & Terms
- FAQ
- About
- Contact

Content for these pages will be provided separately. Implement as route-based pages with hardcoded placeholder text for now.

### 8. Files to create, rename, or delete

**Delete:**
- `frontend/src/components/Carousel.jsx`
- `frontend/src/components/ProductCard.jsx`
- `frontend/src/components/ProductGrid.jsx`
- `frontend/src/pages/ProductPage.jsx`
- `functions/api/products/index.js`
- `functions/api/products/[slug].js`
- `functions/api/carousel.js`

**Create:**
- `frontend/src/components/PlantCard.jsx`
- `frontend/src/components/PlantGrid.jsx`
- `frontend/src/components/CultivationTable.jsx`
- `frontend/src/components/Sidebar.jsx`
- `frontend/src/components/FilterBar.jsx`
- `frontend/src/components/ViewModeToggle.jsx`
- `frontend/src/components/SpecimenList.jsx`
- `frontend/src/components/CartItem.jsx`
- `frontend/src/pages/PlantIndexPage.jsx`
- `frontend/src/pages/PlantProfilePage.jsx`
- `frontend/src/pages/CartPage.jsx`
- `frontend/src/pages/ShippingTermsPage.jsx`
- `frontend/src/pages/FaqPage.jsx`
- `frontend/src/pages/AboutPage.jsx`
- `frontend/src/pages/ContactPage.jsx`
- `frontend/src/services/ViewModeContext.jsx`
- `frontend/src/services/CartContext.jsx`
- `functions/api/plants/index.js`
- `functions/api/plants/[slug].js`
- `functions/api/filters.js`
- `functions/api/cart/index.js`
- `functions/api/cart/[id].js`
- `import_baserow.py`

**Modify:**
- `frontend/src/App.jsx` — new routes
- `frontend/src/main.jsx` — new data service, view mode + cart providers
- `frontend/src/components/Layout.jsx` — sidebar integration
- `frontend/src/components/Header.jsx` — view mode toggle, cart icon, remove carousel
- `frontend/src/components/Footer.jsx` — update links
- `frontend/src/pages/HomePage.jsx` — hero + featured plants (no carousel)
- `frontend/src/services/ApiDataService.js` — new methods
- `frontend/src/services/D1DataService.js` — new methods
- `frontend/src/services/DataContext.jsx` — possibly unchanged
- `frontend/src/style.css` — new component styles
- `api_server.py` — new endpoints
- `db/schema.sql` — new schema
- `db/init_db.py` — new seed data
- `db/migrate_to_d1.sh` — new tables, remove products/carousel
- `TABLES.md` — document new schema
- `CLAUDE.md` — update architecture docs

---

## Design Direction

### Practical design guidance

- Keep the UI intentionally minimal and content-led
- Remove placeholder marketing copy immediately
- Prioritize readability of botanical data and image galleries
- Use a neutral, restrained layout that can evolve later
- Do not spend time polishing an e-commerce visual style before the plant/specimen model is correct

### Specific code-base implications

- `frontend/src/style.css` is currently entirely product-store oriented and heavily placeholder-driven
- It should be refactored around:
  - app shell
  - sidebar
  - filter bar
  - plant card
  - plant profile
  - cultivation table
  - specimen/shop block
  - cart

---

## Authorization and Admin Use

Auth should remain in the architecture, but it should not block the public site reshape. No auth required for browsing. Admin features deferred.

---

## Data Migration Strategy

### Stage A. Stabilize the web schema ✅

Schema designed (see "Target web schema" above).

### Stage B. Map Baserow fields to web schema ✅

Complete field mapping documented (see "Baserow Schema Discovery" above).

### Stage C. Build import transformation

Build `import_baserow.py` (see "Import Pipeline Architecture" above).

### Stage D. Keep local and D1 migration aligned

Update:

- `db/schema.sql` — new schema
- `db/init_db.py` — sample seed data for local dev without Baserow
- `db/migrate_to_d1.sh` — push new schema + data to D1
- `TABLES.md` — document all tables

---

## Recommended Delivery Phases

### Phase 1. Domain-model reset

Goal: remove the product-store assumptions from the architecture

Deliverables:

- new schema design ✅ (documented above)
- Baserow mapping document ✅ (documented above)
- API contract design ✅ (documented above)
- frontend route plan ✅ (documented above)
- `import_baserow.py` script
- `db/schema.sql` rewrite
- `db/init_db.py` rewrite

### Phase 2. Read-only plant site

Goal: launch a proper plant index and plant profile experience without shop mechanics

Deliverables:

- `/plants` and `/plants/:slug` routes
- sidebar navigation
- filter system
- plant profile layout with cultivation table
- static content pages (Shipping, FAQ, About, Contact)
- new data import from Baserow
- updated data services + API endpoints (both local and Cloudflare)

This is the best first usable milestone.

### Phase 3. Shop-mode overlay

Goal: add specimen-aware commercial behavior without distorting the plant-centric structure

Deliverables:

- gallery/shop toggle
- specimen list on plant profile
- price and availability display
- basic view-only cart
- cart API endpoints

### Phase 4. Auth/admin parity

Goal: make authorization genuinely usable across local and production deployments

Deliverables:

- decide whether Cloudflare auth support is required now
- add missing production auth endpoints if needed
- define admin-only functions

### Phase 5. Polish and operational hardening

Goal: improve resilience, maintainability, and presentation quality

Deliverables:

- loading/error states
- better empty states
- real image strategy (when Baserow images are populated)
- testing for import and API contracts
- accessibility pass on sidebar, toggle, filters, and tooltips

---

## Recommendation

Treat this reshape as a domain rewrite on the existing technical skeleton, not as a visual redesign of the current storefront.

The strongest reusable asset in the current code base is the split between:

- frontend SPA
- swappable data services
- local and Cloudflare backends

The weakest part is the current data model. That is where the redesign should start.

## Suggested First Implementation Milestone

"A read-only plant index and plant profile site backed by a new plant/specimen schema imported from Baserow, with sidebar navigation and filtering, but without cart/checkout."

That milestone de-risks the core architecture and preserves room for the later shop overlay.
