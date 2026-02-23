from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class ExternalView:
    critiques: List[str]
    misunderstandings: List[str]
    needs_explanation: List[str]

DEFAULT_EXTERNAL_VIEW = ExternalView(
    critiques=[
        "価格が高額に見える（内容より『覚悟』の対価である点が伝わらない可能性）",
        "限定数が排他的に見える（品質維持のための上限である点が伝わらない可能性）",
    ],
    misunderstandings=[
        "認定/資格ビジネスに見える（実際は認定を出さない設計）",
        "スピリチュアル/精神論に見える（実際は意思決定の構造整理が中核）",
        "成功保証に見える（実際は保証しない/決断は本人）",
    ],
    needs_explanation=[
        "高額である理由（囲い込みをしない/保証しない/少人数で深度を担保）",
        "卒業後の関係性（契約で縛らない/自然な紹介・協業）",
        "提供範囲と責任帰属（情報整理・構造可視化・視点提示／決断はクライアント）",
    ],
)

def simulate_for_scheme(context: str | None = None) -> Dict:
    """
    Minimal simulator (v0.5):
    returns 'third-party view' points for risk management.
    """
    # context reserved for future; for now return defaults.
    return {
        "critiques": DEFAULT_EXTERNAL_VIEW.critiques,
        "misunderstandings": DEFAULT_EXTERNAL_VIEW.misunderstandings,
        "needs_explanation": DEFAULT_EXTERNAL_VIEW.needs_explanation,
    }
