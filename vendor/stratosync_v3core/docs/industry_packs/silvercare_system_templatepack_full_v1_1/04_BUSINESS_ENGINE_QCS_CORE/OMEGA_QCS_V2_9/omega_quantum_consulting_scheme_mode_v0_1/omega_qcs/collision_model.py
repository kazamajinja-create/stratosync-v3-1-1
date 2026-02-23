from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Tuple

from .scoring_utils import normalize_to_unit, weighted_sum
from .config import DEFAULT_SCALES, DEFAULT_THRESHOLDS

@dataclass
class CollisionOutputs:
    collision_intensity: float
    collision_band: str
    structural_resilience: str
    amplification_index: float
    explainability: Dict[str, Any]

def compute_collision_intensity(internal_scores: Dict[str, float], market_sensitivity: Dict[str, float]) -> Tuple[float, Dict[str, float]]:
    total, contrib = weighted_sum(internal_scores, market_sensitivity, default_w=0.5)
    return total, contrib

def compute_structural_resilience(hssi: float, market_volatility: float, thresholds=DEFAULT_THRESHOLDS) -> Tuple[str, float]:
    mv = max(1e-9, float(market_volatility))
    ratio = float(hssi) / mv
    if ratio > thresholds.resilience_high:
        return "耐性高", ratio
    elif ratio > thresholds.resilience_mid:
        return "要注意", ratio
    else:
        return "脆弱", ratio

def compute_amplification_index(hssi: float, growth_momentum: float) -> float:
    return float(hssi) * float(growth_momentum)

def band_collision(ci: float, thresholds=DEFAULT_THRESHOLDS) -> str:
    if ci > thresholds.collision_lvl1:
        return "衝突優先度レベル1"
    elif ci > thresholds.collision_lvl2:
        return "衝突優先度レベル2"
    else:
        return "衝突優先度レベル3"

def run_collision_suite(
    internal_scores: Dict[str, float],
    hssi: float,
    market_volatility: float,
    growth_momentum: float,
    sensitivity_map: Dict[str, float],
    thresholds=DEFAULT_THRESHOLDS,
    scales=DEFAULT_SCALES
) -> CollisionOutputs:
    # Normalize for internal reasoning (non-public)
    unit_internal = {k: normalize_to_unit(v, scales.internal_min, scales.internal_max) for k, v in internal_scores.items()}
    # keep original values for explainability
    ci_raw, contrib_raw = compute_collision_intensity(internal_scores, sensitivity_map)
    ci_unit, contrib_unit = compute_collision_intensity(unit_internal, sensitivity_map)

    sr_label, sr_ratio = compute_structural_resilience(hssi, market_volatility, thresholds=thresholds)
    ai = compute_amplification_index(hssi, growth_momentum)
    band = band_collision(ci_raw, thresholds=thresholds)

    explain = {
        "inputs": {
            "hssi": hssi,
            "market_volatility": market_volatility,
            "growth_momentum": growth_momentum,
        },
        "collision": {
            "ci_raw": ci_raw,
            "ci_unit": ci_unit,
            "top_contributors_raw": sorted(contrib_raw.items(), key=lambda kv: kv[1], reverse=True)[:5],
            "top_contributors_unit": sorted(contrib_unit.items(), key=lambda kv: kv[1], reverse=True)[:5],
            "sensitivity_map": sensitivity_map,
        },
        "resilience": {
            "ratio": sr_ratio,
            "thresholds": thresholds.__dict__,
        },
        "notes": [
            "本出力は予測保証ではなく、外部環境と内部構造の『衝突強度/増幅/耐性』を整理するものです。",
            "投資助言・会計判断・税務判断・監査意見・法的助言を構成しません。",
        ],
    }
    return CollisionOutputs(ci_raw, band, sr_label, ai, explain)
