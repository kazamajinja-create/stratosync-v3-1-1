from __future__ import annotations

def likert_1_5_to_0_100(x: int) -> float:
    """Map Likert 1..5 to 0..100 linearly."""
    if x < 1: x = 1
    if x > 5: x = 5
    return (x - 1) / 4.0 * 100.0

def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))

def avg(values: list[float]) -> float:
    return sum(values) / max(len(values), 1)
