from __future__ import annotations

from dataclasses import dataclass
from math import comb, log
from typing import Dict, Any, Optional


@dataclass
class SurfaceInputs:
    # Boundary / surface drivers
    customer_touchpoints: float = 0.0  # C
    brand_exposure: float = 0.0        # B
    partner_links: float = 0.0         # P
    api_connections: float = 0.0       # I
    data_contact_freq: float = 0.0     # D
    # Internal volume proxy
    internal_volume: float = 1.0       # V (avoid div by zero)


def compute_surface(si: SurfaceInputs, weights: Optional[Dict[str, float]] = None) -> Dict[str, float]:
    """Compute Ω-Surface metrics.

    A = w1*C + w2*B + w3*P + w4*I + w5*D
    SE = A / V
    """
    w = {
        "C": 1.0,
        "B": 1.0,
        "P": 1.0,
        "I": 1.0,
        "D": 1.0,
    }
    if weights:
        w.update({k: float(v) for k, v in weights.items() if k in w})

    A = (
        w["C"] * float(si.customer_touchpoints) +
        w["B"] * float(si.brand_exposure) +
        w["P"] * float(si.partner_links) +
        w["I"] * float(si.api_connections) +
        w["D"] * float(si.data_contact_freq)
    )
    V = max(float(si.internal_volume), 1e-9)
    SE = A / V
    return {
        "A_surface": round(A, 6),
        "V_volume": round(V, 6),
        "SE_surface_efficiency": round(SE, 6),
        "weights": {k: round(v, 6) for k, v in w.items()},
    }


def compute_omega(n_effective: int) -> Dict[str, float]:
    """Compute combination explosion metrics.

    Omega = C(n,2) (pairwise collaboration potential)
    OPI = ln(Omega) (entropy-like proxy), 0 if Omega<=1
    """
    n = max(int(n_effective), 0)
    Omega = comb(n, 2) if n >= 2 else 0
    OPI = log(Omega) if Omega and Omega > 1 else 0.0
    return {
        "n_effective": n,
        "Omega_pairs": float(Omega),
        "OPI_logOmega": round(float(OPI), 6),
    }


def compute_mode_indices(BI: float, HI: float, OI: float, SE: float, OPI: float,
                         lambdas: Optional[Dict[str, float]] = None) -> Dict[str, float]:
    """Compute final SOS score from normalized indices in [0,1] (recommended)."""
    lam = {
        "BI": 0.30,
        "HI": 0.20,
        "OI": 0.20,
        "SE": 0.15,
        "OPI": 0.15,
    }
    if lambdas:
        lam.update({k: float(v) for k, v in lambdas.items() if k in lam})

    SOS = (
        lam["BI"] * BI +
        lam["HI"] * HI +
        lam["OI"] * OI +
        lam["SE"] * SE +
        lam["OPI"] * OPI
    )
    return {
        "BI": round(float(BI), 6),
        "HI": round(float(HI), 6),
        "OI": round(float(OI), 6),
        "SE": round(float(SE), 6),
        "OPI": round(float(OPI), 6),
        "SOS": round(float(SOS), 6),
        "lambdas": {k: round(v, 6) for k, v in lam.items()},
    }


def clamp01(x: float) -> float:
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else float(x)


def normalize_positive(x: float, scale: float) -> float:
    """Simple positive normalization: x/(x+scale)"""
    x = max(float(x), 0.0)
    s = max(float(scale), 1e-9)
    return x / (x + s)


def derive_demo_priors(payload: Dict[str, Any]) -> Dict[str, float]:
    """Derive rough priors for P,C,E,eta from minimal demo inputs.

    This keeps the demo 1-page UI minimal while producing stable scores.
    Users can override by supplying explicit P/C/E/eta in payload.
    """
    rev = payload.get("revenue_jpy")
    emp = payload.get("employees")
    challenges = (payload.get("challenges") or "")
    # Revenue per employee normalization (scale=10M JPY)
    rpe = None
    if rev is not None and emp:
        try:
            rpe = float(rev) / max(float(emp), 1.0)
        except Exception:
            rpe = None
    rpe_norm = normalize_positive(rpe or 0.0, 10_000_000.0)

    # Text-based stress proxy: longer "challenges" may indicate more friction
    stress = min(len(challenges) / 400.0, 1.0)  # 0..1

    # Priors: keep in moderate range to avoid extreme outputs in demos
    P = clamp01(0.45 + 0.35 * rpe_norm)               # profitability proxy
    E = clamp01(0.50 + 0.20 * rpe_norm - 0.15 * stress) # execution proxy
    C = clamp01(0.55 - 0.20 * stress)                 # cohesion proxy
    eta = clamp01(0.55 - 0.10 * stress + 0.10 * rpe_norm) # resilience proxy

    return {"P": round(P, 4), "C": round(C, 4), "E": round(E, 4), "eta": round(eta, 4)}
