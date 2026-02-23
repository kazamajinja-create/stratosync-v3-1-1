# QUICKSTART (Integration Bundle)

1) Read architecture
   - Open `01_ARCHITECTURE/.../STRATOSYNC_UNIFIED_ARCHITECTURE_v1.1.md`

2) Inspect demo case
   - Open `05_STRATOSYNC_RELEASE_DEMO/.../integrated_case.v1.0.json`
   - Review `STRATOSYNC_Executive_Report_v1.0.pdf`

3) Connect engines (implementation layer)
   - Human Engine source: `03_HUMAN_ENGINE_AXIS_CORE/AXIS_CORE_V4_1_1/...`
   - Business Engine source: `04_BUSINESS_ENGINE_QCS_CORE/OMEGA_QCS_V2_9/...`
   - STRATOSYNC orchestrator should call:
     Mode2 (Human) -> Mode3 (Org) -> Mode4 (Scenario) -> Mode6/7 (Synthesis)

4) Build your TemplatePack
   - Start from the demo’s role_requirements & weights and create industry packs.

Note: This bundle does not modify engine code; it packages assets + specs + demo.
