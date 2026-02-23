from __future__ import annotations

from typing import Any, Dict


def residual_monitor(
    predicted: float | None,
    actual: float | None,
    threshold: float = 0.15,
) -> Dict[str, Any]:
    """Residual Structure Monitor (RSM).

    Tracks 'unexplained residual' as an index and raises an alert when above threshold.
    This is deliberately simple for MVP: it creates a durable 'monitoring reason' for
    continuation and prevents overconfidence.
    """

    if predicted is None or actual is None or predicted == 0:
        return {
            "residual_index": None,
            "anomaly_flag": False,
            "threshold": threshold,
            "notes": ["Insufficient data to compute residual."],
        }

    residual = float(actual) - float(predicted)
    idx = abs(residual) / abs(float(predicted))
    anomaly = idx > float(threshold)

    hypotheses = []
    if anomaly:
        hypotheses = [
            "Hidden workload/fatigue accumulation",
            "Uncaptured informal leadership dynamics",
            "External demand-quality shift",
            "Measurement mismatch (accounting timing / KPI definition)",
        ]

    return {
        "predicted": float(predicted),
        "actual": float(actual),
        "residual": residual,
        "residual_index": round(idx, 3),
        "anomaly_flag": anomaly,
        "threshold": threshold,
        "latent_factor_hypotheses": hypotheses,
    }
