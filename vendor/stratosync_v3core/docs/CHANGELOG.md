# Changelog
## 2.7.3 (2026-02-19T14:02:59.996674Z)
- Added industry pack: SilverCare Tier1 Agent Edition v1 under `docs/industry_packs/`.
- Added `docs/MANIFEST_SHA256.txt` for per-file integrity verification.
- Removed `app/__pycache__` from distributable ZIP.

## 2.7.1 (2026-02-19T13:50:54.155528Z)
- Evidence export now auto-includes attachments:
  - `trend.png` (Δ & S chart)
  - `board.pdf` (1-page decision sheet)
- Export manifest includes an `attachments` list.
- No changes to core evaluation math or thresholds.

## 2.7.0
- Distributable package build: Docker + demo data + pre-generated assets.
- Includes demo audit_log.jsonl + state_db.json and generated `trend_demo_alpha.png` / `board_demo_alpha.pdf`.
- Added scripts: `scripts/run_demo.sh` and sample request payloads.
- Keeps v2.6.2 feature set: chart endpoint + PDF endpoint + evidence export + audit verify.

## v2.8.0
- Added `SilverCare System TemplatePack FULL v1.1` under `docs/industry_packs/silvercare_system_templatepack_full_v1_1/` (full recursive import; excludes `__pycache__`).
- Refreshed `docs/MANIFEST_SHA256.txt`.
