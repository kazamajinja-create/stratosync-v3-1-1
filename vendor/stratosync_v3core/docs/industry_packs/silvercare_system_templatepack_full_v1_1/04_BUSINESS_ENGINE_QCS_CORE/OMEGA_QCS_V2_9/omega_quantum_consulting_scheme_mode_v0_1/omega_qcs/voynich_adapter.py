from __future__ import annotations
"""
Voynich adapters for ΩQCS (business edition)
We treat Voynich logic as "symbolic/semantic prompt matrix" rather than translation truth.
"""
from typing import Dict, Any
import hashlib

def map_term_to_seed(term: str) -> int:
    # stable hash -> 0..1023
    h = hashlib.sha256(term.encode("utf-8")).hexdigest()
    return int(h[:6], 16) % 1024

def symbolic_overlay(theme: str) -> Dict[str, Any]:
    seed = map_term_to_seed(theme or "")
    # Provide a neutral overlay usable as discussion triggers (not claims)
    return {
        "ok": True,
        "seed": seed,
        "policy": "symbolic overlay (non-translation). Used only for framing questions.",
        "prompts": [
            "このテーマで『言いづらいが重要な前提』は何か",
            "『見えている選択肢』の外側に何があるか",
            "説明責任上、どの論点を固定し、どこを保留にするか",
        ]
    }
