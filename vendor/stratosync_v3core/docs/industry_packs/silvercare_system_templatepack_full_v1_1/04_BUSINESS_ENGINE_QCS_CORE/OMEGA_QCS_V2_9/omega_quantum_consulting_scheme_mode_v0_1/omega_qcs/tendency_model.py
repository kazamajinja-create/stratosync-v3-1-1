from __future__ import annotations
from typing import Dict, List

def build_tendency_model(indices: Dict[str, str]) -> Dict[str, List[str]]:
    """Build tendency-based scenario space (not decisions)."""
    short_term: List[str] = []
    medium_term: List[str] = []
    side_effects: List[str] = []
    explainability: List[str] = []

    sc = indices.get("構造集中指数")
    if sc == "集中":
        short_term.append("特定要因（顧客・商品・人物・チャネル等）の変化により短期変動が起こりやすい")
        medium_term.append("集中対象が強化されれば伸び、毀損されれば鈍化する『分岐』が生まれやすい")
        side_effects.append("集中対象の説明責任（なぜそれに依存するか）が外部論点になりやすい")
        explainability.append("根拠: 構造集中指数=集中")
    elif sc == "分散":
        short_term.append("短期変動は緩和されやすい（単一要因に引きずられにくい）")
        medium_term.append("中期の伸びは『複数要因の同時成立』に依存しやすい")
        side_effects.append("分散の裏側で意思決定が遅くなる（論点が増える）可能性")
        explainability.append("根拠: 構造集中指数=分散")

    cr = indices.get("コスト硬直指数")
    if cr == "固定費高":
        short_term.append("売上変動時の損益振幅が大きくなりやすい（固定費構造のため）")
        medium_term.append("中期での選択肢（縮小/維持/投資）が、キャッシュ配分論点として前面化しやすい")
        side_effects.append("コスト構造の説明が『守り』に寄ると、成長の語りが弱く見える可能性")
        explainability.append("根拠: コスト硬直指数=固定費高")
    elif cr == "変動費中心":
        short_term.append("売上変動に対して損益が追随しやすい（変動費中心）")
        medium_term.append("中期では供給能力・品質維持の制約が主要論点になりやすい")
        side_effects.append("変動費最適化が過剰になると、品質・信頼が摩耗する可能性")
        explainability.append("根拠: コスト硬直指数=変動費中心")

    vol = indices.get("変動性指数")
    if vol == "高":
        short_term.append("四半期・月次でのぶれが大きく見えやすい")
        medium_term.append("中期の予測幅が広がりやすく、複数シナリオ前提の運営が合理的になりやすい")
        side_effects.append("外部説明で『一貫性がない』と誤解されるリスク（説明責任が上がる）")
        explainability.append("根拠: 変動性指数=高")
    elif vol == "低":
        short_term.append("短期の変動は限定的に見えやすい")
        medium_term.append("中期の課題は変動よりも、成長の源泉（新規/更新/拡張）の設計に寄りやすい")
        side_effects.append("安定の惰性により、意思決定の遅れが起こりやすい")
        explainability.append("根拠: 変動性指数=低")

    cf = indices.get("資金流動指数")
    if cf:
        explainability.append(f"参照: 資金流動指数={cf}（符号パターンのスナップショット）")

    note = [
        "本出力は『傾向モデル（予測モデル）』であり、将来を断定するものではありません。",
        "本モデルは意思決定の代行を行わず、推奨・最適解を提示しません。",
    ]

    return {
        "short_term": short_term,
        "medium_term": medium_term,
        "side_effects": side_effects,
        "explainability": explainability,
        "note": note,
    }
