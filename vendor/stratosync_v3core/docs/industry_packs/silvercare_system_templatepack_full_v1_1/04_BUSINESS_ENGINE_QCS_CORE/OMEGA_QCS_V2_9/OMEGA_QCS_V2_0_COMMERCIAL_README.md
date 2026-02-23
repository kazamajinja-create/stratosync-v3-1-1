# Omega Quantum Consulting Scheme Engine v2.0 (Commercial)
Version: 2.0.0

## What’s new vs v1.1
- Rigorous collision suite with explainability and configurable thresholds
- Market Context Injector: provider architecture (offline file provider + stub for future APIs)
- Audit Trail Logger (JSONL) for "who/when/which version/which inputs/which outputs"
- Report generator (MD + audit-friendly plain text PDF)
- Commercial runner: one-call orchestration producing artifacts + audit event

## Key guarantees
- Non-Decision: no recommendations, no guarantees of outcomes
- Non-Advisory: not investment, accounting, tax, audit, or legal advice
- Explainability: top contributors and thresholds are shown

## Quick start (concept)
- Provide: internal_scores (0-100), sensitivity_map (0-1)
- Optionally provide market packet via JSON file provider

See omega_qcs/commercial_runner.py -> run_commercial_analysis()
