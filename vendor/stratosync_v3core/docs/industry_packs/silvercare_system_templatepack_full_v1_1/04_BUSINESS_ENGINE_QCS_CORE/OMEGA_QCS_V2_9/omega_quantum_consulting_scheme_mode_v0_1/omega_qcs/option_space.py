from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class OptionItem:
    category: str           # Visible / Hidden / Forbidden / Meta
    option: str             # option label
    rationale: str          # why this option exists (structural basis)
    observer: str           # which observer lens surfaced it (CEO / Finance / Ops / Customer / Reputation)

def _add(items: List[OptionItem], category: str, option: str, rationale: str, observer: str) -> None:
    items.append(OptionItem(category=category, option=option, rationale=rationale, observer=observer))

def expand_option_space(
    structure: Dict[str, str],
    indices: Dict[str, str],
    uncertainty: Optional[Dict[str, str]] = None,
    constraints: Optional[Dict[str, str]] = None,
    known_options: Optional[List[str]] = None
) -> Dict[str, List[Dict[str, str]]]:
    """Expand option space from a multi-observer perspective.

    This function does NOT recommend, rank, or decide.
    It only enumerates plausible options that structurally exist but may be unspoken.
    """
    uncertainty = uncertainty or {}
    constraints = constraints or {}
    known_options = known_options or []

    items: List[OptionItem] = []

    # 1) Visible options: pass-through
    for opt in known_options:
        _add(items, "Visible", opt, "入力で明示された選択肢", "CEO")

    sc = indices.get("構造集中指数")
    cr = indices.get("コスト硬直指数")
    vol = indices.get("変動性指数")
    cf = indices.get("資金流動指数")

    # 2) Hidden options: structurally available but not spoken
    if sc == "集中":
        _add(items, "Hidden", "依存点の分散（顧客/商品/チャネル/担当の分離）", "構造集中=集中 → 単一依存は分岐点になりやすい", "Finance")
        _add(items, "Hidden", "集中対象の再定義（『何に集中しているか』を意識化する）", "集中対象を明確化しないと説明責任が上がるため", "Reputation")
    if cr == "固定費高":
        _add(items, "Hidden", "固定費の変動化（外注/成果連動/段階投資）", "コスト硬直=固定費高 → 損益振幅の管理論点が前面化", "Finance")
        _add(items, "Hidden", "規模の調整（縮小/再配置/機能分離）", "固定費は規模と密接に連動しやすい", "Ops")
    if vol == "高":
        _add(items, "Hidden", "シナリオ前提運用（複数ケースを並列で保持）", "変動性=高 → 単一計画が破綻しやすい", "CEO")
        _add(items, "Hidden", "検証・実験（小さく試す）", "予測幅が広いときは実験が情報を増やす", "Ops")

    # 3) Forbidden options: psychologically/organizationally blocked
    # We can't know personal blocks; we infer likely 'taboo' categories from structure.
    if sc == "集中":
        _add(items, "Forbidden", "『断る/切る/やめる』の検討（集中対象の整理）", "集中構造では、関係性の整理がタブー化しやすい", "CEO")
    if cr == "固定費高":
        _add(items, "Forbidden", "価格改定/契約条件変更の検討", "固定費構造では単価議論が避けられがち", "Finance")
    if vol == "高":
        _add(items, "Forbidden", "情報公開範囲の再設計（外部説明の粒度調整）", "変動が大きいと説明責任が重くなり、開示が恐怖になりやすい", "Reputation")

    # 4) Meta options: decision-form changes (time/sequence/partition)
    _add(items, "Meta", "期限設定（決める期限を固定する）", "意思決定摩擦の低減のための形式選択", "CEO")
    _add(items, "Meta", "分割意思決定（論点を分けて順に決める）", "論点が絡むほど、分割が有効になりやすい", "Ops")
    if uncertainty:
        _add(items, "Meta", "保留という選択（不確定性を明示した上で待つ）", "不確定性が高い領域は『待つ』が合理的になる場合がある", "CEO")
        _add(items, "Meta", "観測点切替（CEO/Finance/Ops/Customer/Reputationで再読解）", "多観測により未認識の選択肢が出現しやすい", "Customer")

    # Output grouped by category
    out: Dict[str, List[Dict[str, str]]] = {"Visible": [], "Hidden": [], "Forbidden": [], "Meta": []}
    for it in items:
        out[it.category].append({
            "option": it.option,
            "rationale": it.rationale,
            "observer": it.observer
        })
    return out
