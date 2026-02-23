# QCS Dental Plugin v1 (Dentistry Edition)

This package modularizes the **QCS Triad Model** for dental clinics:
- Dental Resilience Score™ (DRS)
- Drift Detection Index™ (DDI)
- Dependency Risk Score™ (DeRS)
- Structural Clarity Index™ (SCI)
- QCS Global Index™ (GI)

## Philosophy
- **Structure is public** (what is evaluated / why)
- **Formula & thresholds are private** (weights, cutoffs) — provided here as a reference implementation for the owner.

## What's included
- `schemas/` input JSON Schemas
- `configs/` KPI mapping + weights (editable)
- `engine/` scoring engine (Python)
- `reports/` report templates (Markdown)
- `samples/` sample clinic data
- `api/` FastAPI stub endpoints (optional integration)

## Quickstart
```bash
python -m engine.run_sample
```

## Outputs
- `outputs/sample_report.md` (generated)
- `outputs/sample_scores.json`

## v1.1 additions
- `docs/scoring_rubric_ja_v1_1.md` (0-5 scoring criteria)
- `reports/deck_outline_ja_10slides_v1_1.md` (10-slide executive deck template)
- `docs/partner_onepager_tax_ja.md` (partner positioning)
