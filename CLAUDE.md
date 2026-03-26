# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Dala Succulents is an e-commerce site for selling rare succulents. A React SPA (Vite) fetches data dynamically from a Python API server backed by SQLite. The data-fetching layer is injectable so a Cloudflare D1 backend can replace the Python server in production.

## Commands

```bash
# Setup (Python)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Setup (Frontend)
cd frontend && npm install

# Initialize database with seed data
python db/init_db.py

# Development — run both in separate terminals:
python api_server.py              # API server on port 8000
cd frontend && npm run dev        # Vite dev server on port 3000 (proxies /api → 8000)

# Production build (outputs to dist/)
cd frontend && npm run build

# Serve production build (API + static from dist/)
python api_server.py

# Import data from Baserow CMS (requires .env with BASEROW_API_TOKEN and BASEROW_TABLE_ID)
python baserow_to_mysql.py

# Cloudflare D1 — create database (one-time)
wrangler d1 create dala-succulents-db  # then paste database_id into wrangler.toml

# Cloudflare D1 — migrate schema + data from local dala.db
bash db/migrate_to_d1.sh

# Cloudflare Pages — local preview with D1
cd frontend && npm run build && cd .. && wrangler pages dev dist

# Cloudflare Pages — deploy to production
cd frontend && npm run build && cd .. && wrangler pages deploy dist
```

## Architecture

**React SPA** — `frontend/` contains a Vite + React app with React Router for client-side routing. All data is fetched from the API at runtime.

- `frontend/src/main.jsx` — Entry point: BrowserRouter + DataProvider + App
- `frontend/src/App.jsx` — Routes: `/` → HomePage, `/products/:slug` → ProductPage
- `frontend/src/services/ApiDataService.js` — Fetch-based data service (baseUrl configurable via `VITE_API_BASE_URL` env var). Factory function returns `{ getProducts, getProduct, getCarouselSlides }`.
- `frontend/src/services/D1DataService.js` — Cloudflare D1 data service with edge caching headers. Same interface as ApiDataService.
- `frontend/src/services/DataContext.jsx` — React context + DataProvider + useDataService hook. Allows swapping the data service implementation (e.g., for Cloudflare D1).
- `frontend/src/components/` — Layout, Header, Footer, Carousel, ProductCard, ProductGrid, Breadcrumb
- `frontend/src/pages/` — HomePage (carousel + product grid), ProductPage (detail + related products)
- `frontend/src/style.css` — All styles (copied from `static/style.css`). Uses CSS variables, responsive grid (breakpoints at 600px, 900px).
- `frontend/vite.config.js` — Dev server on port 3000, proxies `/api` to localhost:8000, builds to `../dist/`.

**API Server** — `api_server.py` serves REST endpoints and static files from `dist/` with SPA fallback (serves `index.html` for unmatched paths).

- `api_server.py` — REST API (`/api/products`, `/api/products/<slug>`, `/api/carousel`) + SPA fallback for client-side routing
- `db/init_db.py` — Seeds SQLite with sample products and carousel data
- `baserow_to_mysql.py` — Pulls data from Baserow cloud CMS into SQLite. Configured via `.env`.
- `static/style.css` — Source of truth for styles (copied into `frontend/src/` during setup)
- `dist/` — Vite build output, not committed. In production, served by `api_server.py`.

**Cloudflare Pages + D1** — Production deployment uses Cloudflare Pages Functions backed by D1.

- `functions/api/products/index.js` — `GET /api/products` (lists all products)
- `functions/api/products/[slug].js` — `GET /api/products/:slug` (single product by slug)
- `functions/api/carousel.js` — `GET /api/carousel` (carousel slides)
- `wrangler.toml` — Pages config with D1 binding (`DB`)
- `db/migrate_to_d1.sh` — Migrates local dala.db schema + data to remote D1
- `frontend/.env.development` / `.env.production` — `VITE_DATA_BACKEND` controls service selection (`local` or `cloudflare`)
- `frontend/src/main.jsx` — Switches between `ApiDataService` (local) and `D1DataService` (cloudflare) based on env var

**Database tables**: `products` (id, name, slug, scientific_name, description, price, image_url, image_url_large, sold_out, sort_order) and `carousel_slides` (id, image_url, heading, subheading, button_text, button_link, sort_order).

## Database Documentation

When `dala.db` schema changes (new tables, altered columns, seed data changes), update `TABLES.md` to match. This includes changes made via `db/schema.sql`, `db/init_db.py`, or `baserow_to_mysql.py`.

## Style Notes

- Font is Comic Sans MS — this is intentional.
- Color scheme uses green (#4a7c59) with warm whites.
- CSS class names in React components must match `static/style.css` exactly.
