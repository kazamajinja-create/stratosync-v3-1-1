"""
QCS Dental Plugin v1 - Scoring Engine (Reference Implementation)

NOTE:
- The "structure" (what we evaluate) is public.
- The "exact thresholds / weights" may be treated as proprietary.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Tuple
import json
import os
import math


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def to_0_100(score_0_5: float) -> float:
    return clamp(score_0_5, 0.0, 5.0) * 20.0


def grade(score_0_100: float) -> str:
    if score_0_100 >= 85: return "A"
    if score_0_100 >= 70: return "B"
    if score_0_100 >= 55: return "C"
    if score_0_100 >= 40: return "D"
    return "E"


# --- 0-5 scoring rules (editable; keep simple & defensible) -------------------
def score_fixed_cost_ratio(r: float) -> float:
    # lower is better
    # <0.45 => 5, 0.45-0.55 => 4, 0.55-0.65 => 3, 0.65-0.75 => 2, 0.75-0.85 => 1, else 0
    if r < 0.45: return 5
    if r < 0.55: return 4
    if r < 0.65: return 3
    if r < 0.75: return 2
    if r < 0.85: return 1
    return 0


def score_cash_runway(m: float) -> float:
    # higher is better
    if m >= 12: return 5
    if m >= 9: return 4
    if m >= 6: return 3
    if m >= 4: return 2
    if m >= 2: return 1
    return 0


def score_depr_burden_ratio(r: float) -> float:
    # lower is better
    if r < 0.04: return 5
    if r < 0.06: return 4
    if r < 0.08: return 3
    if r < 0.10: return 2
    if r < 0.12: return 1
    return 0


def score_unit_utilization(r: float) -> float:
    # moderate-to-high is good; too high may imply overload but still better than underused in early version
    if r >= 0.85: return 5
    if r >= 0.75: return 4
    if r >= 0.65: return 3
    if r >= 0.55: return 2
    if r >= 0.45: return 1
    return 0


def score_owner_dependency_ratio(r: float) -> float:
    # lower is better
    if r < 0.35: return 5
    if r < 0.45: return 4
    if r < 0.55: return 3
    if r < 0.65: return 2
    if r < 0.75: return 1
    return 0


def score_hygienist_retention_rate(r: float) -> float:
    # higher is better
    if r >= 0.90: return 5
    if r >= 0.85: return 4
    if r >= 0.80: return 3
    if r >= 0.75: return 2
    if r >= 0.70: return 1
    return 0


def score_shock_profit_residual(kpis: Dict[str, float]) -> float:
    """
    Proxy: If visits drop -10%, revenue drops similarly.
    Residual depends on fixed_cost_ratio.
    residual_profit_ratio ~= 1 - (fixed_cost_ratio * shock)
    This is a simplification for early field use.
    """
    fixed = kpis["fixed_cost_ratio"]
    shock = 0.10
    residual = 1.0 - fixed * shock * 5.0  # amplified to reflect fragility; tune later
    residual = clamp(residual, 0.0, 1.0)
    # map residual to 0-5
    if residual >= 0.85: return 5
    if residual >= 0.75: return 4
    if residual >= 0.65: return 3
    if residual >= 0.55: return 2
    if residual >= 0.45: return 1
    return 0


def score_oop_shock_sensitivity(kpis: Dict[str, float]) -> float:
    """
    Proxy: If oop_ratio decreases by -5pt, margin sensitivity increases with oop share.
    Higher oop share => potentially higher sensitivity. We score *stability*, so lower sensitivity is better.
    """
    oop = kpis["oop_ratio"]
    # sensitivity proxy: oop * 1.0 (0-1)
    s = oop
    # stable if s is moderate; very high oop means more volatility in downturns
    if s < 0.20: return 4  # low oop, stable but maybe growth limited
    if s < 0.35: return 5
    if s < 0.50: return 4
    if s < 0.65: return 3
    if s < 0.80: return 2
    return 1


def score_goal_gap_proxy(kpis: Dict[str, float]) -> float:
    """
    If you don't have explicit targets yet, use revenue growth as a proxy.
    Higher stable growth => smaller gap.
    """
    g = kpis["rev_growth_mom"]
    if g >= 0.02: return 5
    if g >= 0.00: return 4
    if g >= -0.02: return 3
    if g >= -0.05: return 2
    if g >= -0.08: return 1
    return 0


def weighted_avg(scores: Dict[str, float], weights: Dict[str, float]) -> float:
    num = 0.0
    den = 0.0
    for k, w in weights.items():
        if k not in scores:
            continue
        num += scores[k] * w
        den += w
    return num / den if den > 0 else 0.0


def load_weights(config_path: str) -> Dict[str, Any]:
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def score_all(payload: Dict[str, Any], config_path: str) -> Dict[str, Any]:
    k = payload["kpis"]

    weights = load_weights(config_path)

    # core scored components (0-5)
    drs_components = {
        "shock_profit_residual": score_shock_profit_residual(k),
        "oop_shock_sensitivity": score_oop_shock_sensitivity(k),
        "fixed_cost_ratio": score_fixed_cost_ratio(k["fixed_cost_ratio"]),
        "cash_runway_months": score_cash_runway(k["cash_runway_months"]),
        "depr_burden_ratio": score_depr_burden_ratio(k["depr_burden_ratio"]),
        "unit_utilization": score_unit_utilization(k["unit_utilization"]),
    }
    drs_0_5 = weighted_avg(drs_components, weights["DRS"])
    drs_0_100 = to_0_100(drs_0_5)

    ddi_components = {
        "new_patient_rate_trend": 4 if k["new_patient_rate"] >= 0.18 else 3 if k["new_patient_rate"] >= 0.12 else 2 if k["new_patient_rate"] >= 0.08 else 1,
        "cancel_rate": 5 if k["cancel_rate"] < 0.03 else 4 if k["cancel_rate"] < 0.05 else 3 if k["cancel_rate"] < 0.07 else 2 if k["cancel_rate"] < 0.10 else 1,
        "review_rating_trend": 5 if k["review_rating_trend"] >= 0.05 else 4 if k["review_rating_trend"] >= 0.00 else 3 if k["review_rating_trend"] >= -0.05 else 2 if k["review_rating_trend"] >= -0.10 else 1,
        "rev_per_staff_trend": 4 if k["rev_per_staff"] >= 1200000 else 3 if k["rev_per_staff"] >= 900000 else 2 if k["rev_per_staff"] >= 700000 else 1,
        "competitor_change": 4 if k["competitor_change"] <= 0 else 3 if k["competitor_change"] <= 1 else 2 if k["competitor_change"] <= 2 else 1,
        "goal_gap_proxy": score_goal_gap_proxy(k),
    }
    ddi_0_5 = weighted_avg(ddi_components, weights["DDI"])
    ddi_0_100 = to_0_100(ddi_0_5)

    ders_components = {
        "owner_dependency_ratio": score_owner_dependency_ratio(k["owner_dependency_ratio"]),
        "hygienist_retention_rate": score_hygienist_retention_rate(k["hygienist_retention_rate"]),
        # the following are collected via short survey (0-5 directly)
        "standardization_level": float(k.get("standardization_level", 3.0)),
        "delegation_level": float(k.get("delegation_level", 2.5)),
        "succession_readiness": float(k.get("succession_readiness", 2.0)),
    }
    ders_0_5 = weighted_avg(ders_components, weights["DeRS"])
    ders_0_100 = to_0_100(ders_0_5)

    sci_components = {
        "kpi_visibility": float(k.get("kpi_visibility", 2.5)),
        "meeting_structure": float(k.get("meeting_structure", 2.0)),
        "role_clarity": float(k.get("role_clarity", 2.5)),
        "data_sharing_frequency": float(k.get("data_sharing_frequency", 2.0)),
        "initiative_tracking": float(k.get("initiative_tracking", 2.0)),
    }
    sci_0_5 = weighted_avg(sci_components, weights["SCI"])
    sci_0_100 = to_0_100(sci_0_5)

    global_0_100 = (
        drs_0_100 * weights["GLOBAL"]["DRS"] +
        ddi_0_100 * weights["GLOBAL"]["DDI"] +
        ders_0_100 * weights["GLOBAL"]["DeRS"] +
        sci_0_100 * weights["GLOBAL"]["SCI"]
    )

    out = {
        "clinic": payload["clinic_profile"],
        "scores": {
            "DRS": {"score_0_5": round(drs_0_5,2), "score_0_100": round(drs_0_100,1), "grade": grade(drs_0_100)},
            "DDI": {"score_0_5": round(ddi_0_5,2), "score_0_100": round(ddi_0_100,1), "grade": grade(ddi_0_100)},
            "DeRS": {"score_0_5": round(ders_0_5,2), "score_0_100": round(ders_0_100,1), "grade": grade(ders_0_100)},
            "SCI": {"score_0_5": round(sci_0_5,2), "score_0_100": round(sci_0_100,1), "grade": grade(sci_0_100)},
            "GLOBAL": {"score_0_100": round(global_0_100,1), "grade": grade(global_0_100)}
        },
        "components": {
            "DRS": drs_components,
            "DDI": ddi_components,
            "DeRS": ders_components,
            "SCI": sci_components
        }
    }
    return out
