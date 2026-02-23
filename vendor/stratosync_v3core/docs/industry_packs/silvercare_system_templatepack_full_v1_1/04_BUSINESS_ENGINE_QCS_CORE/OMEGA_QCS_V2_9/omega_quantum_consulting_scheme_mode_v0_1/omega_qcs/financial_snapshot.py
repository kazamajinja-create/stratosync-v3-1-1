
from dataclasses import dataclass
from typing import Dict

@dataclass
class FinancialSnapshot:
    period: str
    revenue_concentration: str
    cost_structure: str
    cashflow_pattern: str
    volatility_flag: str

def build_snapshot(financials: Dict) -> FinancialSnapshot:
    revenue_concentration = "集中" if financials.get("top_revenue_ratio",0) > 0.6 else "分散"
    cost_structure = "固定費高" if financials.get("fixed_cost_ratio",0) > 0.5 else "変動費中心"
    cashflow_pattern = financials.get("cf_pattern","不明")
    volatility_flag = "高" if financials.get("variance",0) > 0.3 else "低"
    return FinancialSnapshot(
        period = financials.get("period","unknown"),
        revenue_concentration = revenue_concentration,
        cost_structure = cost_structure,
        cashflow_pattern = cashflow_pattern,
        volatility_flag = volatility_flag
    )
