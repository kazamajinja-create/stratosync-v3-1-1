from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class ExecutionCapacity:
    execution_difficulty: str      # low/medium/high (descriptive)
    bottlenecks: List[str]
    feasible_90d_scope: List[str]
    notes: List[str]

def assess_execution_capacity(
    structure: Dict[str, str],
    indices: Dict[str, str],
    constraints: Optional[Dict[str, str]] = None
) -> ExecutionCapacity:
    constraints = constraints or {}
    bottlenecks: List[str] = []
    feasible: List[str] = []

    dep = structure.get("dependency", "")
    decision = structure.get("decision_structure", "")
    sc = indices.get("構造集中指数")
    vol = indices.get("変動性指数")

    if "属人" in dep or sc == "集中":
        bottlenecks.append("意思決定・実行が特定人物/要因に集中しやすい")
        feasible.append("集中点の可視化と分離（役割/権限/運用）")
    if "遅い" in decision or "合意" in decision:
        bottlenecks.append("合意形成コストが高く、実行に遅延が出やすい")
        feasible.append("論点分割と期限設定（Meta意思決定）")
    if vol == "高":
        feasible.append("実験・検証（小さく試す）で情報を増やす")
        bottlenecks.append("変動が大きいと計画が単線化しづらい")

    if len(bottlenecks) >= 3:
        difficulty = "high"
    elif len(bottlenecks) == 2:
        difficulty = "medium"
    else:
        difficulty = "low"

    notes = [
        "本出力は実行可能性を『構造として』記述するもので、優劣評価ではありません。",
        "90日スコープは『実装可能範囲の候補』であり、推奨ではありません。",
    ]
    return ExecutionCapacity(difficulty, bottlenecks, feasible, notes)
