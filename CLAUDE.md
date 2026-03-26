# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Dala Succulents is a static e-commerce site for selling rare succulents. A Python build system generates static HTML from SQLite data and Jinja2 templates.

## Commands

```bash
# Setup
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Initialize database with seed data
python db/init_db.py

# Build static site (outputs to dist/)
python build.py

# Run dev server on port 8000 (serves dist/)
python serve.py

# Import data from Baserow CMS (requires .env with BASEROW_API_TOKEN and BASEROW_TABLE_ID)
python baserow_to_mysql.py
```

## Architecture

**Static site generator** — no runtime server. `build.py` reads from SQLite (`dala.db`), renders Jinja2 templates, and writes HTML/CSS/JS to `dist/`.

- `build.py` — Main build script. Queries products and carousel_slides tables, renders `templates/home.html` and individual `templates/product.html` pages, copies `static/` assets to `dist/`.
- `db/init_db.py` — Seeds SQLite with sample products and carousel data.
- `baserow_to_mysql.py` — Pulls data from Baserow cloud CMS into SQLite. Configured via `.env`.
- `templates/` — Jinja2 templates. `base.html` is the layout; `home.html` and `product.html` extend it.
- `static/` — CSS and JS served as-is. `style.css` uses CSS variables, responsive grid (breakpoints at 600px, 900px). `main.js` handles carousel and mobile menu.
- `dist/` — Generated output, not committed. Deploy this directory to any static host.

**Database tables**: `products` (id, name, slug, scientific_name, description, price, image_url, image_url_large, sold_out, sort_order) and `carousel_slides` (id, image_url, heading, subheading, button_text, button_link, sort_order).

## Style Notes

- Font is Comic Sans MS — this is intentional.
- Color scheme uses green (#4a7c59) with warm whites.
