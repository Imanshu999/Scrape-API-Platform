# Scrape API Platform

A FastAPI service for extracting public/authorized webpage metadata and exposing normalized results through API keys.

## Scope
This project is intended for websites and content you are authorized to access. It does not bypass authentication, DRM, paywalls, CAPTCHA/anti-bot controls, or expose protected media streams.

## Features
- API-key registration and revocation
- JWT-protected management endpoints
- Public scrape endpoint
- Cached normalized page metadata
- SSRF protections for private/local network targets
- Rate limiting
- SQLite by default, PostgreSQL via DATABASE_URL
- Playwright fallback for JavaScript-rendered public pages
- Docker support

## Quick start

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`.

For browser rendering:

```bash
playwright install chromium
```

See the API docs for authentication and scraping examples.
