# AXIS Drift Index™ (Module Pack)

This pack contains a minimal, implementation-ready module set for:
- Online diagnostic (20 questions + text inputs)
- Feature extraction (baseline heuristics, replaceable by LLM)
- Scoring (fixed spec) + classification thresholds (fixed spec)
- Report auto-generation (template-driven)
- CLI runner for quick tests

## Install (local)
```bash
pip install -e .
```

## Run demo
```bash
python -m axis_drift_index.cli --input examples/input_demo.json
```

## Core scoring spec (fixed)
- CF = sum(Q1..Q4)
- MD_raw = sum(Q5..Q8)      -> MD_stability = 20 - MD_raw
- HS_raw = sum(Q9..Q12)     -> HS_stability = 20 - HS_raw
- EE_raw = sum(Q13..Q16)    -> EE_stability = 20 - EE_raw
- AC = sum(Q17..Q20)
- Total = CF + MD_stability + HS_stability + EE_stability + AC (0..100)

Thresholds:
- Stable >= 80
- Exploration 60-79
- Mild Drift 40-59
- Reaction-driven < 40
