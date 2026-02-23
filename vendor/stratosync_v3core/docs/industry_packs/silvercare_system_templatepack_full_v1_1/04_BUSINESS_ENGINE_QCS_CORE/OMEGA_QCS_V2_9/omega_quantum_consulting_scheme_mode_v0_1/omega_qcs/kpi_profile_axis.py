from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class KPIProfile:
    name: str
    recommended: List[str]
    excluded: List[str]
    notes: List[str]

AXIS_INDEPENDENCE_KPI = KPIProfile(
    name="AXIS育成（自立ゴール）KPI",
    recommended=[
        "卒業率（100%を要求しない）",
        "判断代行依存ゼロ（『答えをください』が最終月に出ない）",
        "卒業後の非契約的接点（紹介/協業/再相談が自然発生）",
        "BPコミュニティへの逆依存が発生していない（依存的継続を作っていない）",
    ],
    excluded=[
        "継続率（囲い込み誘因になるため）",
        "満足度スコア（結果保証/感情評価に偏るため）",
        "売上最大化（短期利益最適化で思想が壊れやすいため）",
        "成功事例の誇張（拡散/炎上を招きやすいため）",
    ],
    notes=[
        "本プログラムは『続ける関係』ではなく『決断して終わる関係』を前提とする。",
        "KPIは『自立の成立』を確認するために用いる。成果保証の根拠として用いない。",
    ]
)

def as_dict(p: KPIProfile) -> Dict:
    return {"name": p.name, "recommended": p.recommended, "excluded": p.excluded, "notes": p.notes}
