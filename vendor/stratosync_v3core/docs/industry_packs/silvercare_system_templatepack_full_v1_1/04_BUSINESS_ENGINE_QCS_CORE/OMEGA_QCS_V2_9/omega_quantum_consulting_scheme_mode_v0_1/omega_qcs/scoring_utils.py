from __future__ import annotations
from typing import Dict, Tuple

def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(x)))

def normalize_to_unit(x: float, lo: float, hi: float) -> float:
    if hi == lo:
        return 0.0
    return clamp((x - lo) / (hi - lo), 0.0, 1.0)

def weighted_sum(values: Dict[str, float], weights: Dict[str, float], default_w: float = 0.5) -> Tuple[float, Dict[str, float]]:
    total = 0.0
    contrib = {}
    for k, v in values.items():
        w = float(weights.get(k, default_w))
        c = float(v) * w
        contrib[k] = c
        total += c
    return total, contrib
