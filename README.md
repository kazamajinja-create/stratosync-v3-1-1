# STRATOSYNC v3.1.1 — Commercial Integrated (A)

This package is a **one-click Render deploy** FastAPI app with:
- Demo HTML UI (single flow: input -> PDF output)
- Fixed v3.1.1 math specification:
  - Surface Index (SI), Surface Efficiency (SE)
  - Ω Index (Org connectivity)
  - Decision Amplification Factor (DAF) and Adjusted Risk
  - SurfacePower / Resilience
- Standardized Executive PDF report generator (Japanese-safe fonts)

## Quick Start (Local)
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 10000
```
Open:
- http://localhost:10000/  (home)
- http://localhost:10000/demo  (demo input -> PDF)

## Render
Deploy as a Docker service. `render.yaml` is included.
Health check: `/health`

## Notes
- This is a **deterministic v3.1.1 spec** (weights, clamps fixed).
- Enterprise feature flags are scaffolded but not activated in UI yet.
