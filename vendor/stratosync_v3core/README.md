# STRATOSYNC v3.0.0 — Distributable Full Package
Generated: 2026-02-19T13:47:49.170158Z

Positioning: **Political-Execution Synchronization OS** (BCD)
Outputs: **GO / CONDITIONAL / FREEZE**
Auditability: **SHA256 hash-chained decision records**

This v2.7 build is intended to be *handed to investors / partners* and run as-is:
- Docker (recommended)
- Local Python virtualenv
- Includes demo data + generated assets (trend.png / board.pdf)

---

## 1) Quick run (Docker)
```bash
docker compose up --build
```
Open:
- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

Demo endpoints (after you post a demo evaluation):
- Board HTML: http://localhost:8000/board/demo:alpha
- Board PDF:  http://localhost:8000/board/pdf/demo:alpha
- Trend PNG:  http://localhost:8000/trend/png/demo:alpha?n=50

Unified v3 endpoint (recommended):
- `POST /v3/analyze` — run RCL + SDL + ΩCL + v3 synthesis in one call

RCL endpoints (integrated-case diagnostics):
- `POST /rcl/analyze` — run BEI/ECE/TCD/RSM on an integrated case
- Board HTML for an RCL case: http://localhost:8000/board/case:SILVERCARE_DEMO_001

---

## 2) Quick run (local Python)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

---

## 3) Run the included demo script
```bash
bash scripts/run_demo.sh
```
This will:
- POST multiple evaluations for `demo:alpha`
- Generate trend chart + board PDF
- Export evidence bundle (admin-gated)

---

## What’s included (why this ZIP is larger)
- **Dockerfile + docker-compose.yml**
- **Makefile**
- `scripts/` demo runner + curl samples
- `sample_data/` request JSON examples
- `data/` pre-generated demo artifacts:
  - audit_log.jsonl
  - state_db.json
  - trend_demo_alpha.png
  - board_demo_alpha.pdf

---

## RCL — Ramanujan Convergence Layer (BEI/ECE/TCD/RSM)

RCL is a cross-cutting inference layer intended for business-consulting templates.
It adds four diagnostics that help avoid overconfident recommendations:

- **BEI (Branch Explosion Index)**: branching blow-up risk under high degrees of freedom
- **ECE (Early Convergence Estimator)**: confidence + next-best data to collect
- **TCD (Twin-Cause Detector)**: ambiguity flag when multiple causes fit the same KPI movement
- **RSM (Residual Structure Monitor)**: unexplained residual monitoring + anomaly flag

Sample request:
- `sample_data/rcl_case_silvercare_example.json`

Schemas:
- `schemas/rcl_request.schema.json`
- `schemas/rcl_response.schema.json`

---
---

## Industry packs
This distribution includes an industry-specific add-on pack:
- `docs/industry_packs/silvercare_tier1_agent_edition_v1/`
  - `EXECUTIVE_SCHEMA.json`
  - `MANAGEMENT_INTERVIEW_GUIDE.json`
  - `IMPLEMENTATION_GUIDE.md`

Use these assets to run Tier-1 discovery interviews and to map findings into STRATOSYNC evaluation requests.


## Security note
`/override-lock` and `/evidence/export` are admin-gated via `X-Admin-Token`.
Change `ADMIN_TOKEN` in `.env` before sharing beyond trusted recipients.


## Industry Packs

- SilverCare Tier1 Agent Edition (v1): `docs/industry_packs/silvercare_tier1_agent_edition_v1/`
- SilverCare System TemplatePack FULL (v1.1): `docs/industry_packs/silvercare_system_templatepack_full_v1_1/`


## Report-Pack (v2.9.1)

- 帳票レイアウト共通スキーマ: `schemas/report_layout_master.schema.json`
- 日本語ラベル辞書: `schemas/label_dictionary_ja.json`
- 業態テンプレ追加: `industry_packs_runtime/<industry_id>/`
- 生成パラメータ: `?industry=<industry_id>&kind=executive|agent|enterprise`
