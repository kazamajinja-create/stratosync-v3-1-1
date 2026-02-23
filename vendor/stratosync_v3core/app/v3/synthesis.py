from __future__ import annotations

from typing import Any, Dict, Tuple


def _clamp01(x: float) -> float:
    try:
        x = float(x)
    except Exception:
        x = 0.0
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x


def synthesize_v3(
    *,
    evaluate_outputs: Dict[str, Any] | None,
    rcl_outputs: Dict[str, Any] | None,
    sdl_outputs: Dict[str, Any] | None,
    omega_outputs: Dict[str, Any] | None,
) -> Dict[str, Any]:
    """Produce a v3 executive synthesis block.

    Design goals:
    - Explainable.
    - Stable even when some blocks are missing.
    - Produces a single scalar (v3_score) plus a compact roadmap.
    """

    # Internal stability proxy from /evaluate (if available)
    internal = {}
    if isinstance(evaluate_outputs, dict):
        internal = {
            "synchronization_score": evaluate_outputs.get("synchronization_score"),
            "delta_index": evaluate_outputs.get("delta_index"),
            "system_state": evaluate_outputs.get("system_state"),
        }

    # Decision stability proxy from RCL
    decision = {}
    if isinstance(rcl_outputs, dict):
        conv = (rcl_outputs.get("convergence") or {})
        bei = (rcl_outputs.get("branch_explosion") or {})
        decision = {
            "convergence_confidence": conv.get("confidence_score"),
            "branch_explosion_level": bei.get("risk_level"),
            "bei_score": bei.get("bei_score"),
        }

    surface = {}
    if isinstance(sdl_outputs, dict):
        surface = {
            "surface_index": sdl_outputs.get("surface_index"),
            "surface_expansion_potential": sdl_outputs.get("surface_expansion_potential"),
            "volume_surface_ratio": sdl_outputs.get("volume_surface_ratio"),
        }

    omega = {}
    if isinstance(omega_outputs, dict):
        omega = {
            "innovation_index": omega_outputs.get("innovation_index"),
            "silo_index": omega_outputs.get("silo_index"),
            "rigidity_level": omega_outputs.get("rigidity_level"),
        }

    # Compute a single v3 score in 0..100 (conservative).
    # Prefer: internal sync (if present), convergence confidence, surface index, innovation index.
    def _get_num(d: Dict[str, Any], k: str) -> float | None:
        v = d.get(k)
        try:
            if v is None:
                return None
            return float(v)
        except Exception:
            return None

    parts = []
    wsum = 0.0

    s_sync = _get_num(internal, "synchronization_score")
    if s_sync is not None:
        parts.append((s_sync * 100.0, 0.30))
        wsum += 0.30

    conf = _get_num(decision, "convergence_confidence")
    if conf is not None:
        parts.append((conf * 100.0, 0.20))
        wsum += 0.20

    sdi = _get_num(surface, "surface_index")
    if sdi is not None:
        parts.append((sdi, 0.25))
        wsum += 0.25

    ipi = _get_num(omega, "innovation_index")
    if ipi is not None:
        parts.append((ipi, 0.25))
        wsum += 0.25

    if wsum <= 0:
        v3_score = 0.0
    else:
        v3_score = sum(v * w for v, w in parts) / wsum

    # Roadmap hints
    roadmap = []
    headroom = _get_num(surface, "surface_expansion_potential")
    if headroom is not None and headroom >= 0.55:
        roadmap.append("Increase boundary surface: add channels/APIs/partner interfaces; amplify brand touchpoints.")

    silo = _get_num(omega, "silo_index")
    if silo is not None and silo >= 0.5:
        roadmap.append("Reduce silos: increase cross-role collaboration and information flow to raise Ω (combination entropy).")

    # RCL warning
    if (decision.get("branch_explosion_level") in {"high", "critical"}) or (
        (_get_num(decision, "bei_score") or 0) >= 0.7
    ):
        roadmap.append("Stabilize branching: limit simultaneous strategic forks; run staged experiments to improve convergence confidence.")

    if not roadmap:
        roadmap.append("Maintain convergence discipline while expanding surface touchpoints and cross-functional combinations.")

    return {
        "v3_score": round(float(v3_score), 2),
        "internal_stability": internal,
        "decision_stability": decision,
        "surface_power": surface,
        "innovation_potential": omega,
        "roadmap": roadmap[:5],
    }
