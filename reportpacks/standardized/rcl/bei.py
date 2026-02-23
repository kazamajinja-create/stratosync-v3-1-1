from __future__ import annotations

import math
from typing import Dict, Any


def _risk_level(score_0_100: float) -> str:
    if score_0_100 < 40:
        return "STABLE"
    if score_0_100 < 70:
        return "CAUTION"
    return "EXPLOSION"


def calculate_branch_explosion_index(
    dof: Dict[str, Any],
    alpha: float = 0.08,
    normalize_divisor: float = 1000.0,
) -> Dict[str, Any]:
    """Branch Explosion Index (BEI).

    This is a pragmatic, bounded score intended to:
      - estimate scenario branching blow-up risk
      - recommend convergence actions (which constraints to fix first)

    Parameters
    ----------
    dof:
        degrees_of_freedom object with keys:
        strategy_options, affected_departments, uncertainty_index, change_scope
    alpha:
        industry-calibrated coefficient
    normalize_divisor:
        scalar used to compress raw exp growth into 0-100 range
    """

    strategy_options = max(1, int(dof.get("strategy_options", 1)))
    affected_departments = max(0, int(dof.get("affected_departments", 0)))
    uncertainty_index = float(dof.get("uncertainty_index", 0.0))
    change_scope = float(dof.get("change_scope", 0.0))

    # Effective degrees of freedom (n)
    n = (
        strategy_options
        * (affected_departments + 1)
        * (1.0 + max(0.0, min(1.0, uncertainty_index)))
        * (1.0 + max(0.0, min(1.0, change_scope)))
    )

    raw = math.exp(alpha * math.sqrt(n))
    score = min(100.0, (raw / float(normalize_divisor)) * 100.0)
    level = _risk_level(score)

    # Convergence suggestions: always return concrete actions
    suggestions = []
    if level == "EXPLOSION":
        suggestions = [
            "Fix constraints first (budget/time/quality caps) before exploring options.",
            "Reduce affected scope: pilot in 1 department before organization-wide change.",
            "Turn full exploration into conditional exploration (stage-gate).",
        ]
    elif level == "CAUTION":
        suggestions = [
            "Clarify decision boundaries: what must not change (non-negotiables).",
            "Freeze one variable (e.g., staffing) and re-run scenarios.",
        ]
    else:
        suggestions = [
            "Proceed with scenario comparison; branching complexity is in a stable band.",
        ]

    return {
        "bei_score": round(score, 2),
        "risk_level": level,
        "effective_dof": round(float(n), 4),
        "alpha": alpha,
        "suggestions": suggestions,
    }
