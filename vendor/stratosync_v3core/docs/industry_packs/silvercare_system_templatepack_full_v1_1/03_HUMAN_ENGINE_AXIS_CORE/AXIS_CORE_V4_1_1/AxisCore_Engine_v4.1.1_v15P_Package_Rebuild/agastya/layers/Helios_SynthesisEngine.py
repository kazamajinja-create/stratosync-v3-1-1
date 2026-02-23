# agastya/layers/Helios_SynthesisEngine.py
# -*- coding: utf-8 -*-
"""
Helios Synthesis Engine
- Gamma解析 + Epsilon因果 + （任意）量子メタ を統合し要約と行動指針を出力
"""
from __future__ import annotations
from typing import Dict, Any, List

def synthesize(gamma: Dict[str,Any], epsilon: Dict[str,Any], quantum: Dict[str,Any]) -> Dict[str,Any]:
    hints = []
    if gamma.get("polarity") == "caution":
        hints.append("慎重に意思決定を進める")
    if gamma.get("tense") == "future":
        hints.append("期日・準備の前倒しを検討")
    if gamma.get("theme") in ("転機","移動"):
        hints.append("小さな実験から環境を変える")

    conf = quantum.get("confidence")
    if conf is not None:
        if conf < 0.65:
            hints.append("不確実性が高い領域は段階的に検証")
        elif conf > 0.85:
            hints.append("今期は加速判断も可")

    summary = f"主要テーマ: {gamma.get('theme')}／時制: {gamma.get('tense')}／極性: {gamma.get('polarity')}"
    return {
        "ok": True,
        "summary": summary,
        "recommendations": hints[:3],
        "graph": epsilon
    }
