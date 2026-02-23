from __future__ import annotations
from dataclasses import dataclass
from .normalizer import clamp

@dataclass
class DecisionAxes:
    RA: float  # Risk Appetite 0..100
    BI: float  # Bias Intensity 0..100
    SV: float  # Stress Volatility 0..100
    SP: float  # Structure Preference 0..100

def compute_daf(ax: DecisionAxes) -> float:
    """DAF_raw = 1.0 + 0.003*(RA-50) + 0.004*(BI-50) + 0.004*(SV-50) - 0.002*(SP-50); clamp 0.70..1.60"""
    daf_raw = (
        1.0
        + 0.003*(ax.RA - 50.0)
        + 0.004*(ax.BI - 50.0)
        + 0.004*(ax.SV - 50.0)
        - 0.002*(ax.SP - 50.0)
    )
    return clamp(daf_raw, 0.70, 1.60)

def compute_adjusted_risk(market_risk_0_100: float, daf: float) -> float:
    return clamp(market_risk_0_100 * daf, 0.0, 100.0)
