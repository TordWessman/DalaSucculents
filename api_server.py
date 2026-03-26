#!/usr/bin/env python3
"""Backend that serves REST API (D1-style JSON), auth endpoints, and static files from dist/."""

import datetime
import json
import os
import sqlite3
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

import jwt
from dotenv import load_dotenv
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'dala.db')
DIST_DIR = os.path.join(BASE_DIR, 'dist')
PORT = 8000

GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
JWT_SECRET = os.environ.get('JWT_SECRET', 'dev-secret-change-me')
ADMIN_EMAILS = [e.strip() for e in os.environ.get('ADMIN_EMAILS', '').split(',') if e.strip()]
CORS_ORIGIN = os.environ.get('CORS_ORIGIN', 'http://localhost:3000')


def dict_factory(cursor, row):
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = dict_factory
    return conn


def create_session_token(user_id, email, role):
    payload = {
        'user_id': user_id,
        'email': email,
        'role': role,
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')


def verify_session_token(token):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def parse_cookie(cookie_header):
    """Parse a Cookie header string into a dict."""
    cookies = {}
    if cookie_header:
        for item in cookie_header.split(';'):
            item = item.strip()
            if '=' in item:
                key, val = item.split('=', 1)
                cookies[key.strip()] = val.strip()
    return cookies


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
        elif path == '/api/auth/me':
            self._serve_auth_me()
        else:
            # SPA fallback: serve index.html for paths that don't match a real file
            file_path = os.path.join(DIST_DIR, path.lstrip('/'))
            if not os.path.isfile(file_path):
                self.path = '/index.html'
            super().do_GET()

    def do_POST(self):
        path = urlparse(self.path).path

        if path == '/api/auth/login':
            self._handle_auth_login()
        elif path == '/api/auth/logout':
            self._handle_auth_logout()
        else:
            self._send_json({"error": "Not found", "success": False}, status=404)

    def _read_body(self):
        length = int(self.headers.get('Content-Length', 0))
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length))

    def _send_json(self, data, status=200, extra_headers=None):
        body = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self._send_cors_headers()
        if extra_headers:
            for key, val in extra_headers:
                self.send_header(key, val)
        self.end_headers()
        self.wfile.write(body)

    def _send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', CORS_ORIGIN)
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Allow-Credentials', 'true')

    def do_OPTIONS(self):
        self.send_response(204)
        self._send_cors_headers()
        self.end_headers()

    def end_headers(self):
        # Don't add duplicate CORS headers — _send_json and do_OPTIONS handle them
        super().end_headers()

    def _get_session_user(self):
        """Return decoded JWT payload from session cookie, or None."""
        cookie_header = self.headers.get('Cookie', '')
        cookies = parse_cookie(cookie_header)
        token = cookies.get('session')
        if not token:
            return None
        return verify_session_token(token)

    # --- Auth endpoints ---

    def _handle_auth_login(self):
        try:
            body = self._read_body()
            credential = body.get('credential')
            if not credential:
                self._send_json({"error": "Missing credential", "success": False}, status=400)
                return

            idinfo = id_token.verify_oauth2_token(
                credential, google_requests.Request(), GOOGLE_CLIENT_ID
            )

            google_id = idinfo['sub']
            email = idinfo['email']
            name = idinfo.get('name', '')
            picture = idinfo.get('picture', '')
            role = 'admin' if email in ADMIN_EMAILS else 'user'

            conn = get_db()
            conn.execute('''
                INSERT INTO users (google_id, email, name, picture_url, role, last_login)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(google_id) DO UPDATE SET
                    email = excluded.email,
                    name = excluded.name,
                    picture_url = excluded.picture_url,
                    role = excluded.role,
                    last_login = CURRENT_TIMESTAMP
            ''', (google_id, email, name, picture, role))
            conn.commit()

            user = conn.execute('SELECT * FROM users WHERE google_id = ?', (google_id,)).fetchone()
            conn.close()

            token = create_session_token(user['id'], email, role)
            cookie = f"session={token}; HttpOnly; SameSite=Lax; Path=/; Max-Age=604800"

            self._send_json({
                "success": True,
                "user": {"id": user['id'], "email": email, "name": name, "picture_url": picture, "role": role}
            }, extra_headers=[('Set-Cookie', cookie)])

        except ValueError as e:
            self._send_json({"error": f"Invalid token: {e}", "success": False}, status=401)

    def _handle_auth_logout(self):
        cookie = "session=; HttpOnly; SameSite=Lax; Path=/; Max-Age=0"
        self._send_json({"success": True}, extra_headers=[('Set-Cookie', cookie)])

    def _serve_auth_me(self):
        payload = self._get_session_user()
        if not payload:
            self._send_json({"success": True, "user": None})
            return

        conn = get_db()
        user = conn.execute('SELECT id, email, name, picture_url, role FROM users WHERE id = ?',
                            (payload['user_id'],)).fetchone()
        conn.close()

        self._send_json({"success": True, "user": user})

    # --- Data endpoints ---

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

    if not GOOGLE_CLIENT_ID:
        print("Warning: GOOGLE_CLIENT_ID not set — Google auth will not work")

    server = HTTPServer(('', PORT), DalaHandler)
    print(f"Serving on http://localhost:{PORT}")
    print(f"  API: /api/products, /api/products/<slug>, /api/carousel")
    print(f"  Auth: /api/auth/login, /api/auth/logout, /api/auth/me")
    print(f"  Static files from: {DIST_DIR}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()


if __name__ == '__main__':
    main()
