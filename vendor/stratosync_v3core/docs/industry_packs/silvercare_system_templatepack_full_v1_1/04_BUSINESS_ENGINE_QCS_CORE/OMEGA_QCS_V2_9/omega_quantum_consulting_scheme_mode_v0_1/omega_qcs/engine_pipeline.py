from __future__ import annotations
from dataclasses import asdict
from typing import Dict, Optional, Any

from .normalize_financials import normalize
from .financial_snapshot import build_snapshot
from .structure_indices import extract_indices
from .tendency_model import build_tendency_model
from .option_space import expand_option_space

from .financial_impact_range import estimate_financial_impact_range
from .execution_capacity import assess_execution_capacity
from .risk_taxonomy import build_risk_taxonomy
from .growth_driver import map_growth_drivers
from .stakeholder_matrix import build_stakeholder_matrix
from .kpi_monitoring import design_kpi_monitoring

def run_business_competition_pipeline(
    financials: Optional[Dict] = None,
    structure: Optional[Dict[str, str]] = None,
    uncertainty: Optional[Dict[str, str]] = None,
    constraints: Optional[Dict[str, str]] = None,
    known_options: Optional[list] = None
) -> Dict[str, Any]:
    structure = structure or {}
    uncertainty = uncertainty or {}
    constraints = constraints or {}
    known_options = known_options or []

    snapshot_dict = None
    if financials:
        fin = normalize(financials)
        derived = fin.get("derived", {})
        snap = build_snapshot({
            "period": fin.get("period"),
            "top_revenue_ratio": derived.get("top_revenue_ratio", 0),
            "fixed_cost_ratio": derived.get("fixed_cost_ratio", 0),
            "cf_pattern": derived.get("cf_pattern", "不明"),
            "variance": derived.get("variance", 0),
        })
        snapshot_dict = asdict(snap)
        indices = extract_indices(snapshot_dict)
    else:
        indices = {
            "構造集中指数": structure.get("structure_concentration", "不明"),
            "コスト硬直指数": structure.get("cost_rigidity", "不明"),
            "資金流動指数": structure.get("cashflow_pattern", "不明"),
            "変動性指数": structure.get("volatility", "不明"),
        }

    tendency = build_tendency_model(indices)
    option_space = expand_option_space(structure=structure, indices=indices, uncertainty=uncertainty, constraints=constraints, known_options=known_options)

    fin_range = estimate_financial_impact_range(indices, tendency_model=tendency, inputs_hint=financials or {})
    exec_cap = assess_execution_capacity(structure=structure, indices=indices, constraints=constraints)
    risks = build_risk_taxonomy(structure=structure, indices=indices, tendency_model=tendency)
    growth = map_growth_drivers(structure=structure, indices=indices)
    stakeholders = build_stakeholder_matrix(structure=structure, indices=indices)
    kpi_plan = design_kpi_monitoring(structure=structure, indices=indices, option_space=option_space)

    return {
        "snapshot": snapshot_dict,
        "indices": indices,
        "tendency_model": tendency,
        "option_space": option_space,
        "financial_impact_range": asdict(fin_range),
        "execution_capacity": asdict(exec_cap),
        "risk_taxonomy": [r.__dict__ for r in risks],
        "growth_driver_map": growth.__dict__,
        "stakeholder_matrix": [s.__dict__ for s in stakeholders],
        "kpi_monitoring_plan": kpi_plan.__dict__,
    }
