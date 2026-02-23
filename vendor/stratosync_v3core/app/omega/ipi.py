from __future__ import annotations

import math
from dataclasses import dataclass


def _clamp01(x: float) -> float:
    try:
        x = float(x)
    except Exception:
        x = 0.0
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x


def _norm100(x: float, scale: float = 5.0) -> float:
    """Normalize entropy-like values to 0..100.

    Typical ln(Ω) for SMEs is a small number; default scale=5.0.
    Industry packs may tune this.
    """
    try:
        x = float(x)
    except Exception:
        x = 0.0
    if scale <= 0:
        scale = 5.0
    v = (x / scale) * 100.0
    if v < 0:
        return 0.0
    if v > 100:
        return 100.0
    return v


@dataclass
class IPIParams:
    """Industry-tunable parameters for Innovation Potential Index."""

    scale: float = 5.0
    w_connections: float = 1.0
    w_cross_roles: float = 1.0
    w_info_flow: float = 1.0
    w_flex: float = 1.0


def calculate_ipi(
    *,
    connections: float,
    cross_roles: float,
    info_flow: float,
    flexibility: float,
    params: IPIParams | None = None,
) -> dict:
    """Innovation Potential Index (IPI) based on combinatorial entropy.

    Ω ≈ connections × cross_roles × info_flow × flexibility
    IPI ∝ ln(Ω)

    Inputs are expected to be non-negative. info_flow/flexibility can be given
    as 0..1; other inputs are counts/ratios.
    """

    p = params or IPIParams()
    c = max(0.0, float(connections)) * p.w_connections
    x = max(0.0, float(cross_roles)) * p.w_cross_roles
    f = max(0.0, float(info_flow)) * p.w_info_flow
    g = max(0.0, float(flexibility)) * p.w_flex

    omega = max(1e-9, c * x * max(1e-6, f) * max(1e-6, g))
    entropy = math.log(omega)
    innovation_index = _norm100(entropy, scale=p.scale)

    # Silo & rigidity heuristics (0..1)
    silo_index = _clamp01(1.0 - _clamp01(f))
    rigidity = _clamp01(1.0 - _clamp01(g))
    if rigidity < 0.33:
        rigidity_level = "low"
    elif rigidity < 0.66:
        rigidity_level = "moderate"
    else:
        rigidity_level = "high"

    return {
        "innovation_index": round(innovation_index, 2),
        "omega_estimate": round(omega, 6),
        "entropy_ln_omega": round(entropy, 6),
        "silo_index": round(silo_index, 3),
        "rigidity_level": rigidity_level,
    }
