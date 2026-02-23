from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class FinancialImpactRange:
    revenue_range: Dict[str, str]        # Low/Mid/High (descriptive ranges)
    margin_sensitivity: Dict[str, str]   # fixed/variable implications
    cashflow_waveform: str              # stable / high_amplitude / intermittent
    notes: List[str]

def estimate_financial_impact_range(
    indices: Dict[str, str],
    tendency_model: Optional[Dict] = None,
    inputs_hint: Optional[Dict] = None
) -> FinancialImpactRange:
    """Estimate *ranges* and qualitative impacts. No guarantees."""
    tendency_model = tendency_model or {}
    inputs_hint = inputs_hint or {}

    sc = indices.get("構造集中指数")
    cr = indices.get("コスト硬直指数")
    vol = indices.get("変動性指数")

    if sc == "集中" and vol == "高":
        revenue_range = {"Low": "下振れ局面が出やすい", "Mid": "分岐が大きい", "High": "条件成立時に跳ねやすい"}
    elif sc == "分散" and vol == "低":
        revenue_range = {"Low": "急落は起こりにくい", "Mid": "安定推移しやすい", "High": "伸びは累積効果に依存しやすい"}
    else:
        revenue_range = {"Low": "下振れ余地あり", "Mid": "標準的な幅", "High": "上振れ余地あり"}

    if cr == "固定費高":
        margin_sensitivity = {
            "Sensitivity": "売上変動に対して利益率が振れやすい",
            "Mechanism": "固定費比率が高いほど損益振幅が増える",
        }
        cashflow_waveform = "high_amplitude" if vol == "高" else "intermittent"
    else:
        margin_sensitivity = {
            "Sensitivity": "売上変動に対して利益率が追随しやすい",
            "Mechanism": "変動費中心だと調整が効きやすい",
        }
        cashflow_waveform = "stable" if vol == "低" else "intermittent"

    notes = [
        "本出力は財務インパクトの『レンジ（幅）』を示すもので、将来の数値を断定しません。",
        "NPV/IRR等の投資指標算定、会計判断、税務判断は行いません。",
    ]
    return FinancialImpactRange(
        revenue_range=revenue_range,
        margin_sensitivity=margin_sensitivity,
        cashflow_waveform=cashflow_waveform,
        notes=notes,
    )
