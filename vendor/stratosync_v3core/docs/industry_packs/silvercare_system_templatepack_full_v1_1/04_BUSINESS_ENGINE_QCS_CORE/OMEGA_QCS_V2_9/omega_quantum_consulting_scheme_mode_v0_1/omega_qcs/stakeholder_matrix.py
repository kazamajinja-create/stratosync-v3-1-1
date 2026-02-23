from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class StakeholderImpact:
    stakeholder: str
    likely_concerns: List[str]
    alignment: str
    explanation_burden: str

def build_stakeholder_matrix(structure: Dict[str, str], indices: Dict[str, str]) -> List[StakeholderImpact]:
    sc = indices.get("構造集中指数")
    vol = indices.get("変動性指数")

    items: List[StakeholderImpact] = []
    items.append(StakeholderImpact("経営層", ["分岐管理", "説明責任", "資源配分"], "aligned", "medium" if vol == "高" else "low"))

    ops = ["実装負荷", "運用安定", "役割分離"]
    if sc == "集中":
        ops.append("集中点の冗長化")
    items.append(StakeholderImpact("現場/運用", ops, "partially_aligned", "medium"))

    items.append(StakeholderImpact("顧客/参加者", ["体験の一貫性", "価格/条件の変化", "信頼"], "unknown", "medium"))
    items.append(StakeholderImpact("投資家/外部関係者", ["継続性", "再現性", "リスク説明", "キャッシュフロー波形"], "unknown", "high"))
    items.append(StakeholderImpact("外部評価/レピュテーション", ["外部説明の粒度", "なぜその選択か", "一貫性"], "unknown", "high" if vol == "高" else "medium"))
    return items
