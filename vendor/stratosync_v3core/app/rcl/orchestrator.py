from __future__ import annotations

from typing import Any, Dict, List

from app.rcl.bei import calculate_branch_explosion_index
from app.rcl.ece import calculate_early_convergence
from app.rcl.tcd import detect_twin_causes
from app.rcl.rsm import residual_monitor


def run_rcl(case: Dict[str, Any], industry_params: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Run the Ramanujan Convergence Layer on an integrated case.

    Parameters
    ----------
    case:
        Integrated case dict (see app/rcl/models.py)
    industry_params:
        Optional industry calibration:
        {"bei_alpha": 0.08, "ece_prior": {...}, "rsm_threshold": 0.15}
    """

    industry_params = industry_params or {}

    dof = case.get("degrees_of_freedom", {}) or {}
    coverage = case.get("data_coverage", {}) or {}
    mode_outputs = case.get("mode_outputs", {}) or {}
    kpi_series = case.get("kpi_timeseries", []) or []
    interventions = case.get("interventions", []) or []

    bei = calculate_branch_explosion_index(dof, alpha=float(industry_params.get("bei_alpha", 0.08)))
    ece = calculate_early_convergence(coverage, mode_outputs=mode_outputs, industry_prior=industry_params.get("ece_prior"))

    # Twin cause hints can be passed from mode outputs if available
    hints = {}
    if isinstance(mode_outputs, dict):
        hints.update(mode_outputs.get("hints", {}) or {})
    tcd = detect_twin_causes(kpi_series, interventions, hints=hints)

    # Residual: if caller provides predicted/actual, use; else try profit last vs prev
    pred = None
    act = None
    if isinstance(mode_outputs, dict) and isinstance(mode_outputs.get("predicted"), dict):
        pred = mode_outputs.get("predicted", {}).get("profit")
        act = mode_outputs.get("actual", {}).get("profit") if isinstance(mode_outputs.get("actual"), dict) else None
    if pred is None or act is None:
        # fallback to profit movement magnitude (coarse)
        if len(kpi_series) >= 2:
            pred = kpi_series[-2].get("profit")
            act = kpi_series[-1].get("profit")

    rsm = residual_monitor(predicted=pred, actual=act, threshold=float(industry_params.get("rsm_threshold", 0.15)))

    return {
        "branch_explosion": bei,
        "convergence": ece,
        "twin_cause": tcd,
        "residual": rsm,
    }
