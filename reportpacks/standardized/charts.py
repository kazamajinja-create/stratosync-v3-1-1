from __future__ import annotations
from typing import List, Dict, Any
import os
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def ensure_dir(path: str) -> None:
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)

def render_trend_png(out_path: str, series: List[Dict[str, Any]], title: str = "Trend") -> str:
    """Render a simple line chart (no custom colors) for Δ and S over time."""
    ensure_dir(out_path)

    # Keep last N points
    x = list(range(1, len(series) + 1))
    delta = [p.get("delta_index") for p in series]
    sync = [p.get("synchronization_score") for p in series]

    plt.figure()
    plt.plot(x, delta, label="Δ-Index")
    plt.plot(x, sync, label="S (Sync Score)")
    plt.xlabel("Evaluation (recent →)")
    plt.ylabel("Score")
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=160)
    plt.close()
    return out_path
