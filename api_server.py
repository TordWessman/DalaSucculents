#!/usr/bin/env python3
"""Mock backend that serves REST API (D1-style JSON) and static files from dist/."""

import json
import os
import sqlite3
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'dala.db')
DIST_DIR = os.path.join(BASE_DIR, 'dist')
PORT = 8000


def dict_factory(cursor, row):
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = dict_factory
    return conn


class DalaHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIST_DIR, **kwargs)

    def do_GET(self):
        path = urlparse(self.path).path

        if path == '/api/products':
            self._serve_products()
        elif path.startswith('/api/products/'):
            slug = path.split('/api/products/')[1].rstrip('/')
            self._serve_product(slug)
        elif path == '/api/carousel':
            self._serve_carousel()
        else:
            # SPA fallback: serve index.html for paths that don't match a real file
            file_path = os.path.join(DIST_DIR, path.lstrip('/'))
            if not os.path.isfile(file_path):
                self.path = '/index.html'
            super().do_GET()

    def _send_json(self, data, status=200):
        body = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def _send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        self.send_response(204)
        self._send_cors_headers()
        self.end_headers()

    def end_headers(self):
        if not hasattr(self, '_cors_sent'):
            self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

    def _serve_products(self):
        conn = get_db()
        products = conn.execute('SELECT * FROM products ORDER BY sort_order').fetchall()
        conn.close()
        self._send_json({"results": products, "success": True})

    def _serve_product(self, slug):
        conn = get_db()
        product = conn.execute('SELECT * FROM products WHERE slug = ?', (slug,)).fetchone()
        conn.close()
        if product:
            self._send_json({"result": product, "success": True})
        else:
            self._send_json({"error": "Not found", "success": False}, status=404)

    def _serve_carousel(self):
        conn = get_db()
        slides = conn.execute('SELECT * FROM carousel_slides ORDER BY sort_order').fetchall()
        conn.close()
        self._send_json({"results": slides, "success": True})


def main():
    if not os.path.exists(DB_PATH):
        print(f"Error: {DB_PATH} not found. Run: python db/init_db.py")
        return

    os.makedirs(DIST_DIR, exist_ok=True)

    server = HTTPServer(('', PORT), DalaHandler)
    print(f"Serving on http://localhost:{PORT}")
    print(f"  API: /api/products, /api/products/<slug>, /api/carousel")
    print(f"  Static files from: {DIST_DIR}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()


if __name__ == '__main__':
    main()
