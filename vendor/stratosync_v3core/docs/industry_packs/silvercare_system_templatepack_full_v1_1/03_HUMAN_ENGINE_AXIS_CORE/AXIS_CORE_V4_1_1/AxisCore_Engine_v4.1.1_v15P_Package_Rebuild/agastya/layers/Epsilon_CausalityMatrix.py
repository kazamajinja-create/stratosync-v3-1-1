# agastya/layers/Epsilon_CausalityMatrix.py
# -*- coding: utf-8 -*-
"""
Epsilon Causality Matrix
- 霊視文の因果パターンを簡易グラフに投影
- ノード: event_i, エッジ: cause->effect（重みは疑似確率）
"""
from __future__ import annotations
from hashlib import sha256
from typing import Dict, Any, List

def infer(events: List[str], seed: str, chapter: int) -> Dict[str, Any]:
    base = sha256(f"{seed}:{chapter}:causal".encode("utf-8")).hexdigest()
    nodes = [{"id": f"e{i}", "label": e} for i, e in enumerate(events)]
    edges = []
    for i in range(len(events)-1):
        w = (int(base[2*i:2*i+2], 16) % 60 + 40)/100.0  # 0.4-0.99
        edges.append({"from": f"e{i}", "to": f"e{i+1}", "weight": round(min(0.99,w),2)})
    return {"ok": True, "nodes": nodes, "edges": edges}
