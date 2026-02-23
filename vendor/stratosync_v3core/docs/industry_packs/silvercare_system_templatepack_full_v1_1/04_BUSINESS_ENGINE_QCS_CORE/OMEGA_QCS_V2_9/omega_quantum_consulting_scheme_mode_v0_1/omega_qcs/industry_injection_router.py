from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple

from .external_factor_sensitivity_defaults import DEFAULT_SENSITIVITY_MATRIX
from .industry_risk_dictionary_extended import INDUSTRY_RISK_DICTIONARY_EXTENDED
from .market_context_injector import InjectorParams

@dataclass
class IndustryInjectionPolicy:
    # default strategy if no industry match
    strategy: str = "A"
    # default sensitivity matrix
    sensitivity_matrix: Dict[str, Dict[str, float]] = None
    # default injector params
    injector_params: InjectorParams = InjectorParams()
    # optional competitor velocity default
    competitor_velocity: float = 0.0

def _deepcopy_matrix(m: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, float]]:
    return {k: dict(v) for k, v in (m or {}).items()}

def choose_strategy_by_industry(industry_key: str) -> str:
    k = (industry_key or "").strip().lower()
    # Heuristic policy:
    # - Agriculture / heavily regulated / exogenous shocks -> B
    # - SaaS / fast competitive velocity -> C
    # - Default -> A
    if k in ["agriculture", "healthcare", "finance", "manufacturing", "energy", "logistics"]:
        return "B"
    if k in ["saas", "software", "ai", "ecommerce", "media", "gaming", "consulting"]:
        return "C"
    if k in ["community_management", "education"]:
        # depends; keep A unless user supplies competitor velocity
        return "A"
    return "A"

def build_sensitivity_matrix_for_industry(industry_key: str) -> Dict[str, Dict[str, float]]:
    """Start from defaults; optionally adjust weights using industry risk dictionary.
    Risk dictionary keys are NOT 1:1 to 12 vars, so we apply a conservative adjustment:
    - If industry has high platform/competition/tech disruption, increase C weights for E/H/X/G
    - If high regulation/exogenous, increase R weights for S/R/T/P
    This preserves explainability and auditability.
    """
    k = (industry_key or "").strip().lower()
    base = _deepcopy_matrix(DEFAULT_SENSITIVITY_MATRIX)

    risks = INDUSTRY_RISK_DICTIONARY_EXTENDED.get(k, {})
    if not risks:
        return base

    # Simple derived signals (0..1), conservative caps
    comp_signal = max([float(risks.get(x, 0.0)) for x in ["tech_disruption_speed","ai_competition_pressure","pricing_pressure","market_cyclical_exposure","platform_dependency"]], default=0.0)
    reg_signal = max([float(risks.get(x, 0.0)) for x in ["regulatory_change_frequency","regulatory_pressure","import_regulation","insurance_reimbursement_risk"]], default=0.0)
    macro_signal = max([float(risks.get(x, 0.0)) for x in ["currency_exposure","energy_cost_volatility","commodity_price_risk","climate_volatility"]], default=0.0)

    # Normalize to 0..1-ish (risk weights already 0..1); apply small deltas
    def bump(var, key, delta):
        base[var][key] = min(1.0, max(0.0, float(base[var].get(key, 0.5)) + delta))

    # Competition-related bumps
    if comp_signal > 0.0:
        d = min(0.15, 0.10 * comp_signal)
        for v in ["E","H","X","G","B"]:
            bump(v, "C", d)

    # Regulation / exogenous bumps
    if reg_signal > 0.0:
        d = min(0.15, 0.10 * reg_signal)
        for v in ["S","R","T","P","D"]:
            bump(v, "R", d)

    # Macro volatility bumps
    if macro_signal > 0.0:
        d = min(0.12, 0.08 * macro_signal)
        for v in ["D","B","T","M"]:
            bump(v, "M", d)

    return base

def resolve_injection_policy(
    industry_key: Optional[str],
    competitor_velocity: Optional[float] = None,
    override_strategy: Optional[str] = None,
    override_matrix: Optional[Dict[str, Dict[str, float]]] = None,
    override_params: Optional[InjectorParams] = None,
) -> IndustryInjectionPolicy:
    strategy = (override_strategy or choose_strategy_by_industry(industry_key)).upper()
    matrix = override_matrix or build_sensitivity_matrix_for_industry(industry_key or "")
    params = override_params or InjectorParams()
    cv = float(competitor_velocity) if competitor_velocity is not None else 0.0
    return IndustryInjectionPolicy(strategy=strategy, sensitivity_matrix=matrix, injector_params=params, competitor_velocity=cv)
