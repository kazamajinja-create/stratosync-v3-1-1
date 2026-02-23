from __future__ import annotations
from typing import Tuple
from .models import Classification, Label

# --- Fixed thresholds (saved & synchronized) ---
# Stable:        80..100
# Exploration:   60..79
# Mild drift:    40..59
# Reaction-driven: 0..39

def classify_total(total: int) -> Tuple[Label, float]:
    # confidence is a simple heuristic based on distance from boundary
    if total >= 80:
        label: Label = "stable"
        margin = total - 80
    elif total >= 60:
        label = "exploration"
        margin = min(total - 60, 79 - total)
    elif total >= 40:
        label = "mild_drift"
        margin = min(total - 40, 59 - total)
    else:
        label = "reaction_driven"
        margin = 39 - total

    # map margin (0..20+) to confidence (0.55..0.95)
    conf = 0.55 + min(0.40, max(0.0, margin) / 50.0)
    return label, float(round(conf, 2))

def build_classification(total: int, rationale: str) -> Classification:
    label, conf = classify_total(total)
    return Classification(label=label, confidence=conf, rationale=rationale)
