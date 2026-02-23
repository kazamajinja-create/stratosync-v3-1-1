from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class RiskItem:
    category: str
    description: str
    probability_range: str
    impact_level: str
    explainability: str

def build_risk_taxonomy(structure: Dict[str, str], indices: Dict[str, str], tendency_model: Dict) -> List[RiskItem]:
    risks: List[RiskItem] = []
    sc = indices.get("構造集中指数")
    cr = indices.get("コスト硬直指数")
    vol = indices.get("変動性指数")

    if cr == "固定費高":
        risks.append(RiskItem("財務", "固定費構造により損益が振れやすい", "medium~high", "medium~high", "根拠: コスト硬直指数=固定費高"))
    if vol == "高":
        risks.append(RiskItem("財務", "キャッシュフロー波形が不安定に見えやすい", "medium~high", "medium", "根拠: 変動性指数=高"))
    if sc == "集中":
        risks.append(RiskItem("オペレーション", "集中点に障害が出ると連鎖的に影響が広がりやすい", "medium", "medium~high", "根拠: 構造集中指数=集中"))

    dep = structure.get("dependency", "")
    if dep:
        risks.append(RiskItem("人的依存", "属人性・暗黙知がボトルネックになりやすい", "medium", "medium", f"根拠: dependency={dep}"))

    risks.append(RiskItem("レピュテーション", "外部説明の論点化（なぜその選択か）が強まりやすい", "medium", "medium", "根拠: 不確定性明示により説明粒度が問われる"))
    risks.append(RiskItem("法務", "契約・表示・個人情報・権利などの論点が関わる可能性", "unknown", "unknown", "注意: 具体判断は専門家レビューが必要"))
    return risks
