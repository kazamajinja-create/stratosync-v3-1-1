# STRATOSYNC v3.1.1 — Render One-Click (No‑Code) Deployment

## What you get
- HTML UI: `/demo` (single-screen input → PDF output)
- Health check: `/health`
- API (v3 runtime): `/v3/analyze` (used by the demo flow)
- Auto template install:
  - Drop `*.zip` into `industry_packs_inbox/` (in your repo) and redeploy
  - Or mount a disk and upload there, then restart — extracted to `industry_packs_runtime/`

## Deploy on Render (Docker)
1. Push this folder to a Git repo.
2. In Render: **New → Web Service → Connect repo**
3. Render will detect `render.yaml` (Docker runtime).
4. Deploy.

### After deploy
Open:
- `https://<your-service>.onrender.com/demo`

## Optional: enable billing later
Set env vars in Render dashboard:
- `ENABLE_BILLING=1`
- `STRIPE_SECRET_KEY`
- `PRICE_ID_PROFESSIONAL`
- `PRICE_ID_ENTERPRISE`
(Then redeploy.)
