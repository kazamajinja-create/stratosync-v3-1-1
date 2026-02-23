# Run Demo (Conceptual)

This bundle packages assets/specs/demos. It does not enforce a single runtime.

Recommended workflow:
1) Open demo case:
   - 05_STRATOSYNC_RELEASE_DEMO/.../integrated_case.v1.0.json
2) Review reports:
   - STRATOSYNC_Executive_Report_v1.0.pdf
3) Implement a runner that:
   - Loads inputs -> calls Human Engine (AXIS) for Mode2
   - Calls Business Engine (QCS) for Mode1
   - Computes Mode3/4 then Mode6/7
4) Export updated integrated_case + regenerate reports.

If you want, create a `run_demo.py` in the root that wires these calls for your environment.


## Convenience
- `bash run_demo.sh` (passes args to runner)
- `make demo` / `make demo_pdf`

## Template Packs
- See `TEMPLATE_PACKS/README.md`


## TemplatePack usage
- Apply a TemplatePack to overwrite role_requirements & scenario_demands (non-destructive).
- Example:
  - `make demo_tp`
  - `TEMPLATE=TEMPLATE_PACKS/TemplatePack_JP_FoodService_v1_skeleton.json bash run_demo.sh`


## Mode1 demo (sample KPI)
When a TemplatePack contains `assets.sample_data_path`, the runner computes a lightweight Mode1 business summary and writes it into `mode1_business` and `business_model` indices.


## Mode3 demo (role fit / friction)
When a TemplatePack provides `role_catalog`, the runner computes a lightweight Mode3 output:
- `mode3_org.role_fit`
- `mode3_org.friction_map`
- `org_model.leadership_gap_index`
- `org_model.succession_risk_indicator`


## Mode4 demo (scenario composite)
When TemplatePack is applied, the runner computes lightweight Mode4 composite scores using Mode1 + Mode3 (+ Mode6 if present).
Outputs:
- `scenarios[*].composite_score`
- `scenarios[*].components`
- `mode4_scenarios` summary


## Demo Executive Report
- Generate markdown (+ optional pdf if reportlab exists):
  - `python run_demo.py --input <case> --out out_demo --write-report`
  - `make demo_med_report` / `make demo_dental_report`
- Shell: `WRITE_REPORT=1 bash run_demo.sh`


## Report format v1
`--write-report` writes:
- `Executive_Report.demo.md`
- `Executive_Report.demo.v1.pdf` (styled PDF)


## SilverCare demo
Use TEMPLATE=TEMPLATE_PACKS/TemplatePack_JP_SilverCare_v1_0.json
