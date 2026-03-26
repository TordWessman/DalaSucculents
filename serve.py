#!/usr/bin/env python3
"""Local dev server for the Dala Succulents static site."""

import http.server
import os
import functools

PORT = 8000
DIST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dist')

handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=DIST_DIR)

print(f"Serving dist/ at http://localhost:{PORT}")
print("Press Ctrl+C to stop.")
http.server.HTTPServer(('', PORT), handler).serve_forever()
