# STRATOSYNC MASTER ARCHITECTURE v0.2

Unified Architecture File (Mode2–4 + Translator + Data Contracts)

---



---

# SOURCE: MODE2_HUMAN_SPEC_v0.2.md

# STRATOSYNC Mode 2 (Human Decision Mode) - Detailed Spec v0.2 (2026-02-18)

## 1. Purpose
Convert **AXIS-Core raw outputs** + **intake** into a **business-explainable, numeric HumanProfile** used by Mode 3/4/6/7.

## 2. Canonical Decision Vector (fixed 7D)
All values are normalized to **0–100**.

- `risk_taking`
- `analytical_depth`
- `speed_vs_deliberation`  (higher = faster decisions)
- `authority_orientation`  (higher = centralize authority)
- `autonomy_need`
- `structure_preference`
- `emotional_reactivity`

This vector is the **single source of truth** for cross-mode integration.

## 3. Inputs

### 3.1 Minimum (MVP)
- `person_id` (string)
- `role` (string)
- `context` (object)
- `intake_text` (string, 300–2000 chars recommended)
- `history[]` (3 decision logs recommended)
  - `goal`, `options`, `choice`, `outcome`, `learning` (strings)
- `constraints` (object)

### 3.2 AXIS Raw
- `axis_raw` (JSON/YAML/MD accepted; stored verbatim in Audit Appendix)

## 4. Computation Pipeline

### Step A. Feature Extraction
1) **AXIS score seeds** (if present)
   - `stability`, `adaptability`, `vitality` (0–100 preferred; else normalize)
2) **Trait lexicon extraction** from text fields (summary/traits)
   - dictionary maps phrases → (dimension, delta)
3) **Intake signal extraction**
   - decision history patterns and language markers

### Step B. Dimension Mapping (seed mapping)
Initial mapping (MVP):
- `structure_preference`  ← `stability`
- `speed_vs_deliberation`← `vitality`
- `analytical_depth`     ← 100 - `vitality` * 0.2 + `stability` * 0.2 (baseline)
- `risk_taking`          ← `adaptability`
- `autonomy_need`        ← `adaptability` * 0.6 + `vitality` * 0.4
- `authority_orientation`← `stability` * 0.5 + (100-`autonomy_need`) * 0.5
- `emotional_reactivity` ← inferred from lexicon + intake markers (baseline 50)

Then apply lexicon deltas and clamp to 0–100.

### Step C. Normalization
If any seeds are not in 0–100:
- MinMax to 0–100 within the source range
- Record normalization method in `audit.normalization`

### Step D. Bias Flags (rule-based v0.2)
Flags are **tendencies**, not labels. Output as list of strings.

- `High_Overconfidence`:
  - `risk_taking > 75` AND `analytical_depth < 40`
- `Analysis_Paralysis`:
  - `analytical_depth > 80` AND `speed_vs_deliberation < 30`
- `Authority_Friction_Risk`:
  - `authority_orientation > 85` AND `emotional_reactivity > 60`
- `Change_Resistance`:
  - `structure_preference > 80` AND `risk_taking < 40`
- `Volatility_Seeking`:
  - `risk_taking > 80` AND `structure_preference < 35`

### Step E. Derived Indices (v0.2)
- `risk_posture_index (RPI)`
  - `RPI = 0.45*risk_taking + 0.25*(100-analytical_depth) + 0.15*emotional_reactivity + 0.15*(100-structure_preference)`
- `decision_stability_score (DSS)`
  - `DSS = 100 - 1.2*abs(speed_vs_deliberation - 50)`
  - clamp 0–100

## 5. Output Contract
Output must conform to `human_profile.schema.json` (v0.2). Additional fields allowed under `extensions`.

## 6. Non-Goals / Guardrails
- Not for hiring/firing decisions.
- Not for discrimination-related outputs.
- Provide “conditions for friction” rather than “good/bad person”.


---

# SOURCE: HDA_TRANSLATOR_SPEC_v0.2.md

# STRATOSYNC HDA-Translator (AXIS → Business) - Spec v0.2 (2026-02-18)

## 1. Objective
Translate `axis_raw` into STRATOSYNC `human_profile` with:
- deterministic mapping (MVP)
- explainable trace
- stable versioning

## 2. Inputs
- `axis_raw`: arbitrary structure (JSON/YAML/MD)
- `intake`: Mode2 minimum inputs (optional but recommended)

## 3. Outputs
- `human_profile`: normalized 0–100, includes:
  - `decision_vector` (7D)
  - `bias_flags`
  - `risk_posture_index`
  - `decision_stability_score`
  - `explainability.trace[]` (mapping evidence)

## 4. Explainability Trace Format
Each applied rule must emit a trace item:
```json
{
  "source": "axis_raw.scores.stability",
  "target": "decision_vector.structure_preference",
  "operation": "assign",
  "value": 72,
  "confidence": 0.7
}
```

## 5. Mapping Sources Priority
1) Numeric scores found in `axis_raw` (preferred)
2) Trait lexicon hits
3) Intake-derived heuristics
4) Default baselines (50)

## 6. Lexicon System (MVP)
Lexicon entry:
```json
{
  "pattern": "粘り強い|やり抜く",
  "deltas": {"decision_vector.structure_preference": 8},
  "confidence": 0.6
}
```
- Regex allowed
- Multiple hits accumulate but clamp to avoid runaway.

## 7. Versioning
- `translator_version`: `HDA-Translator_v0.2`
- All outputs embed `versions` + `manifest_sha256`


---

# SOURCE: MODE3_ORG_DYNAMICS_SPEC_v0.2.md

# STRATOSYNC Mode 3 (Organizational Dynamics) - Algorithm Spec v0.2 (2026-02-18)

## 1. Purpose
Compute:
- Role fit scores (person ↔ role)
- Friction probability map (person ↔ role ↔ org_unit)
- Key-person dependency per role/unit
- Hotspots list for executive report

## 2. Vectors
Dimension d = 7 (Mode2 decision vector).

- Person vector: P_i ∈ [0,100]^d
- Role requirement vector: R_j ∈ [0,100]^d
- Context pressure: Pressure_k ∈ [0,1]

Weights:
- w ∈ [0,1]^d (from TemplatePack)
- default w_m = 1/d if not provided

## 3. Role Fit
Distance:
D_ij = Σ_m w_m * |P_i,m - R_j,m|

Normalize:
Dprime_ij = D_ij / Σ_m w_m   (0–100 scale)

Fit:
Fit_ij = 100 - clip(Dprime_ij, 0, 100)

## 4. Friction Probability
Mismatch:
M_ij = Dprime_ij / 100

Logistic model:
FrictionProb_ijk = σ(a*M_ij + b*Pressure_k + c*M_ij*Pressure_k + d0)

σ(x)=1/(1+e^(-x))

### Default coefficients (MVP starting point)
a=3.0, b=2.0, c=3.0, d0=-2.0

## 5. Pressure_k Composition (TemplatePack)
Pressure_k = clip(
  p_busy*BusyIndex +
  p_eval*EvaluationIntensity +
  p_autonomy*(1-AutonomyProvided) +
  p_customer*CustomerComplaintRate
, 0, 1)

## 6. Key-Person Dependency
Dependency_jk = clip( (Top1(Fit_candidates) - Mean(Fit_candidates)) / 100 , 0, 1)

## 7. Outputs
- role_fit_scores
- friction_map
- hotspots (top N with reasons)
- dependency


---

# SOURCE: MODE4_SCENARIO_SPEC_v0.2.md

# STRATOSYNC Mode 4 (Scenario Branch) - Math & Implementation Spec v0.2 (2026-02-18)

## 1. Purpose
Compare scenarios across:
- Finance
- Risk
- OrgLoad (Mode3)
- Align (Mode6-lite)

Return:
- Scorecards (0–100)
- Pareto frontier
- Switching thresholds via sensitivity scan

## 2. Criteria Normalization (0–100, higher is better)
Finance_s = normalize_to_0_100(ΔEBITDA_s)
Risk_s    = 100 - normalize_to_0_100(Risk_s_raw)
OrgLoad_s = 100 - normalize_to_0_100(OrgLoad_s_raw)
Align_s   = already 0–100

## 3. Composite (reference only)
Score_s = α*Finance_s + β*Risk_s + γ*OrgLoad_s + δ*Align_s
(α+β+γ+δ=1; provided by TemplatePack)

## 4. Pareto Frontier
Non-dominated set over (Finance, Risk, OrgLoad, Align).

## 5. Switching Threshold
Scan key parameter p in [p_min, p_max] and detect argmax changes of Score_s(p).


---

# SCHEMA REFERENCES

- schemas/human_profile.schema.json
- schemas/integrated_case.schema.json
- MANIFEST_v0.2.json
