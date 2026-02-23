from __future__ import annotations

from typing import Any, Dict, List


def _get_last_two(series: List[Dict[str, Any]], key: str) -> tuple[float | None, float | None]:
    vals = []
    for r in series[-2:]:
        v = r.get(key)
        if v is None:
            vals.append(None)
        else:
            try:
                vals.append(float(v))
            except Exception:
                vals.append(None)
    if len(vals) == 1:
        vals = [None, vals[0]]
    return vals[0] if vals else None, vals[1] if len(vals) > 1 else None


def detect_twin_causes(
    kpi_timeseries: List[Dict[str, Any]],
    interventions: List[Dict[str, Any]],
    hints: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Twin-Cause Detector (TCD).

    Identifies when a KPI movement could plausibly be explained by multiple causes.
    This is a lightweight MVP heuristic (no causal graph) intended to reduce
    overconfident attribution in reports.
    """

    hints = hints or {}
    possible: List[Dict[str, Any]] = []
    notes: List[str] = []

    # KPI movement (revenue/profit)
    r0, r1 = _get_last_two(kpi_timeseries, "revenue")
    p0, p1 = _get_last_two(kpi_timeseries, "profit")

    def delta(a: float | None, b: float | None) -> float | None:
        if a is None or b is None:
            return None
        return b - a

    dr = delta(r0, r1)
    dp = delta(p0, p1)

    # Intervention signals
    types = [str(i.get("type")) for i in interventions if i.get("type")]
    if any("marketing" in t for t in types):
        possible.append({"cause": "Marketing/Acquisition Effect", "evidence": "marketing intervention logged"})
    if any("staff" in t or "reallocation" in t for t in types):
        possible.append({"cause": "Org/Human Reconfiguration Effect", "evidence": "staff reallocation logged"})
    if any("pricing" in t for t in types):
        possible.append({"cause": "Pricing Effect", "evidence": "pricing change logged"})

    # Hints: friction drop etc.
    if hints.get("friction_drop") is True:
        possible.append({"cause": "Friction Relief Effect", "evidence": "friction index drop"})

    # If KPI improved but no interventions, flag unknown latent factors
    improved = (dr is not None and dr > 0) or (dp is not None and dp > 0)
    if improved and not possible:
        possible.append({"cause": "Latent/External Factors", "evidence": "KPI improved without logged interventions"})
        notes.append("Consider capturing external events and informal changes.")

    ambiguity = len({p["cause"] for p in possible}) >= 2

    # Minimal disambiguation tests
    tests = []
    if ambiguity:
        tests = [
            "Check time-lag: did KPI move immediately after the intervention?",
            "Cross-check with org signals (overtime, complaints, absenteeism).",
            "Run a counterfactual: what KPI would look like without the intervention?",
        ]

    return {
        "kpi_delta": {"revenue": dr, "profit": dp},
        "possible_causes": possible,
        "ambiguity_flag": ambiguity,
        "disambiguation_tests": tests,
        "notes": notes,
    }
