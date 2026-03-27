# Installation Guide

## Prerequisites

- Python 3
- Node.js and npm
- Wrangler CLI (`npm install -g wrangler`) — for Cloudflare deployment

## Initial Setup

```bash
# Clone the repo
git clone <repo-url> && cd DalaSucculents

# Python virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Frontend dependencies
cd frontend && npm install && cd ..

# Environment variables
cp .env.example .env
```

Edit `.env` and fill in the values. See `.env.example` for the full list of variables. For Google OAuth setup, see [Appendix A](#appendix-a-google-oauth-client-id-setup).

## Database Setup

### Local (SQLite)

```bash
python db/init_db.py
```

### Cloudflare D1 (production)

```bash
wrangler d1 create dala-succulents-db
```

Copy the `database_id` from the output into `wrangler.toml`, then migrate:

```bash
bash db/migrate_to_d1.sh
```

## Development

Run both in separate terminals:

```bash
# Terminal 1 — API server on port 8000
python api_server.py

# Terminal 2 — Vite dev server on port 3000 (proxies /api to 8000)
cd frontend && npm run dev
```

## Deployment

```bash
# Build frontend
cd frontend && npm run build && cd ..

# Deploy to Cloudflare Pages
wrangler pages deploy dist

# Migrate database to D1 (if schema/data changed)
bash db/migrate_to_d1.sh
```

---

## Appendix A: Google OAuth Client ID Setup

1. Go to **console.cloud.google.com**
2. Create a new project (or select an existing one)
3. In the left sidebar, go to **APIs & Services** → **Credentials**
4. Click **+ Create Credentials** → **OAuth client ID**
5. If prompted, configure the **OAuth consent screen** — choose "External", fill in the app name and support contact email, and save
6. Back on the credentials page, click **+ Create Credentials** → **OAuth client ID**
7. For **Application type**, choose **Web application**
8. Give it a name
9. Under **Authorized redirect URIs**, add your callback URLs:
   - Production: `https://<your-domain>/auth/callback`
   - Local dev: `http://localhost:8000/auth/callback`
10. Click **Create**

Save the **Client ID** and **Client Secret**. Add the Client ID to your `.env` as `GOOGLE_CLIENT_ID`.

Note: while the consent screen is in "Testing" status, only users you explicitly add as test users can authenticate. Add yourself under **OAuth consent screen** → **Test users**.

## Appendix B: Cloudflare DNS Configuration

### If your domain is already on Cloudflare:

1. Go to **Cloudflare Pages** → your project → **Custom domains** tab
2. Click **Set up a custom domain**
3. Enter your domain
4. Cloudflare will automatically add the CNAME record and provision an SSL certificate

You can also add `www.<your-domain>` as a second custom domain.

### If your domain is NOT yet on Cloudflare:

1. Add your domain at dash.cloudflare.com → **Add a Site**
2. Pick a plan (Free works)
3. Cloudflare will scan existing DNS records — review and confirm
4. Change your nameservers at your registrar to the two Cloudflare nameservers shown
5. Wait for propagation (usually minutes, up to 48 hours)
6. Once active, follow the steps above to add the custom domain to your Pages project

### Key details

- The CNAME record points your domain to `<your-project>.pages.dev`
- Cloudflare handles SSL automatically
- For `www` → apex redirect (or vice versa), add a **Redirect Rule** under your domain's settings
