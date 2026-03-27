#!/usr/bin/env python3
"""Backend that serves REST API (D1-style JSON), auth endpoints, and static files from dist/."""

import datetime
import email.parser
import json
import os
import re
import sqlite3
import uuid
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

import boto3
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

R2_ACCOUNT_ID = os.environ.get('R2_ACCOUNT_ID', '')
R2_ACCESS_KEY_ID = os.environ.get('R2_ACCESS_KEY_ID', '')
R2_SECRET_ACCESS_KEY = os.environ.get('R2_SECRET_ACCESS_KEY', '')
R2_BUCKET_NAME = os.environ.get('R2_BUCKET_NAME', 'dala-succulents-images')
R2_PUBLIC_URL = os.environ.get('R2_PUBLIC_URL', '')

ALLOWED_IMAGE_TYPES = {'image/jpeg', 'image/png', 'image/webp'}
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB


def get_r2_client():
    return boto3.client(
        's3',
        endpoint_url=f'https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com',
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        region_name='auto',
    )


def parse_multipart(content_type, body):
    """Parse multipart/form-data using email.parser (Python 3.13 compatible)."""
    header = f'Content-Type: {content_type}\r\n\r\n'
    msg = email.parser.BytesParser().parsebytes(header.encode() + body)
    parts = {}
    for part in msg.walk():
        name = part.get_param('name', header='content-disposition')
        if name:
            if part.get_content_type().startswith('image/') or part.get_filename():
                parts[name] = {
                    'data': part.get_payload(decode=True),
                    'content_type': part.get_content_type(),
                    'filename': part.get_filename() or 'upload',
                }
            else:
                parts[name] = part.get_payload(decode=True).decode('utf-8', errors='replace')
    return parts


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

        # Match /api/plants/:slug/images
        images_match = re.match(r'^/api/plants/([^/]+)/images/?$', path)
        if path == '/api/plants':
            self._serve_plants()
        elif images_match:
            self._serve_plant_images(images_match.group(1))
        elif path.startswith('/api/plants/'):
            slug = path.split('/api/plants/')[1].rstrip('/')
            self._serve_plant(slug)
        elif path == '/api/filters':
            self._serve_filters()
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

        images_match = re.match(r'^/api/plants/([^/]+)/images/?$', path)
        if path == '/api/auth/login':
            self._handle_auth_login()
        elif path == '/api/auth/logout':
            self._handle_auth_logout()
        elif images_match:
            self._handle_image_upload(images_match.group(1))
        else:
            self._send_json({"error": "Not found", "success": False}, status=404)

    def do_DELETE(self):
        path = urlparse(self.path).path

        delete_match = re.match(r'^/api/plants/([^/]+)/images/(\d+)/?$', path)
        if delete_match:
            self._handle_image_delete(delete_match.group(1), int(delete_match.group(2)))
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
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
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

    def _serve_plants(self):
        conn = get_db()
        rows = conn.execute('''
            SELECT p.id, p.slug,
                   CASE
                       WHEN p.subspecies IS NOT NULL THEN g.name || ' ' || p.species || ' subsp. ' || p.subspecies
                       WHEN p.variety IS NOT NULL THEN g.name || ' ' || p.species || ' var. ' || p.variety
                       WHEN p.form IS NOT NULL THEN g.name || ' ' || p.species || ' f. ' || p.form
                       WHEN p.cultivar IS NOT NULL THEN g.name || ' ' || p.species || ' ' || char(39) || p.cultivar || char(39)
                       ELSE g.name || ' ' || p.species
                   END AS display_name,
                   g.name AS genus, g.family,
                   p.vegetation_period,
                   COUNT(s.id) AS specimen_count,
                   SUM(CASE WHEN s.for_sale = 1 THEN 1 ELSE 0 END) AS for_sale_count,
                   (SELECT s2.image_url FROM specimens s2 WHERE s2.plant_id = p.id AND s2.image_url IS NOT NULL LIMIT 1) AS image_url
            FROM plants p
            JOIN genera g ON g.id = p.genus_id
            LEFT JOIN specimens s ON s.plant_id = p.id
            GROUP BY p.id
            ORDER BY p.sort_order, g.name, p.species
        ''').fetchall()
        conn.close()
        self._send_json({"results": rows, "success": True})

    def _serve_plant(self, slug):
        conn = get_db()
        plant = conn.execute('''
            SELECT p.*, g.name AS genus, g.family
            FROM plants p
            JOIN genera g ON g.id = p.genus_id
            WHERE p.slug = ?
        ''', (slug,)).fetchone()
        if not plant:
            conn.close()
            self._send_json({"error": "Not found", "success": False}, status=404)
            return

        # Build display_name
        display_name = plant['genus'] + ' ' + plant['species']
        if plant.get('subspecies'):
            display_name += ' subsp. ' + plant['subspecies']
        elif plant.get('variety'):
            display_name += ' var. ' + plant['variety']
        elif plant.get('form'):
            display_name += ' f. ' + plant['form']
        elif plant.get('cultivar'):
            display_name += " '" + plant['cultivar'] + "'"

        countries = [r['name'] for r in conn.execute('''
            SELECT c.name FROM plant_countries pc
            JOIN countries c ON c.alpha3 = pc.country_alpha3
            WHERE pc.plant_id = ?
            ORDER BY c.name
        ''', (plant['id'],)).fetchall()]

        specimens = conn.execute('''
            SELECT id, specimen_code, for_sale, price, propagation_method,
                   propagation_date, image_url
            FROM specimens WHERE plant_id = ?
            ORDER BY specimen_code
        ''', (plant['id'],)).fetchall()
        for sp in specimens:
            sp['for_sale'] = bool(sp['for_sale'])

        images = conn.execute('''
            SELECT id, image_url, caption, sort_order
            FROM plant_images WHERE plant_id = ?
            ORDER BY sort_order, id
        ''', (plant['id'],)).fetchall()

        conn.close()

        result = {
            "id": plant['id'],
            "slug": plant['slug'],
            "display_name": display_name,
            "genus": plant['genus'],
            "family": plant['family'],
            "species": plant['species'],
            "author_citation": plant.get('author_citation'),
            "cultivation": {
                "vegetation_period": plant.get('vegetation_period'),
                "substrate": plant.get('substrate'),
                "winter_temp_range": plant.get('winter_temp_range'),
                "watering": plant.get('watering'),
                "exposure": plant.get('exposure'),
            },
            "conservation": {
                "red_list_status": plant.get('red_list_status'),
                "red_list_url": plant.get('red_list_url'),
                "cites_listing": plant.get('cites_listing'),
                "llifle_url": plant.get('llifle_url'),
            },
            "countries": countries,
            "notes": plant.get('notes'),
            "specimens": specimens,
            "images": images,
        }
        self._send_json({"result": result, "success": True})

    def _serve_plant_images(self, slug):
        conn = get_db()
        plant = conn.execute('SELECT id FROM plants WHERE slug = ?', (slug,)).fetchone()
        if not plant:
            conn.close()
            self._send_json({"error": "Not found", "success": False}, status=404)
            return
        images = conn.execute('''
            SELECT id, image_url, caption, sort_order
            FROM plant_images WHERE plant_id = ?
            ORDER BY sort_order, id
        ''', (plant['id'],)).fetchall()
        conn.close()
        self._send_json({"results": images, "success": True})

    def _handle_image_upload(self, slug):
        user = self._get_session_user()
        if not user or user.get('role') != 'admin':
            self._send_json({"error": "Forbidden", "success": False}, status=403)
            return

        content_type = self.headers.get('Content-Type', '')
        if not content_type.startswith('multipart/form-data'):
            self._send_json({"error": "Expected multipart/form-data", "success": False}, status=400)
            return

        length = int(self.headers.get('Content-Length', 0))
        if length > MAX_IMAGE_SIZE:
            self._send_json({"error": "File too large (max 10 MB)", "success": False}, status=413)
            return

        body = self.rfile.read(length)
        parts = parse_multipart(content_type, body)

        file_part = parts.get('file')
        if not file_part or not isinstance(file_part, dict):
            self._send_json({"error": "Missing file", "success": False}, status=400)
            return

        if file_part['content_type'] not in ALLOWED_IMAGE_TYPES:
            self._send_json({"error": "Invalid image type (jpeg/png/webp only)", "success": False}, status=400)
            return

        caption = parts.get('caption', '') if isinstance(parts.get('caption'), str) else ''

        conn = get_db()
        plant = conn.execute('SELECT id FROM plants WHERE slug = ?', (slug,)).fetchone()
        if not plant:
            conn.close()
            self._send_json({"error": "Plant not found", "success": False}, status=404)
            return

        ext = file_part['content_type'].split('/')[-1]
        if ext == 'jpeg':
            ext = 'jpg'
        key = f"dev/plants/{plant['id']}/{uuid.uuid4()}.{ext}"

        try:
            r2 = get_r2_client()
            r2.put_object(
                Bucket=R2_BUCKET_NAME,
                Key=key,
                Body=file_part['data'],
                ContentType=file_part['content_type'],
            )
        except Exception as e:
            conn.close()
            self._send_json({"error": f"Upload failed: {e}", "success": False}, status=500)
            return

        image_url = f"{R2_PUBLIC_URL}/{key}"
        conn.execute(
            'INSERT INTO plant_images (plant_id, image_url, caption) VALUES (?, ?, ?)',
            (plant['id'], image_url, caption),
        )
        conn.commit()
        image = conn.execute(
            'SELECT id, image_url, caption, sort_order FROM plant_images WHERE rowid = last_insert_rowid()'
        ).fetchone()
        conn.close()

        self._send_json({"result": image, "success": True}, status=201)

    def _handle_image_delete(self, slug, image_id):
        user = self._get_session_user()
        if not user or user.get('role') != 'admin':
            self._send_json({"error": "Forbidden", "success": False}, status=403)
            return

        conn = get_db()
        plant = conn.execute('SELECT id FROM plants WHERE slug = ?', (slug,)).fetchone()
        if not plant:
            conn.close()
            self._send_json({"error": "Plant not found", "success": False}, status=404)
            return

        image = conn.execute(
            'SELECT id, image_url FROM plant_images WHERE id = ? AND plant_id = ?',
            (image_id, plant['id']),
        ).fetchone()
        if not image:
            conn.close()
            self._send_json({"error": "Image not found", "success": False}, status=404)
            return

        # Extract R2 key from URL
        r2_key = image['image_url'].replace(R2_PUBLIC_URL + '/', '') if R2_PUBLIC_URL else None
        if r2_key:
            try:
                r2 = get_r2_client()
                r2.delete_object(Bucket=R2_BUCKET_NAME, Key=r2_key)
            except Exception:
                pass  # best-effort R2 cleanup

        conn.execute('DELETE FROM plant_images WHERE id = ?', (image_id,))
        conn.commit()
        conn.close()
        self._send_json({"success": True})

    def _serve_filters(self):
        conn = get_db()
        families = [r['family'] for r in conn.execute(
            'SELECT DISTINCT family FROM genera ORDER BY family').fetchall()]
        genus_names = [r['name'] for r in conn.execute(
            'SELECT DISTINCT name FROM genera ORDER BY name').fetchall()]
        vegetation_periods = [r['vegetation_period'] for r in conn.execute(
            'SELECT DISTINCT vegetation_period FROM plants WHERE vegetation_period IS NOT NULL ORDER BY vegetation_period').fetchall()]
        exposures = [r['exposure'] for r in conn.execute(
            'SELECT DISTINCT exposure FROM plants WHERE exposure IS NOT NULL ORDER BY exposure').fetchall()]
        conn.close()
        self._send_json({
            "family": families,
            "genus": genus_names,
            "vegetation_period": vegetation_periods,
            "exposure": exposures,
            "success": True
        })


def main():
    if not os.path.exists(DB_PATH):
        print(f"Error: {DB_PATH} not found. Run: python db/init_db.py")
        return

    os.makedirs(DIST_DIR, exist_ok=True)

    if not GOOGLE_CLIENT_ID:
        print("Warning: GOOGLE_CLIENT_ID not set — Google auth will not work")

    server = HTTPServer(('', PORT), DalaHandler)
    print(f"Serving on http://localhost:{PORT}")
    print(f"  API: /api/plants, /api/plants/<slug>, /api/filters")
    print(f"  Auth: /api/auth/login, /api/auth/logout, /api/auth/me")
    print(f"  Static files from: {DIST_DIR}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()


if __name__ == '__main__':
    main()
