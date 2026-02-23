from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class GrowthDriverMap:
    revenue_levers: List[str]
    cost_levers: List[str]
    trust_levers: List[str]
    scalability_notes: List[str]
    repeatability: str  # strong/medium/weak/unknown

def map_growth_drivers(structure: Dict[str, str], indices: Dict[str, str]) -> GrowthDriverMap:
    sc = indices.get("構造集中指数")
    cr = indices.get("コスト硬直指数")

    revenue: List[str] = []
    cost: List[str] = []
    trust: List[str] = []
    notes: List[str] = []

    if sc == "集中":
        revenue += ["集中対象の強化（深耕・単価・継続）", "集中対象の分散（新規セグメント・チャネル）"]
        trust += ["集中理由の説明可能性を上げる（外部説明耐性）"]
        notes += ["集中構造は伸びも鈍化も大きく、分岐管理が重要になりやすい"]
        repeatability = "medium"
    else:
        revenue += ["複数要因の積み上げ（獲得×継続×単価）"]
        trust += ["一貫した体験設計による信用の積み上げ"]
        notes += ["分散構造は急伸よりも累積成長になりやすい"]
        repeatability = "strong"

    if cr == "固定費高":
        cost += ["固定費の段階投資・分割（機能分離）", "固定費の変動化（外注/成果連動）"]
        notes += ["固定費構造はスケールに有利/不利が分かれやすい"]
    else:
        cost += ["変動費の品質維持とスループット最適化"]
        notes += ["変動費中心は調整しやすいが品質摩耗に注意が必要"]

    return GrowthDriverMap(revenue, cost, trust, notes, repeatability)
