# TEMPLATE_PACKS

Template Packs define industry defaults for:
- role_catalog (role_requirements vectors)
- scenario_demands (scenario behavioral demands)
- optional weights (decision vector weights, business axis weights)

Start by copying `TemplatePack_JP_FoodService_v1_skeleton.json` and adjusting.

## Runner integration
- Direct: `python run_demo.py --template TEMPLATE_PACKS/<pack>.json --input <case> --out out_demo`
- Shell: `TEMPLATE=TEMPLATE_PACKS/<pack>.json bash run_demo.sh`
- Make: `make demo_tp`

## Medical/Dental packs
- `TemplatePack_JP_MedicalClinic_v1.json` (assets bundled)
- `TemplatePack_JP_DentalClinic_v1_1.json` (assets bundled)

## Make targets
- `make demo_med`
- `make demo_dental`

## Sample KPI data
- Medical: TEMPLATE_PACKS/SAMPLE_DATA/sample_kpi_medical_clinic_v1.json
- Dental : TEMPLATE_PACKS/SAMPLE_DATA/sample_kpi_dental_clinic_v1_1.json
- Applying these TemplatePacks will compute a lightweight Mode1 demo in `mode1_business`.
