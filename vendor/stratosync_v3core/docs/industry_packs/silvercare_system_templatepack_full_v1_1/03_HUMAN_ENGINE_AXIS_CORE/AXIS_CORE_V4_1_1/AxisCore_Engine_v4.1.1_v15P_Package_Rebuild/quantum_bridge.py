# -*- coding: utf-8 -*-
"""Senjyu Nexus QuantumBridge v1
Bridges Senjyu Core (A–H fields) with Nexus v1.2 (I/J + CIM + Ethics).
- Exposes a simple API for Core to evaluate interference and apply junction damping.
- Provides thin wrappers to keep Core loosely coupled.
"""
from typing import List, Dict
from math import pi

try:
    # Prefer local Nexus v1.2
    from quantum.cim import ObserverWave, evaluate_cim, EthicsParams, ethics_cost
except Exception as e:
    raise ImportError("Nexus v1.2 not found (quantum.cim). Install Senjyu_Nexus_v1.2_AutoRelease_Kit first.") from e

# Defaults
DEFAULT_KAPPA = 0.25
DEFAULT_WIJ = 1.0

class QuantumBridge:
    def __init__(self, kappa: float = DEFAULT_KAPPA, base_weight: float = DEFAULT_WIJ):
        self.kappa = kappa
        self.base_weight = base_weight

    def eval_interference(self, waves: List[Dict]) -> Dict:
        """waves: [{"A": float, "phi": float (radians)}]"""
        ow = [ObserverWave(A=w.get("A", 1.0), phi=w.get("phi", 0.0)) for w in waves]
        return evaluate_cim(ow, w_ij=self.base_weight, kappa=self.kappa)

    def ethics_score(self, tau: float = 0.8, nu: float = 0.8, alpha: float = 0.8,
                     w_tau: float = 1.0, w_nu: float = 1.0, w_alpha: float = 1.0) -> Dict:
        p = EthicsParams(tau=tau, nu=nu, alpha=alpha, w_tau=w_tau, w_nu=w_nu, w_alpha=w_alpha)
        return {"params": p.__dict__, "cost": ethics_cost(p)}

# Convenience mapping from Senjyu Core observer state to wave parameters.
def core_state_to_wave(state: Dict) -> Dict:
    """Map Senjyu Core observer state -> {A, phi} for CIM.
    Expected keys in state:
      - "intensity" -> amplitude A >= 0
      - "phase" -> phase in radians (if degrees, send "phase_deg": float)
    """
    A = float(state.get("intensity", 1.0))
    if "phase" in state:
        phi = float(state["phase"])
    else:
        # convert from degrees if provided
        phi = float(state.get("phase_deg", 0.0)) * (3.141592653589793/180.0)
    return {"A": max(A, 0.0), "phi": phi}
