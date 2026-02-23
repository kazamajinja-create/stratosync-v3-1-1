#!/usr/bin/env python3
# STRATOSYNC SYSTEM v1.1 - Demo Runner (TemplatePack-ready)
# Built: 2026-02-18
#
# Purpose:
# - Provide a reproducible entry point for the STRATOSYNC integrated bundle.
# - Allow industry expansion by applying a TemplatePack JSON (role_catalog + scenario_demands + weights).
#
# Usage examples:
#   python run_demo.py --input 05_STRATOSYNC_RELEASE_DEMO/STRATOSYNC_V1_RELEASE_COMPLETE/integrated_case.v1.0.json --out out_demo
#   python run_demo.py --input 05_STRATOSYNC_RELEASE_DEMO/STRATOSYNC_V1_RELEASE_COMPLETE/integrated_case.v1.0.json --template TEMPLATE_PACKS/TemplatePack_JP_FoodService_v1_skeleton.json --out out_demo
#   python run_demo.py --input ... --template ... --out out_demo --regen-pdf
#
# Notes:
# - This runner does not import proprietary AXIS/QCS code.
# - Mode1–5 are treated as upstream engines. This runner demonstrates how to *wire* them by:
#   (a) applying TemplatePack defaults (role vectors + scenario demands + optional weights),
#   (b) computing Mode6/7 demo synthesis from existing Mode3/4 outputs (or placeholders).
#
import argparse
import json
import math
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

DV_KEYS = [
    "risk_taking","analytical_depth","speed_vs_deliberation","authority_orientation",
    "autonomy_need","structure_preference","emotional_reactivity"
]

def mean(xs):
    return sum(xs)/len(xs) if xs else 0.0

def stdev(xs):
    if not xs or len(xs) < 2:
        return 0.0
    m = mean(xs)
    var = sum((x-m)**2 for x in xs)/(len(xs)-1)
    return math.sqrt(var)

def linear_growth_rate(monthly_values):
    # simple (last-first)/first
    if not monthly_values or monthly_values[0] == 0:
        return 0.0
    return (monthly_values[-1] - monthly_values[0]) / float(monthly_values[0])

def compute_mode1_demo_from_sample(sample: Dict[str, Any]) -> Dict[str, Any]:
    """Compute a lightweight Mode1 (Business) demo output from sample KPI data."""
    rev = [float(x) for x in sample.get("monthly_revenue", [])]
    pts = [float(x) for x in sample.get("monthly_patients", [])]

    # Revenue stability: inverse of coefficient of variation
    cv = (stdev(rev) / mean(rev)) if mean(rev) > 0 else 1.0
    revenue_stability_index = clamp(100.0 * (1.0 - cv), 0.0, 100.0)

    # Growth sustainability: combine revenue growth and patient growth (bounded)
    rev_g = linear_growth_rate(rev)
    pts_g = linear_growth_rate(pts) if pts else 0.0
    growth = 0.6*rev_g + 0.4*pts_g
    growth_sustainability_index = clamp(50.0 + 80.0*growth, 0.0, 100.0)

    # Market dependency proxy: top_referral_share (higher -> worse)
    top_ref_share = float(sample.get("top_referral_share", 0.2))
    market_dependency = clamp(100.0 * top_ref_share, 0.0, 100.0)
    market_dependency_index = clamp(100.0 - market_dependency, 0.0, 100.0)

    # Key-person dependency proxy: top_doctor_revenue_share (higher -> worse)
    top_doc_share = float(sample.get("top_doctor_revenue_share", 0.5))
    keyperson_dependency = clamp(100.0 * top_doc_share, 0.0, 100.0)
    key_person_dependency_index = clamp(100.0 - keyperson_dependency, 0.0, 100.0)

    # Financial risk proxy from fixed_cost_ratio and cash_months
    fixed_cost_ratio = float(sample.get("fixed_cost_ratio", 0.6))
    cash_months = float(sample.get("cash_months", 3.0))
    rigidity_risk = clamp(100.0 * fixed_cost_ratio, 0.0, 100.0)
    liquidity_score = clamp(20.0*cash_months, 0.0, 100.0)  # 5 months -> 100
    financial_risk = clamp(0.55*rigidity_risk + 0.45*(100.0 - liquidity_score), 0.0, 100.0)

    return {
        "revenue_stability_index": round(revenue_stability_index, 2),
        "growth_sustainability_index": round(growth_sustainability_index, 2),
        "market_dependency_index": round(market_dependency_index, 2),
        "key_person_dependency_index": round(key_person_dependency_index, 2),
        "financial_risk_index": round(financial_risk, 2),
        "method_version": "Mode1_v0.demo_from_sample_kpi"
    }
def clamp(x: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, x))

def l1_fit(vec: Dict[str,float], demand: Dict[str,float], weights: Dict[str,float]) -> Tuple[float,float]:
    dist = sum(weights[k] * abs(vec[k] - demand[k]) for k in DV_KEYS)
    fit = 100.0 - clamp(dist, 0.0, 100.0)
    return round(fit, 2), round(dist, 2)

def cosine_similarity(a: Dict[str,float], b: Dict[str,float]) -> float:
    # a,b expected on DV_KEYS
    dot = sum(float(a[k])*float(b[k]) for k in DV_KEYS)
    na = math.sqrt(sum(float(a[k])**2 for k in DV_KEYS))
    nb = math.sqrt(sum(float(b[k])**2 for k in DV_KEYS))
    if na == 0 or nb == 0:
        return 0.0
    return dot/(na*nb)

def role_fit_score(person_vec: Dict[str,float], req_vec: Dict[str,float]) -> float:
    # Use cosine similarity mapped to 0..100
    if any(k not in person_vec for k in DV_KEYS) or any(k not in req_vec for k in DV_KEYS):
        return 50.0
    sim = cosine_similarity(person_vec, req_vec)  # -1..1 (but our values are positive, so 0..1)
    return clamp(100.0*sim, 0.0, 100.0)

def friction_probability(a_vec: Dict[str,float], b_vec: Dict[str,float]) -> float:
    # Lightweight friction: weighted L1 distance normalized -> 0..1
    if any(k not in a_vec for k in DV_KEYS) or any(k not in b_vec for k in DV_KEYS):
        return 0.25
    dist = sum(abs(float(a_vec[k]) - float(b_vec[k])) for k in DV_KEYS) / (len(DV_KEYS)*100.0)  # 0..1
    # Emphasize emotional_reactivity mismatch and authority/autonomy mismatch
    bonus = 0.0
    bonus += abs(float(a_vec["emotional_reactivity"]) - float(b_vec["emotional_reactivity"])) / 100.0 * 0.25
    bonus += abs(float(a_vec["authority_orientation"]) - float(b_vec["authority_orientation"])) / 100.0 * 0.20
    bonus += abs(float(a_vec["autonomy_need"]) - float(b_vec["autonomy_need"])) / 100.0 * 0.20
    fp = clamp(dist + bonus, 0.0, 1.0)
    return round(fp, 4)

def compute_mode3_demo(case: Dict[str, Any]) -> Dict[str, Any]:
    """Compute lightweight Mode3 outputs from role_requirements + human_profiles.
    Produces:
    - org_model.role_fit (person_id -> role_id -> score)
    - org_model.friction_map (person_a -> role -> unit -> friction_prob) if org_model has mapping
    - org_model.leadership_gap_index (simple)
    - org_model.succession_risk_indicator (simple)
    """
    org = case.get("org_model", {}) or {}
    role_reqs = org.get("role_requirements", {}) or {}
    people = case.get("human_profiles", []) or []

    # role_fit matrix
    role_fit = {}
    for p in people:
        pid = p.get("person_id") or p.get("id") or p.get("name") or "person"
        vec = p.get("decision_vector", {}) or {}
        fits = {}
        for role_id, req_vec in role_reqs.items():
            fits[role_id] = round(role_fit_score(vec, req_vec), 2)
        role_fit[pid] = fits

    # friction map: if org has team_map: {person_id:{org_unit, role_id}} else derive from person.role
    team_map = org.get("team_map") or {}
    if not team_map:
        for p in people:
            pid = p.get("person_id") or p.get("id") or p.get("name") or "person"
            team_map[pid] = {
                "org_unit": p.get("org_unit") or "Unknown",
                "role_id": p.get("role") or "Unknown"
            }

    # pairwise friction between leadership and each person by org_unit
    friction_map = {}
    leadership = [p for p in people if p.get("role") in ("CEO","COO","Clinic_Director","Dental_Director")] or people[:1]
    for lp in leadership:
        lid = lp.get("person_id") or lp.get("id") or lp.get("name") or "leader"
        friction_map[lid] = {}
        lvec = lp.get("decision_vector", {}) or {}
        for p in people:
            pid = p.get("person_id") or p.get("id") or p.get("name") or "person"
            if pid == lid:
                continue
            unit = (team_map.get(pid, {}) or {}).get("org_unit","Unknown")
            # organize as leader -> role -> unit -> prob
            friction_map[lid].setdefault(team_map.get(pid, {}).get("role_id","Unknown"), {})
            friction_map[lid][team_map.get(pid, {}).get("role_id","Unknown")][unit] = friction_probability(lvec, p.get("decision_vector", {}) or {})

    # leadership gap: average fit of leadership to top-required roles (if exists)
    leadership_ids = []
    for lp in leadership:
        leadership_ids.append(lp.get("person_id") or lp.get("id") or lp.get("name") or "leader")
    leader_fit_scores = []
    for lid in leadership_ids:
        if lid in role_fit:
            # take best-fit role score
            best = max(role_fit[lid].values()) if role_fit[lid] else 50.0
            leader_fit_scores.append(best)
    leadership_gap_index = round(clamp(100.0 - (sum(leader_fit_scores)/len(leader_fit_scores) if leader_fit_scores else 50.0), 0, 100), 2)

    # succession risk: if key-person dependency high, raise
    bm = case.get("business_model", {}) or {}
    kpd = float(bm.get("key_person_dependency_index", 50.0))
    succession_risk_indicator = round(clamp(100.0 - kpd, 0, 100), 2)

    org["role_fit"] = role_fit
    org["friction_map"] = friction_map
    org["leadership_gap_index"] = leadership_gap_index
    org["succession_risk_indicator"] = succession_risk_indicator

    case["org_model"] = org
    case.setdefault("mode3_org", {})
    case["mode3_org"] = {
        "role_fit": role_fit,
        "friction_map": friction_map,
        "leadership_gap_index": leadership_gap_index,
        "succession_risk_indicator": succession_risk_indicator,
        "method_version": "Mode3_v0.demo_from_templatepack"
    }
    case.setdefault("versions", {})
    case["versions"]["mode3_method"] = "Mode3_v0.demo_from_templatepack"
    return case
def basic_validate(case: Dict[str, Any]) -> List[str]:
    required = ["case_id","versions","business_model","human_profiles","org_model","scenarios"]
    return [k for k in required if k not in case]

def load_template_pack(path: Path) -> Dict[str, Any]:
    tp = json.loads(path.read_text(encoding="utf-8"))
    # Minimal validation
    for k in ("template_pack_id","industry","version","role_catalog","scenario_demands"):
        if k not in tp:
            raise SystemExit(f"Invalid TemplatePack: missing key: RELEASE_MANIFEST_v1.0.json")
    return tp

def apply_template_pack(case: Dict[str, Any], tp: Dict[str, Any]) -> Dict[str, Any]:
    # 1) Scenario demands: store under case.scenario_model.demands (non-destructive)
    case.setdefault("scenario_model", {})
    case["scenario_model"].setdefault("demands", {})
    case["scenario_model"]["demands"].update(tp.get("scenario_demands", {}))

    # 2) Role catalog -> update org_model.role_requirements (vector requirements)
    case.setdefault("org_model", {})
    case["org_model"].setdefault("role_requirements", {})

    for role in tp.get("role_catalog", []):
        role_id = role.get("role_id")
        if not role_id:
            continue
        required_vector = role.get("required_vector", {})
        # Keep a consistent structure: role_id -> vector
        case["org_model"]["role_requirements"][role_id] = required_vector

    # 3) Optional weights
    weights = tp.get("weights", {}).get("decision_vector")
    if weights:
        case.setdefault("weights", {})
        case["weights"]["decision_vector"] = weights

    # 4) Assets references (non-destructive hints for downstream engines)
    assets = tp.get("assets", {}) or {}
    if assets:
        case.setdefault("business_model", {})
        case["business_model"].setdefault("schema_refs", {})
        # Example: qcs_module_path -> schema_refs.qcs_module_path
        for k, v in assets.items():
            case["business_model"]["schema_refs"][k] = v

    # 4.5) If TemplatePack bundles sample KPI data, compute lightweight Mode1 demo outputs
    sample_path = assets.get("sample_data_path")
    if sample_path:
        sp = Path(sample_path)
        if sp.exists():
            try:
                sample = json.loads(sp.read_text(encoding="utf-8"))
                mode1 = compute_mode1_demo_from_sample(sample)
                case.setdefault("business_model", {})
                case["business_model"].update({k: mode1[k] for k in [
                    "revenue_stability_index","growth_sustainability_index",
                    "market_dependency_index","key_person_dependency_index","financial_risk_index"
                ]})
                case.setdefault("mode1_business", {})
                case["mode1_business"] = mode1
                case.setdefault("versions", {})
                case["versions"]["mode1_method"] = mode1.get("method_version")
                case["versions"]["sample_data_path"] = sample_path
            except Exception:
                pass
        # 5) Annotate provenance
        case.setdefault("versions", {})
        case["versions"]["template_pack_id"] = tp.get("template_pack_id")
        case["versions"]["template_pack_version"] = tp.get("version")
        return case

def get_decision_weights(case: Dict[str, Any]) -> Dict[str,float]:
    w = case.get("weights", {}).get("decision_vector")
    if w and all(k in w for k in DV_KEYS):
        # normalize just in case
        s = sum(float(w[k]) for k in DV_KEYS)
        if s > 0:
            return {k: float(w[k])/s for k in DV_KEYS}
    return {k: 1.0/len(DV_KEYS) for k in DV_KEYS}

def compute_mode6_mode7_demo(case: Dict[str, Any]) -> Dict[str, Any]:
    profiles = case.get("human_profiles", [])
    ceo = next((hp for hp in profiles if hp.get("role") == "CEO"), None) or (profiles[0] if profiles else None)
    if not ceo:
        return case

    weights = get_decision_weights(case)

    # Use TemplatePack scenario_demands if available
    demands = case.get("scenario_model", {}).get("demands", {})
    # fallback defaults if missing
    if not demands:
        demands = {
            "S-A": {"risk_taking":85,"analytical_depth":50,"speed_vs_deliberation":85,"authority_orientation":60,"autonomy_need":70,"structure_preference":40,"emotional_reactivity":55},
            "S-B": {"risk_taking":60,"analytical_depth":70,"speed_vs_deliberation":60,"authority_orientation":55,"autonomy_need":55,"structure_preference":75,"emotional_reactivity":45},
            "S-C": {"risk_taking":45,"analytical_depth":80,"speed_vs_deliberation":45,"authority_orientation":50,"autonomy_need":50,"structure_preference":85,"emotional_reactivity":40},
        }

    ceo_vec = ceo.get("decision_vector", {})
    if any(k not in ceo_vec for k in DV_KEYS):
        return case

    mode6 = {
        "strategy_person_fit": {},
        "leadership_stretch_indicator": {},
        "organizational_resilience_index": None,
        "components": {},
        "method_version": "Mode6_v1.runner_demo.templatepack"
    }

    for sid, demand in demands.items():
        # Only compute if vector is complete
        if any(k not in demand for k in DV_KEYS):
            continue
        fit, dist = l1_fit(ceo_vec, demand, weights)
        mode6["strategy_person_fit"][sid] = fit
        mode6["leadership_stretch_indicator"][sid] = dist

    # Org resilience from existing org_model
    org_model = case.get("org_model", {})
    friction_map = org_model.get("friction_map", {})
    deps = org_model.get("dependency", {})

    fps = []
    for pid, roles in friction_map.items():
        for rname, units in roles.items():
            for unit, fp in units.items():
                try:
                    fps.append(float(fp))
                except Exception:
                    pass
    mean_friction = sum(fps)/len(fps) if fps else 0.0

    dep_vals = [float(v) for v in deps.values()] if deps else [0.0]
    dep_index = max(dep_vals) if dep_vals else 0.0

    leadership = [hp for hp in profiles if hp.get("role") in ("CEO","COO")] or profiles
    dss_vals = [float(hp.get("decision_stability_score", 50.0)) for hp in leadership] if leadership else [50.0]
    avg_dss = sum(dss_vals)/len(dss_vals)
    volatility_index = 1.0 - (avg_dss/100.0)

    resilience = 100.0 - (mean_friction*40.0 + dep_index*30.0 + volatility_index*30.0)
    resilience = clamp(resilience, 0.0, 100.0)

    mode6["organizational_resilience_index"] = round(resilience, 2)
    mode6["components"] = {
        "mean_friction_0_1": round(mean_friction, 4),
        "dependency_index_0_1": round(dep_index, 4),
        "avg_decision_stability_score": round(avg_dss, 2),
        "volatility_index_0_1": round(volatility_index, 4),
        "weights_decision_vector": {k: round(float(weights[k]), 6) for k in DV_KEYS}
    }

    # Mode7
    bm = case.get("business_model", {})
    biz_stability = (float(bm.get("revenue_stability_index", 50.0)) + float(bm.get("growth_sustainability_index", 50.0))) / 2.0
    leadership_stability = avg_dss

    best_s, best_score = None, -1.0
    for s in case.get("scenarios", []):
        try:
            cs = float(s.get("composite_score", 0.0))
        except Exception:
            cs = 0.0
        if cs > best_score:
            best_score = cs
            best_s = s.get("scenario_id")

    scenario_optimality = best_score if best_score >= 0 else 50.0

    health = 0.30*biz_stability + 0.25*resilience + 0.20*leadership_stability + 0.25*scenario_optimality
    health = clamp(health, 0.0, 100.0)

    mode7 = {
        "executive_health_score": round(health, 2),
        "components": {
            "business_stability": round(biz_stability, 2),
            "org_resilience": round(resilience, 2),
            "leadership_stability": round(leadership_stability, 2),
            "scenario_optimality": round(scenario_optimality, 2),
            "best_scenario": best_s,
        },
        "method_version": "Mode7_v1.runner_demo.templatepack"
    }

    case["mode6_alignment"] = mode6
    case["mode7_synthesis"] = mode7
    case.setdefault("versions", {})
    case["versions"]["runner_built_at"] = "2026-02-18"
    case["versions"]["mode6_method"] = mode6["method_version"]
    case["versions"]["mode7_method"] = mode7["method_version"]
    return case

def compute_mode4_demo(case: Dict[str, Any]) -> Dict[str, Any]:
    """Compute lightweight Mode4 scenario branch results.
    Uses:
    - scenario_model.demands (from TemplatePack)
    - business_model indices (from Mode1 demo or existing)
    - mode3_org signals (friction + leadership gap)
    Produces:
    - scenarios[*].composite_score updated (0..100)
    - scenarios[*].components filled
    - mode4_scenarios object with summary
    """
    demands = case.get("scenario_model", {}).get("demands", {}) or {}
    scenarios = case.get("scenarios", []) or []

    bm = case.get("business_model", {}) or {}
    # Business base score from Mode1 core indices
    biz = 0.0
    biz += float(bm.get("revenue_stability_index", 50.0)) * 0.30
    biz += float(bm.get("growth_sustainability_index", 50.0)) * 0.30
    biz += float(bm.get("market_dependency_index", 50.0)) * 0.15
    biz += float(bm.get("key_person_dependency_index", 50.0)) * 0.15
    biz += (100.0 - float(bm.get("financial_risk_index", 50.0))) * 0.10  # lower risk better

    # Org load score from Mode3 outputs
    mode3 = case.get("mode3_org", {}) or {}
    lg = float(mode3.get("leadership_gap_index", case.get("org_model", {}).get("leadership_gap_index", 50.0)))
    succ = float(mode3.get("succession_risk_indicator", case.get("org_model", {}).get("succession_risk_indicator", 50.0)))
    # Extract mean friction (0..1) -> penalty
    friction_map = mode3.get("friction_map") or case.get("org_model", {}).get("friction_map", {}) or {}
    fps = []
    for leader, roles in friction_map.items():
        for r, units in roles.items():
            for unit, fp in units.items():
                try:
                    fps.append(float(fp))
                except Exception:
                    pass
    mean_fp = sum(fps)/len(fps) if fps else 0.25
    org_load = clamp(100.0 - (mean_fp*60.0 + lg*0.20 + succ*0.20), 0.0, 100.0)

    # Human-strategy fit from Mode6 if already computed, else compute quickly using CEO vector and demands
    # We'll compute basic fit = average across demands using existing Mode6 if present.
    mode6 = case.get("mode6_alignment", {}) or {}
    spf = mode6.get("strategy_person_fit", {}) or {}

    updated = []
    for s in scenarios:
        sid = s.get("scenario_id") or s.get("id") or "S"
        # Scenario risk posture: use scenario demand risk_taking if exists
        d = demands.get(sid) or demands.get(s.get("scenario_key","")) or {}
        risk_t = float(d.get("risk_taking", 60.0)) if isinstance(d, dict) else 60.0
        risk_balance = clamp(100.0 - abs(risk_t - 60.0), 0.0, 100.0)  # 60 is neutral

        human_fit = float(spf.get(sid, 60.0)) if spf else 60.0

        composite = (
            0.45 * biz +
            0.25 * org_load +
            0.20 * human_fit +
            0.10 * risk_balance
        )
        composite = clamp(composite, 0.0, 100.0)

        s["composite_score"] = round(composite, 2)
        s["components"] = {
            "biz_base": round(biz, 2),
            "org_load": round(org_load, 2),
            "human_fit": round(human_fit, 2),
            "risk_balance": round(risk_balance, 2)
        }
        updated.append(s)

    # Determine best scenario
    best = max(updated, key=lambda x: float(x.get("composite_score", 0.0))) if updated else None
    case["scenarios"] = updated
    case["mode4_scenarios"] = {
        "best_scenario_id": best.get("scenario_id") if best else None,
        "best_score": best.get("composite_score") if best else None,
        "mean_score": round(sum(float(s.get("composite_score",0.0)) for s in updated)/len(updated),2) if updated else None,
        "method_version": "Mode4_v0.demo_composite_from_mode1_3"
    }
    case.setdefault("versions", {})
    case["versions"]["mode4_method"] = "Mode4_v0.demo_composite_from_mode1_3"
    return case
def render_executive_markdown(case: Dict[str, Any]) -> str:
    """Render a lightweight executive report markdown from Mode1/3/4/6/7."""
    v = case.get("versions", {}) or {}
    bm = case.get("business_model", {}) or {}
    m1 = case.get("mode1_business", {}) or {}
    m3 = case.get("mode3_org", {}) or {}
    m4 = case.get("mode4_scenarios", {}) or {}
    m6 = case.get("mode6_alignment", {}) or {}
    m7 = case.get("mode7_synthesis", {}) or {}

    best = m4.get("best_scenario_id")
    best_score = m4.get("best_score")

    lines = []
    lines.append(f"# STRATOSYNC Executive Demo Report")
    lines.append("")
    lines.append(f"- Case ID: `{case.get('case_id')}`")
    lines.append(f"- Built at: `{v.get('runner_built_at')}`")
    if v.get("template_pack_id"):
        lines.append(f"- TemplatePack: `{v.get('template_pack_id')}` (`{v.get('template_pack_version')}`)")
    lines.append("")

    lines.append("## Mode1: Business Snapshot (Demo)")
    lines.append(f"- Revenue Stability Index: **{bm.get('revenue_stability_index','-')}**")
    lines.append(f"- Growth Sustainability Index: **{bm.get('growth_sustainability_index','-')}**")
    lines.append(f"- Market Dependency Index: **{bm.get('market_dependency_index','-')}**")
    lines.append(f"- Key-Person Dependency Index: **{bm.get('key_person_dependency_index','-')}**")
    lines.append(f"- Financial Risk Index (lower is better): **{bm.get('financial_risk_index','-')}**")
    lines.append("")

    lines.append("## Mode3: Organization Dynamics (Demo)")
    lines.append(f"- Leadership Gap Index: **{case.get('org_model',{}).get('leadership_gap_index','-')}**")
    lines.append(f"- Succession Risk Indicator: **{case.get('org_model',{}).get('succession_risk_indicator','-')}**")
    # friction summary
    friction_map = (m3.get("friction_map") or case.get("org_model", {}).get("friction_map") or {})
    fps=[]
    for leader, roles in friction_map.items():
        for r, units in roles.items():
            for unit, fp in units.items():
                try: fps.append(float(fp))
                except: pass
    mean_fp = round(sum(fps)/len(fps), 4) if fps else None
    lines.append(f"- Mean Friction Probability: **{mean_fp if mean_fp is not None else '-'}**")
    lines.append("")

    lines.append("## Mode4: Scenario Branch (Demo)")
    if best:
        lines.append(f"- Best Scenario: **{best}** (Composite: **{best_score}**)")
    else:
        lines.append("- Best Scenario: -")
    lines.append("")
    lines.append("### Scenario Scores")
    for s in case.get("scenarios", []) or []:
        sid = s.get("scenario_id")
        cs = s.get("composite_score")
        lines.append(f"- {sid}: **{cs}**")
    lines.append("")

    lines.append("## Mode6/7: Synthesis (Demo)")
    lines.append(f"- Organizational Resilience Index: **{m6.get('organizational_resilience_index','-')}**")
    lines.append(f"- Executive Health Score: **{m7.get('executive_health_score','-')}**")
    comps = (m7.get("components") or {})
    if comps:
        lines.append("")
        lines.append("### Health Components")
        for k, val in comps.items():
            lines.append(f"- {k}: **{val}**")
    lines.append("")

    lines.append("## Notes")
    lines.append("- This is a demo report generated without proprietary AXIS/QCS runtime imports.")
    lines.append("- Indices and composites are lightweight placeholders for wiring and UX validation.")
    lines.append("")
    return "\n".join(lines)



def write_report_files(case: Dict[str, Any], out_dir: Path) -> Dict[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)

    md = render_executive_markdown(case)
    md_path = out_dir / "Executive_Report.demo.md"
    md_path.write_text(md, encoding="utf-8")

    pdf_path = out_dir / "Executive_Report.demo.v3.pdf"

    try:
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.lib import colors
    except Exception:
        return {"markdown": str(md_path), "pdf": "", "pdf_generated": "False"}

    styles = getSampleStyleSheet()
    brand_blue = colors.HexColor("#1C2F5C")
    brand_silver = colors.HexColor("#C0C0C0")

    title = ParagraphStyle("BrandTitle", parent=styles["Title"], fontSize=24, textColor=brand_blue, spaceAfter=12)
    h1 = ParagraphStyle("BrandH1", parent=styles["Heading1"], textColor=brand_blue)
    body = ParagraphStyle("BrandBody", parent=styles["BodyText"], leading=14)

    doc = SimpleDocTemplate(str(pdf_path), pagesize=A4)
    story = []

    # Cover
    story.append(Paragraph("STRATOSYNC", title))
    story.append(Paragraph("Human-Integrated Strategic Intelligence Platform", styles["Heading2"]))
    story.append(Spacer(1, 16))
    story.append(Paragraph(f"Case ID: {case.get('case_id','-')}", body))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Confidential Executive Briefing", styles["Italic"]))
    story.append(PageBreak())

    bm = case.get("business_model", {}) or {}
    m4 = case.get("mode4_scenarios", {}) or {}
    m7 = case.get("mode7_synthesis", {}) or {}

    best = m4.get("best_scenario_id","-")
    best_score = m4.get("best_score","-")

    story.append(Paragraph("Executive Summary", h1))
    story.append(Paragraph(f"Best strategic direction at this stage: <b>{best}</b> (Composite Score: <b>{best_score}</b>)", body))
    story.append(Spacer(1, 6))

    health = m7.get("executive_health_score","-")
    story.append(Paragraph(f"Executive Health Score: <b>{health}</b>", body))
    story.append(Spacer(1, 12))

    # Narrative reasoning
    reasoning = []
    if float(bm.get("financial_risk_index",50)) > 60:
        reasoning.append("Current cost structure and liquidity balance increase strategic pressure.")
    if float(bm.get("key_person_dependency_index",50)) < 50:
        reasoning.append("Organizational resilience is constrained by key-person reliance.")
    if not reasoning:
        reasoning.append("Structural indicators show balanced risk distribution in this phase.")

    story.append(Paragraph("Strategic Interpretation", styles["Heading2"]))
    tp_id = (case.get("versions",{}) or {}).get("template_pack_id","")
    if "SilverCare" in tp_id:
        k = (case.get("business_model",{}) or {}).get("kpi",{}) if isinstance((case.get("business_model",{}) or {}).get("kpi",{}), dict) else {}
        # Note: demo runner may not store kpi under business_model; so we ask case["input_kpi"] if exists
        k = case.get("input_kpi", k)
        occ = k.get("occupancy_rate")
        turn = k.get("turnover_rate")
        lab = k.get("labor_cost_ratio")
        if occ is not None:
            story.append(Paragraph(f"• Occupancy rate is {occ}% — stability is tightly coupled to staffing continuity.", body))
        if turn is not None:
            story.append(Paragraph(f"• Turnover is {turn}% — reduce churn via night-shift load balancing and role fit.", body))
        if lab is not None:
            story.append(Paragraph(f"• Labor cost ratio is {lab}% — monitor margin pressure and burnout signals.", body))

    for r in reasoning:
        story.append(Paragraph(f"• {r}", body))

    story.append(PageBreak())

    story.append(Paragraph("Scenario Comparison", h1))
    rows = [["Scenario","Composite"]]
    for s in case.get("scenarios",[]) or []:
        rows.append([str(s.get("scenario_id","-")), str(s.get("composite_score","-"))])

    t = Table(rows)
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),brand_blue),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("GRID",(0,0),(-1,-1),0.25,brand_silver),
    ]))
    story.append(t)

    story.append(Spacer(1, 20))
    story.append(Paragraph("STRATOSYNC | AXIS-X Executive Architecture v3", styles["Italic"]))

    doc.build(story)

    return {"markdown": str(md_path), "pdf": str(pdf_path), "pdf_generated": "True"}

    styles = getSampleStyleSheet()
    title = ParagraphStyle("TitleBig", parent=styles["Title"], fontSize=24, spaceAfter=12)
    h1 = ParagraphStyle("H1", parent=styles["Heading1"], spaceBefore=8, spaceAfter=6)
    body = ParagraphStyle("Body2", parent=styles["BodyText"], leading=14, spaceAfter=4)

    doc = SimpleDocTemplate(str(pdf_path), pagesize=A4)
    story = []

    # Cover
    story.append(Paragraph("STRATOSYNC", title))
    story.append(Paragraph("Human-Integrated Strategic Intelligence Platform", styles["Heading2"]))
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"Case ID: {case.get('case_id','-')}", body))
    story.append(Spacer(1, 12))
    story.append(PageBreak())

    bm = case.get("business_model", {}) or {}
    m4 = case.get("mode4_scenarios", {}) or {}
    m7 = case.get("mode7_synthesis", {}) or {}

    # Summary Page
    story.append(Paragraph("Executive Summary", h1))
    best = m4.get("best_scenario_id","-")
    best_score = m4.get("best_score","-")
    story.append(Paragraph(f"<b>Best Scenario:</b> {best} (Score: {best_score})", body))
    story.append(Spacer(1, 6))

    health = m7.get("executive_health_score","-")
    story.append(Paragraph(f"<b>Executive Health Score:</b> {health}", body))
    story.append(Spacer(1, 12))

    # Top 3 warning signals (simple heuristic)
    warnings = []
    if float(bm.get("financial_risk_index",50)) > 60:
        warnings.append("High financial risk pressure")
    if float(bm.get("key_person_dependency_index",50)) < 50:
        warnings.append("High key-person dependency")
    if not warnings:
        warnings.append("No major structural red flags detected (demo heuristic)")

    story.append(Paragraph("<b>Top Risk Signals</b>", styles["Heading2"]))
    for w in warnings:
        story.append(Paragraph(f"• {w}", body))

    story.append(PageBreak())

    # Detail: Scenario Table
    story.append(Paragraph("Scenario Comparison", h1))
    rows = [["Scenario","Composite"]]
    for s in case.get("scenarios",[]) or []:
        rows.append([str(s.get("scenario_id","-")), str(s.get("composite_score","-"))])
    t = Table(rows)
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.black),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("GRID",(0,0),(-1,-1),0.25,colors.grey),
    ]))
    story.append(t)

    doc.build(story)

    return {"markdown": str(md_path), "pdf": str(pdf_path), "pdf_generated": "True"}
def try_regenerate_pdf(markdown_path: Path, pdf_path: Path) -> bool:
    try:
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import inch
        from reportlab.lib import pagesizes
    except Exception:
        return False

    md = markdown_path.read_text(encoding="utf-8")
    doc = SimpleDocTemplate(str(pdf_path), pagesize=pagesizes.A4)
    styles = getSampleStyleSheet()
    elements = []
    for line in md.split("\n"):
        if line.startswith("# "):
            elements.append(Paragraph(line[2:], styles["Heading1"]))
        elif line.startswith("## "):
            elements.append(Paragraph(line[3:], styles["Heading2"]))
        elif line.startswith("### "):
            elements.append(Paragraph(line[4:], styles["Heading3"]))
        elif line.startswith("- "):
            elements.append(Paragraph("• " + line[2:], styles["BodyText"]))
        elif line.strip() == "":
            elements.append(Spacer(1, 0.15*inch))
        else:
            elements.append(Paragraph(line, styles["BodyText"]))
    doc.build(elements)
    return True

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Path to integrated_case JSON")
    ap.add_argument("--template", default=None, help="Path to TemplatePack JSON (optional)")
    ap.add_argument("--out", default="out_demo", help="Output directory")
    ap.add_argument("--regen-pdf", action="store_true", help="Try regenerating Executive PDF (requires reportlab)")
    ap.add_argument("--write-report", action="store_true", help="Write demo executive report (md + optional pdf)")
    args = ap.parse_args()

    in_path = Path(args.input)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    case = json.loads(in_path.read_text(encoding="utf-8"))
    missing = basic_validate(case)
    if missing:
        raise SystemExit(f"Invalid integrated_case: missing keys: {missing}")

    if args.template:
        tp_path = Path(args.template)
        tp = load_template_pack(tp_path)
        case = apply_template_pack(case, tp)
        case = compute_mode3_demo(case)
        case = compute_mode4_demo(case)

    case = compute_mode6_mode7_demo(case)

    out_case = out_dir / "integrated_case.updated.json"
    out_case.write_text(json.dumps(case, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote: {out_case}")

    if args.write_report:
        info = write_report_files(case, out_dir)
        print(f"Report markdown: {info['markdown']}")
        if info.get("pdf_generated") == "True":
            print(f"Report pdf: {info['pdf']}")
        else:
            print("Report pdf: (skipped; reportlab missing)")

    if args.regen_pdf:
        demo_exec_md = Path("05_STRATOSYNC_RELEASE_DEMO/STRATOSYNC_V1_RELEASE_COMPLETE/report_exec_v1.0.md")
        if demo_exec_md.exists():
            pdf_out = out_dir / "Executive_Report.updated.pdf"
            ok = try_regenerate_pdf(demo_exec_md, pdf_out)
            print("PDF regenerated" if ok else "PDF generation skipped (reportlab missing)")
        else:
            print("Executive markdown not found; skipping PDF regeneration.")

if __name__ == "__main__":
    main()
