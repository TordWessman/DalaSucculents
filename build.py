#!/usr/bin/env python3
"""Build the Dala Succulents static site from SQLite + Jinja2 templates."""

import os
import shutil
import sqlite3

from jinja2 import Environment, FileSystemLoader

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'dala.db')
DIST_DIR = os.path.join(BASE_DIR, 'dist')
STATIC_SRC = os.path.join(BASE_DIR, 'static')
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')


def dict_factory(cursor, row):
    """Convert sqlite3 rows to dicts."""
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))


def format_price(value):
    return f"${value:.2f}"


def load_data(conn):
    products = conn.execute('SELECT * FROM products ORDER BY sort_order').fetchall()
    slides = conn.execute('SELECT * FROM carousel_slides ORDER BY sort_order').fetchall()
    return products, slides


def build():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = dict_factory
    products, slides = load_data(conn)
    conn.close()

    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), autoescape=False)
    env.filters['format_price'] = format_price

    # Clean dist
    if os.path.exists(DIST_DIR):
        shutil.rmtree(DIST_DIR)
    os.makedirs(DIST_DIR)
    os.makedirs(os.path.join(DIST_DIR, 'products'))
    os.makedirs(os.path.join(DIST_DIR, 'static'))

    # Copy static assets
    for fname in os.listdir(STATIC_SRC):
        shutil.copy2(os.path.join(STATIC_SRC, fname), os.path.join(DIST_DIR, 'static', fname))

    # Render index.html
    home_tmpl = env.get_template('home.html')
    index_html = home_tmpl.render(products=products, slides=slides, static_prefix='')
    with open(os.path.join(DIST_DIR, 'index.html'), 'w') as f:
        f.write(index_html)
    print('Built: dist/index.html')

    # Render product pages
    product_tmpl = env.get_template('product.html')
    for product in products:
        # Pick up to 3 related products (excluding current)
        related = [p for p in products if p['id'] != product['id']][:3]
        html = product_tmpl.render(product=product, related=related, static_prefix='../')
        path = os.path.join(DIST_DIR, 'products', f"{product['slug']}.html")
        with open(path, 'w') as f:
            f.write(html)
        print(f"Built: dist/products/{product['slug']}.html")

    print(f"\nDone! {1 + len(products)} pages generated.")


if __name__ == '__main__':
    build()
