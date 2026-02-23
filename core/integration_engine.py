from __future__ import annotations
from dataclasses import dataclass
from .normalizer import clamp

@dataclass
class IntegrationResult:
    surface_power: float   # 0..100
    resilience: float      # 0..100

def compute_surface_power(SE: float, SI: float) -> float:
    return clamp(0.60*SE + 0.40*SI, 0.0, 100.0)

def compute_resilience(adjusted_risk: float, omega_index: float, PM: float) -> float:
    """Resilience = 0.35*(100-AdjustedRisk) + 0.35*Ω + 0.30*PM"""
    return clamp(0.35*(100.0-adjusted_risk) + 0.35*omega_index + 0.30*PM, 0.0, 100.0)
