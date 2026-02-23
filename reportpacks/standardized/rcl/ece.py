from __future__ import annotations

from typing import Any, Dict, List, Tuple


def _avg(vals: List[float]) -> float:
    return sum(vals) / max(1, len(vals))


def estimate_entropy_from_mode_outputs(mode_outputs: Dict[str, Any]) -> float:
    """Estimate an uncertainty proxy (0..1) from mode_outputs.

    v2.8 does not have full Mode1..7 objects, so we use a conservative heuristic.
    If callers provide an explicit `entropy` in mode_outputs, we respect it.
    """
    if isinstance(mode_outputs, dict) and "entropy" in mode_outputs:
        try:
            e = float(mode_outputs.get("entropy"))
            return 0.0 if e < 0 else 1.0 if e > 1 else e
        except Exception:
            pass
    # Default moderate uncertainty
    return 0.25


def calculate_early_convergence(
    coverage: Dict[str, float],
    mode_outputs: Dict[str, Any] | None = None,
    industry_prior: Dict[str, float] | None = None,
    top_n: int = 3,
) -> Dict[str, Any]:
    """Early Convergence Estimator (ECE).

    Purpose: with partial inputs, provide (a) current confidence, (b) next-best data to
    collect that most rapidly increases confidence.

    Confidence is computed as:
        confidence = avg_coverage * (1 - entropy)

    Where entropy is a heuristic uncertainty proxy.
    """
    mode_outputs = mode_outputs or {}
    entropy = estimate_entropy_from_mode_outputs(mode_outputs)

    # Optionally tilt weights by industry prior (if provided)
    # priors are interpreted as "importance weights" for each coverage key.
    keys = list(coverage.keys())
    if industry_prior:
        weights = [float(industry_prior.get(k, 1.0)) for k in keys]
        wsum = sum(weights) or 1.0
        avg_cov = sum(float(coverage.get(k, 0.0)) * w for k, w in zip(keys, weights)) / wsum
    else:
        avg_cov = _avg([float(coverage.get(k, 0.0)) for k in keys])

    confidence = max(0.0, min(1.0, avg_cov * (1.0 - entropy)))

    # Next best questions: lowest coverage items first, with prior weighting if present
    scored: List[Tuple[str, float]] = []
    for k in keys:
        cov = float(coverage.get(k, 0.0))
        imp = float((industry_prior or {}).get(k, 1.0))
        # lower coverage + higher importance => higher priority
        priority = (1.0 - cov) * imp
        scored.append((k, priority))

    scored.sort(key=lambda x: x[1], reverse=True)
    next_best = [k for k, _ in scored[: max(1, int(top_n))]]

    # Estimated confidence delta if next_best inputs are improved by +0.2 each (capped)
    simulated = dict(coverage)
    for k in next_best:
        simulated[k] = min(1.0, float(simulated.get(k, 0.0)) + 0.2)
    if industry_prior:
        weights = [float(industry_prior.get(k, 1.0)) for k in keys]
        wsum = sum(weights) or 1.0
        sim_avg = sum(float(simulated.get(k, 0.0)) * w for k, w in zip(keys, weights)) / wsum
    else:
        sim_avg = _avg([float(simulated.get(k, 0.0)) for k in keys])
    sim_conf = max(0.0, min(1.0, sim_avg * (1.0 - entropy)))
    delta = sim_conf - confidence

    return {
        "confidence_score": round(confidence, 3),
        "entropy_proxy": round(entropy, 3),
        "data_coverage_avg": round(avg_cov, 3),
        "next_best_questions": next_best,
        "estimated_delta_confidence": round(delta, 3),
    }
