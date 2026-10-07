# Scrape API Platform

A FastAPI platform that turns **public or authorized webpages** into normalized, continuously refreshable API data.

## What it does

User flow:

1. Register/login.
2. Submit a source URL.
3. The crawler discovers sitemap URLs and same-origin links.
4. It extracts page metadata, visible text, links, images, JSON-LD and OpenGraph/meta fields.
5. JavaScript-rendered public pages can use a Playwright browser fallback.
6. Results are stored in the database.
7. The user receives an API key.
8. Their app/website calls `/v1/data/{source_id}` with `X-API-Key`.
9. A persistent deployment can refresh sources on a schedule.

## Safety and scope

Use this only for websites/content you are authorized to access. The scraper does **not** bypass authentication, DRM, paywalls, CAPTCHA/anti-bot controls, access restrictions, or protected media delivery.

## Main endpoints

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/keys`
- `POST /scrape`
- `POST /scrape/sources`
- `GET /scrape/sources`
- `POST /scrape/sources/{source_id}/refresh`
- `GET /v1/data?url=...`
- `GET /v1/data/{source_id}`
- `GET /health`
- `GET /docs`

## Install

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env
uvicorn app.main:app --reload
```

## Production refresh

For an always-running service, deploy FastAPI behind a process manager and run a durable scheduler/worker that periodically calls the source refresh operation. SQLite is suitable for development; PostgreSQL is recommended for production.

## Example API call

```bash
curl -H "X-API-Key: sk_..." "https://YOUR-DOMAIN/v1/data/1"
```

The response contains the normalized source object and all crawled page records currently stored for that source.
