from __future__ import annotations
from dataclasses import dataclass

@dataclass
class FeatureFlags:
    heatmap: bool = False
    api: bool = False
    timeseries: bool = False
    network_viz: bool = False
    full_report: bool = True

def flags_for_plan(plan: str) -> FeatureFlags:
    plan = (plan or "professional").lower()
    if plan == "enterprise":
        return FeatureFlags(heatmap=True, api=True, timeseries=True, network_viz=True, full_report=True)
    return FeatureFlags(heatmap=False, api=False, timeseries=False, network_viz=False, full_report=True)
