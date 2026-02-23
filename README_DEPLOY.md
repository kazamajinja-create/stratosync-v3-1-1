# STRATOSYNC v3.1 Commercial No-Code (B Rebuild)

This package is a clean rebuild that is ready for Render deployment with:
- Optional Postgres persistence (recommended)
- Stripe subscription gate (Price ID based, amounts live in Stripe)
- Auto bootstrap on startup (DB init + env validation)

## Quick start (local)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 10000
```

## Render deployment ("deploy only" demo)
1) Create a new Render Web Service using this repo/zip.
2) Deploy.

By default, billing is **disabled** (`ENABLE_BILLING=0`) and the service will
run with a local SQLite DB (./data/local.db) with zero configuration.

## Render deployment (commercial / billing on)
1) Set env vars in Render:
- ENABLE_BILLING=1
- STRIPE_SECRET_KEY
- STRIPE_WEBHOOK_SECRET
- PRICE_ID_PROFESSIONAL
- PRICE_ID_ENTERPRISE
- DATABASE_URL (Render Postgres recommended)

2) Deploy. Startup will auto-init DB.

## Billing (MVP endpoints)
- POST /billing/create-checkout-session?plan_key=professional&company_name=...
- POST /billing/webhook

## v3 Analyze
- POST /v3/analyze?company_id=1  with JSON payload.
Note: Engine integration is currently a structured placeholder hook. Plug STRATOSYNC core engine into `app/core_engine/analyzer.py`.

## No-code industry template growth
Drop a new folder under:
`industry_packs_runtime/<industry_id>/` with `manifest.json`.
On startup, the service auto-generates:
`industry_packs_runtime/registry.json`.
