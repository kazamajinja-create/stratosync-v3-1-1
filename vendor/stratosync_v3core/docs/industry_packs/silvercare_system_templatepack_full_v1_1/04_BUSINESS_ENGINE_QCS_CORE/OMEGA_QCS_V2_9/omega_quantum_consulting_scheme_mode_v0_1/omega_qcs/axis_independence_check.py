from __future__ import annotations
from typing import Dict, Literal, List

Readiness = Literal["READY","BORDER","NOT_READY"]

def evaluate_independence(session_events: List[Dict] | None) -> Dict:
    """
    Heuristic readiness check based on session notes.
    This is NOT a certification. It is an internal indicator.
    """
    text = " ".join((e.get("note","") for e in (session_events or [])))
    # signals
    asks_answer = any(k in text for k in ["答えをください","決めてください","正解を教えて"])
    tolerates_no_answer = any(k in text for k in ["結論を出さない","構造だけ見る","検討観点","説明責任"])
    handles_cases = any(k in text for k in ["ケース","A/B","副作用","短期","中期","論点"])
    if asks_answer and not tolerates_no_answer:
        r: Readiness = "NOT_READY"
    elif tolerates_no_answer and handles_cases and not asks_answer:
        r = "READY"
    else:
        r = "BORDER"
    return {
        "AXIS_READINESS": r,
        "notes": [
            "本指標は認定・資格ではなく、運用上の内部評価のための目安。",
            "『推奨/結論提示』ではなく『検討観点/構造整理』を維持できているかを重視。",
        ]
    }
