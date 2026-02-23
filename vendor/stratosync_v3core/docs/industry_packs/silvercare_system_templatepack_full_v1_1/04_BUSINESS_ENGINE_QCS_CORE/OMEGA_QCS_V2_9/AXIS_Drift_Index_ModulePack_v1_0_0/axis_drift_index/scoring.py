from __future__ import annotations
from typing import Dict, Tuple
from .models import Scores

# --- Fixed scoring spec (saved & synchronized) ---
# Axis blocks:
#   CF = sum(Q1..Q4)
#   MD_raw = sum(Q5..Q8)      -> MD_stability = 20 - MD_raw
#   HS_raw = sum(Q9..Q12)     -> HS_stability = 20 - HS_raw
#   EE_raw = sum(Q13..Q16)    -> EE_stability = 20 - EE_raw
#   AC = sum(Q17..Q20)
# Total (stability score):
#   Total = CF + MD_stability + HS_stability + EE_stability + AC   (0..100)

def _sum_range(q: Dict[str, int], start: int, end: int) -> int:
    return sum(q[f"Q{i}"] for i in range(start, end + 1))

def compute_scores(quant_answers: Dict[str, int]) -> Scores:
    cf = _sum_range(quant_answers, 1, 4)
    md_raw = _sum_range(quant_answers, 5, 8)
    hs_raw = _sum_range(quant_answers, 9, 12)
    ee_raw = _sum_range(quant_answers, 13, 16)
    ac = _sum_range(quant_answers, 17, 20)

    md = 20 - md_raw
    hs = 20 - hs_raw
    ee = 20 - ee_raw

    total = cf + md + hs + ee + ac

    # Defensive clamp (should not be necessary if inputs are valid)
    total = max(0, min(100, total))

    return Scores(
        core_fixity=cf,
        market_dependency_stability=md,
        horizontal_spread_stability=hs,
        energy_erosion_stability=ee,
        axis_coherence=ac,
        total=total,
        market_dependency_raw=md_raw,
        horizontal_spread_raw=hs_raw,
        energy_erosion_raw=ee_raw,
    )
