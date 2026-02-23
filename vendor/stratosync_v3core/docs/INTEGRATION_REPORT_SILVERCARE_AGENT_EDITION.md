# Integration Report — SilverCare Tier1 Agent Edition v1

Date (UTC): 2026-02-19T14:02:59.996674Z

## Inputs
- Base package: STRATOSYNC_v2_7_1_DISTRIBUTABLE_COMPLETE.zip
  - Size: 147464 bytes
  - SHA256: `7f51d2b35a97ed77d397a3628e1fc600f50c11b8c42ac4d16579e85518d1ef58`
- Add-on pack: STRATOSYNC_SILVERCARE_TIER1_AGENT_EDITION_v1.zip
  - Size: 1898 bytes
  - SHA256: `9abc464816254b7f59d4b060154bccd375fe3ec03aaf520e3fef780bf3aaa53f`

## Integration actions
- Copied SilverCare assets into:
  - `docs/industry_packs/silvercare_tier1_agent_edition_v1/`
- JSON validation:
  - EXECUTIVE_SCHEMA.json: OK
  - MANAGEMENT_INTERVIEW_GUIDE.json: OK
- Added integrity manifest:
  - `docs/MANIFEST_SHA256.txt`
- Removed `app/__pycache__` from the distributable.

## Resulting package (uncompressed workspace)
- File count: 35
- Total size: 202119 bytes

## File list (relative paths)
```
.env.example
Dockerfile
Makefile
README.md
app/__init__.py
app/audit.py
app/charts.py
app/config.py
app/core.py
app/main.py
app/models.py
app/reporting.py
app/state_store.py
data/audit_log.jsonl
data/board_demo_alpha.pdf
data/state_db.json
data/trend_demo_alpha.png
docker-compose.yml
docs/API_SPEC.md
docs/CHANGELOG.md
docs/DASHBOARD_WIREFRAME.md
docs/DEMO_GUIDE.md
docs/EXECUTIVE_ONEPAGER_TEMPLATE.md
docs/INVESTOR_PITCH_OUTLINE_10SLIDES.md
docs/MANIFEST_SHA256.txt
docs/MASTER_SPECIFICATION_v2_6.md
docs/PRICING_MODEL_BCD.md
docs/industry_packs/silvercare_tier1_agent_edition_v1/EXECUTIVE_SCHEMA.json
docs/industry_packs/silvercare_tier1_agent_edition_v1/IMPLEMENTATION_GUIDE.md
docs/industry_packs/silvercare_tier1_agent_edition_v1/MANAGEMENT_INTERVIEW_GUIDE.json
ops/EVIDENCE_BUNDLE_SOP.md
requirements.txt
sample_data/evaluate_request_example.json
sample_data/override_request_example.json
scripts/run_demo.sh
```
