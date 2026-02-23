from __future__ import annotations

from typing import Any, Dict

from app.plan_manager.plans import CompanyPlan, PROFESSIONAL, ENTERPRISE
from app.core_engine.stratosync_math import (
    SurfaceInputs,
    compute_surface,
    compute_omega,
    compute_mode_indices,
    derive_demo_priors,
    clamp01,
    normalize_positive,
)
from app.core_engine.ramanujan_module import partition_estimate, ramanujan_pi_approx, TAXICAB_1729


def analyze_company(payload: Dict[str, Any], plan: CompanyPlan) -> Dict[str, Any]:
    """Primary analysis entrypoint for STRATOSYNC v3.1.1.

    - Always returns a deterministic, JSON-serializable dict.
    - Uses stable defaults when fields are missing.
    - Adds optional Ω-Surface + Ω-Combination + (B) Ramanujan-style explosive convergence indicators.
    """
    # ---- 0) Base / demo priors
    priors = derive_demo_priors(payload)
    metrics = priors.get("metrics", {})
    # Required core dimensions (0..1)
    P = clamp01(float(metrics.get("P", 0.55)))      # Profitability
    C = clamp01(float(metrics.get("C", 0.55)))      # Cohesion
    E = clamp01(float(metrics.get("E", 0.55)))      # Execution
    eta = clamp01(float(metrics.get("eta", 0.55)))  # Resilience

    # Risk proxies (0..1) where higher is worse
    bias_risk = clamp01(float(metrics.get("BiasRisk", payload.get("bias_risk", 0.35)) or 0.35))
    friction_risk = clamp01(float(metrics.get("F", payload.get("friction", 0.35)) or 0.35))

    # ---- 1) Ω-Surface (C) boundary model
    surface_inputs = SurfaceInputs(
        customer_touchpoints=float(payload.get("customer_touchpoints", 6)),
        brand_exposure=float(payload.get("brand_exposure", 5)),
        partner_links=float(payload.get("partner_links", 3)),
        api_connections=float(payload.get("api_connections", 0)),
        data_contact_freq=float(payload.get("data_contact_freq", 4)),
        internal_volume=float(payload.get("internal_volume", payload.get("headcount", 10) or 10)),
    )
    surface = compute_surface(surface_inputs, weights=payload.get("surface_weights"))

    # Normalize SE and OPI into [0,1] for fusion hooks
    SE_n = normalize_positive(surface.get("SE_surface_efficiency", 0.0), scale=2.5)

    # ---- 2) Ω-Combination (A) model
    n_eff = int(payload.get("n_effective", payload.get("headcount", 10) or 10))
    omega = compute_omega(n_eff)
    OPI_n = normalize_positive(omega.get("OPI_logOmega", 0.0), scale=4.0)

    # ---- 3) (B) Explosive convergence indicators (Ramanujan-style)
    # NOTE: used as *secondary* signal: "potential state-space" size proxy.
    # We keep it deterministic and cheap.
    p_est = partition_estimate(max(n_eff, 0))
    # Turn it into a bounded index using log scaling.
    explosion_index = normalize_positive(p_est.get("log_p_est", 0.0), scale=10.0)
    pi_demo = ramanujan_pi_approx(terms=int(payload.get("pi_terms", 1)))

    # ---- 4) Mode fusion (BI/HI/OI + surface/omega hooks)
    BI = clamp01(0.40 * P + 0.30 * E + 0.30 * eta)
    HI = clamp01(0.45 * (1.0 - bias_risk) + 0.30 * C + 0.25 * eta)
    OI = clamp01(0.45 * C + 0.35 * E + 0.20 * (1.0 - friction_risk))

    fusion = compute_mode_indices(
        BI, HI, OI, SE_n, OPI_n,
        lambdas=payload.get("fusion_lambdas"),
    )

    from app.core_engine.model_versions import MODEL_VERSION, ENGINE_FAMILY, MATH_PROFILE, FORMULA_LOCK

    result: Dict[str, Any] = {
        "engine": ENGINE_FAMILY,
        "model_version": MODEL_VERSION,
        "math_profile": MATH_PROFILE,
        "formula_lock": FORMULA_LOCK,
        "plan": plan.key,
        "metrics": {
            **metrics,
            "BI": round(BI, 6),
            "HI": round(HI, 6),
            "OI": round(OI, 6),
            "BiasRisk": round(bias_risk, 6),
            "F": round(friction_risk, 6),
        },
        "omega_surface": surface,
        "omega_combination": omega,
        "math_B_explosive": {
            "partition_estimate": p_est,
            "explosion_index": round(explosion_index, 6),
            "pi_demo": pi_demo,
            "taxicab": TAXICAB_1729,
        },
        "mode_fusion": fusion,
    }

    # ---- 5) Plan gating
    if plan.key == PROFESSIONAL.key:
        m = result.get("metrics", {})
        compact = {
            "Business_Health_Index": m.get("R", m.get("R_total", None)),
            "Profitability_Index": m.get("P", None),
            "Cohesion_Index": m.get("C", None),
            "Execution_Index": m.get("E", None),
            "Resilience_Index": m.get("eta", None),
            "Friction_Risk": m.get("F", None),
            "Decision_Bias_Risk": m.get("BiasRisk", None),
        }
        result["panel_7"] = compact
        # Keep surface/omega signals but omit deep blocks if requested
        if payload.get("pro_compact", True):
            # Remove verbose extras
            result.pop("math_B_explosive", None)

    if plan.key == ENTERPRISE.key:
        result.setdefault("api", {"enabled": True, "limits": "none"})
        result.setdefault("reportpacks", {"enabled": True, "scope": "all"})

    return result



def run_analysis(payload: Dict[str, Any], plan_key: str = "enterprise") -> Dict[str, Any]:
    """Backward-compatible wrapper used by API routes."""
    from app.plan_manager.plans import plan_from_key
    plan = plan_from_key(plan_key)
    return analyze_company(payload, plan)
