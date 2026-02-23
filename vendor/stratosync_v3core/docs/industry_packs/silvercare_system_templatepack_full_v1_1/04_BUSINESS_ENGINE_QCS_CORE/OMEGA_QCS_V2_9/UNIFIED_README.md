# ΩQCS Final Unified Pack (v2.3.0)
This pack merges:
- ΩQCS Engine v2.2 (Business/Commercial + Market + Portfolio)
- AXIS Drift Index Module Pack
- HSRE Agriculture Pilot Pack

## Key integrations
1) AXIS Drift Index -> Report auto-insert (optional)
   - commercial_runner.run_commercial_analysis(axis_drift_payload=...)
   - report_generator renders `axis_drift` section when present

2) HSRE Agriculture -> Industry dictionary mapping
   - industry_risk_dictionary_extended includes `agriculture` key
   - prompt added: PROMPTS_COLLECTION/07_hsre_agriculture_mapping_prompt.txt

## Notes
- No recommendations, no guarantees, non-advisory boundaries preserved.


## v2.5.0 Update
- Auto industry policy router: strategy/matrix selection based on industry_key
- Commercial runner resolves policy and stores resolved_policy in external_injection


---

## DD-Ready Integrated Architecture

ΩQCS now embeds institutional-grade Due Diligence (DD-Ready) capability within its unified structure.
Financial connectivity is maintained internally without fragmenting the architecture.
This preserves strategic, governance, and institutional coherence.
