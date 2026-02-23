from __future__ import annotations
"""
Agastya adapters for ΩQCS (business edition)

Policy adaptations:
- No "recommendations" (convert to "considerations")
- No outcome guarantees
- Deterministic meta (seed/chapter) used only as *structure* prompts
"""
from hashlib import sha256
from typing import Dict, Any, List
from .language_business import business_tone

def _h(seed: str, chapter: int, salt: str) -> str:
    return sha256(f"{seed}:{chapter}:{salt}".encode("utf-8")).hexdigest()

def quantum_observe(seed: str, chapter: int) -> Dict[str, Any]:
    h = _h(seed, chapter, "agastya")
    amp = (int(h[2:6], 16) % 1000) / 1000.0
    angle = (int(h[6:10], 16) % 3600) / 10.0
    conf = 0.6 + 0.35*(int(h[10:12], 16)/255.0)
    inter = (int(h[12:16], 16) % 100)/100.0
    return {
        "confidence": round(conf, 2),
        "amplitude": round(amp, 3),
        "angle_deg": angle,
        "interference": round(inter, 2),
        "notes": ["agastya quantum layer (deterministic meta)"]
    }

def gamma_language_observe(text: str, seed: str, chapter: int) -> Dict[str, Any]:
    h = _h(seed, chapter, text)
    polarity = ["positive", "neutral", "caution"][int(h[:2], 16) % 3]
    tense = ["past","present","future"][int(h[2:4], 16) % 3]
    themes = ["関係性","事業","健康","資金","学習","転機","移動"]
    theme = themes[int(h[4:6], 16) % len(themes)]
    symbols = ["鍵","門","舟","鳥","塔","道","星","太陽","月","輪"]
    syms = [symbols[int(h[i:i+2], 16) % len(symbols)] for i in range(6, 18, 2)]
    return {"ok": True, "polarity": polarity, "tense": tense, "theme": theme, "symbols": syms}

def epsilon_causality(events: List[str], seed: str, chapter: int) -> Dict[str, Any]:
    base = _h(seed, chapter, "causal")
    nodes = [{"id": f"e{i}", "label": e} for i, e in enumerate(events)]
    edges = []
    for i in range(max(0, len(events)-1)):
        w = (int(base[2*i:2*i+2], 16) % 60 + 40)/100.0  # 0.4-0.99
        edges.append({"from": f"e{i}", "to": f"e{i+1}", "weight": round(min(0.99,w),2)})
    return {"ok": True, "nodes": nodes, "edges": edges}

def helios_synthesize(gamma: Dict[str,Any], epsilon: Dict[str,Any], quantum: Dict[str,Any]) -> Dict[str,Any]:
    considerations = []
    if gamma.get("polarity") == "caution":
        considerations.append("意思決定プロセス上、慎重さが求められる可能性があります")
    if gamma.get("tense") == "future":
        considerations.append("期日・準備の前倒しを論点として整理できます")
    if gamma.get("theme") in ("転機","移動"):
        considerations.append("小さな検証から環境条件を調整する選択肢があります")

    conf = quantum.get("confidence")
    if conf is not None:
        if conf < 0.65:
            considerations.append("不確実性が高い領域は段階的に検証する余地があります")
        elif conf > 0.85:
            considerations.append("条件が整う場合は意思決定を前倒しする余地があります")

    summary = f"主要テーマ: {gamma.get('theme')}／時間軸: {gamma.get('tense')}／リスク感度: {gamma.get('polarity')}"
    summary = business_tone(summary)

    return {
        "ok": True,
        "summary": summary,
        "considerations": [business_tone(x) for x in considerations[:3]],
        "graph": epsilon
    }
