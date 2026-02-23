"""AXIS Drift Index adapter for Ω QCS unified pack.
This module keeps Drift Index as an optional analytical layer.
"""
from __future__ import annotations
from typing import Any, Dict, Optional

try:
    from .axis_drift_index.pipeline import run_pipeline  # type: ignore
except Exception as e:  # pragma: no cover
    run_pipeline = None  # type: ignore
    _IMPORT_ERROR = e
else:
    _IMPORT_ERROR = None

def compute_axis_drift(input_payload: Dict[str, Any], *, baseline: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Compute AXIS drift scores from the bundled axis_drift_index module.

    Parameters
    ----------
    input_payload : dict
        Current state snapshot (answers, metrics, etc.) compatible with axis_drift_index.
    baseline : dict | None
        Optional baseline snapshot for drift comparison.

    Returns
    -------
    dict
        Drift analysis output (scores, classification, report fields).
    """
    if run_pipeline is None:
        raise ImportError(f"axis_drift_index is not available: {_IMPORT_ERROR}")
    return run_pipeline(current=input_payload, baseline=baseline)
