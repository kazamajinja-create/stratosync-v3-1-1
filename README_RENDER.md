# Render one-click (Blueprint) deploy

This repo supports Render Blueprint deploy via `render.yaml`.

## Steps (no-code)

1. In Render Dashboard → **Blueprints** → **New Blueprint Instance**
2. Select this GitHub repo.
3. Click **Apply**.
4. After deploy is Live, open:
   - `https://<service>.onrender.com/health`
   - `https://<service>.onrender.com/docs`

## Auth key (API_KEY)

Render will auto-generate `API_KEY`. For protected endpoints, pass:
- Header: `X-API-Key: <API_KEY value from Render env vars>`

## Billing

Billing is disabled by default (`ENABLE_BILLING=false`). Enable only after setting Stripe secrets.


## Strict DB boot

By default `STRICT_DB_BOOT=false` to avoid deploy failures while Postgres is starting.
Set `STRICT_DB_BOOT=true` later if you want startup to fail fast on DB errors.
