from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Tuple, Optional
import math

# Internal 12 vars expected keys
VARS_12 = ["S","K","D","B","R","T","E","H","P","M","X","G"]

@dataclass
class InjectorParams:
    # global max amplification width (lambda)
    lam: float = 0.6
    # shock gate parameters for strategy B
    shock_tau: float = 0.65
    shock_k: float = 8.0
    # relative velocity blending (strategy C)
    eta_velocity: float = 0.5

def _clip(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, float(x)))

def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))

def normalize_internal(scores_0_100: Dict[str, float]) -> Dict[str, float]:
    """Normalize 0-100 to 0-1 for internal computation."""
    z = {}
    for k in VARS_12:
        if k in scores_0_100:
            z[k] = _clip(scores_0_100[k] / 100.0)
    return z

def normalize_external(M: float, C: float, R_ext: float, scale: float = 4.0) -> Tuple[float, float, float]:
    """Normalize 0-4 (or same scale) to 0-1."""
    return (_clip(M / scale), _clip(C / scale), _clip(R_ext / scale))

def apply_external_factors(
    internal_0_100: Dict[str, float],
    M: float,
    C: float,
    R_ext: float,
    sensitivity_matrix: Dict[str, Dict[str, float]],
    strategy: str = "A",
    params: Optional[InjectorParams] = None,
    # optional competitor velocity proxy (0-1), used in strategy C
    competitor_velocity: float = 0.0,
) -> Tuple[Dict[str, float], Dict[str, Any]]:
    """
    Applies external factors (M, C, R_ext) to 12 variables using one of three strategies.
    Returns: (adjusted_internal_0_100, explainability)
    - sensitivity_matrix: {var: {"M": alpha, "C": beta, "R": gamma, "delta": optional}} weights in 0..1
    """
    params = params or InjectorParams()
    z = normalize_internal(internal_0_100)
    m, c, r = normalize_external(M, C, R_ext)

    strategy = (strategy or "A").upper()

    # Shock gate for strategy B
    g = _sigmoid(params.shock_k * (r - params.shock_tau)) if strategy == "B" else None

    # Relative velocity for strategy C
    c_velocity = _clip(competitor_velocity)
    c_eff = _clip(c + params.eta_velocity * c_velocity) if strategy == "C" else c

    out = {}
    impacts = {}
    for var, z_i in z.items():
        w = sensitivity_matrix.get(var, {})
        alpha = float(w.get("M", 0.5))
        beta  = float(w.get("C", 0.5))
        gamma = float(w.get("R", 0.5))

        if strategy == "A":
            p_i = alpha*m + beta*c_eff + gamma*r
        elif strategy == "B":
            p_base = alpha*m + beta*c_eff
            p_shock = gamma*r
            p_i = (1.0 - g) * p_base + g * p_shock
        elif strategy == "C":
            p_i = alpha*m + beta*c_eff + gamma*r
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

        # Core multiplicative adjustment around neutral 0.5
        mult = 1.0 + params.lam * (p_i - 0.5)
        z_prime = _clip(z_i * mult)

        # Relative advantage penalty (strategy C)
        penalty = 0.0
        if strategy == "C":
            delta = float(w.get("delta", 0.0))  # 0..0.2 typical
            penalty = delta * c_velocity
            z_prime = _clip(z_prime - penalty)

        out[var] = z_prime * 100.0
        impacts[var] = {
            "z": z_i,
            "m": m, "c": c, "c_eff": c_eff, "r": r,
            "alpha": alpha, "beta": beta, "gamma": gamma,
            "p_i": p_i,
            "mult": mult,
            "penalty": penalty,
            "z_prime": z_prime,
            "delta_0_100": (z_prime - z_i) * 100.0,
        }

    # Keep original keys passed in (if any outside VARS_12)
    adjusted = dict(internal_0_100)
    adjusted.update({k: out[k] for k in out.keys()})

    # Top impacts for explainability
    top = sorted(((k, abs(v["delta_0_100"])) for k, v in impacts.items()), key=lambda kv: kv[1], reverse=True)[:5]

    explain = {
        "strategy": strategy,
        "inputs": {"M": M, "C": C, "R_ext": R_ext, "competitor_velocity": competitor_velocity},
        "normalized": {"m": m, "c": c, "r": r, "c_eff": c_eff, "shock_gate_g": g},
        "params": params.__dict__,
        "top_abs_impacts": top,
        "impacts": impacts,
        "notes": [
            "本処理は予測保証ではなく、外部環境が内部構造に与える『増幅/減衰』係数を整理する内部演算です。",
            "外部出力では三値/五段階評価へ変換し、数値断定を避けます。",
        ],
    }
    return adjusted, explain
