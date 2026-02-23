from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any, List

_RES = Path(__file__).resolve().parent / "resources" / "qway"

def load_ring_map() -> Dict[str, Any]:
    p = _RES / "omega_ring_map.json"
    return json.loads(p.read_text(encoding="utf-8"))

def load_kernel() -> Dict[str, Any]:
    p = _RES / "qway_kernel.json"
    return json.loads(p.read_text(encoding="utf-8"))

def rings_by_layer() -> Dict[str, List[Dict[str, Any]]]:
    ring_map = load_ring_map()
    out: Dict[str, List[Dict[str, Any]]] = {}
    for r in ring_map["rings"]:
        out.setdefault(r["layer"], []).append(r)
    return out

def suggest_ring_focus(theme: str, constraints: Dict[str, Any]) -> Dict[str, Any]:
    """
    Very light heuristic. Goal: categorize the case into 16-ring domains,
    NOT to decide. Used for report structure.
    """
    ring_map = load_ring_map()
    open_rings = []
    stable = []
    soft = []

    t = (theme or "").lower()
    # constraints mapping
    if constraints.get("time"): open_rings.append(9)
    if constraints.get("money"): open_rings.append(10)
    if constraints.get("people"): open_rings.append(6)  # role
    if constraints.get("role"): soft.append(8)  # responsibility

    # keyword mapping
    if any(k in t for k in ["組織","チーム","採用","退職","マネジメント"]): open_rings += [5,6,8]
    if any(k in t for k in ["事業","売上","収益","投資","撤退","M&A","資金"]): open_rings += [10,12,14]
    if any(k in t for k in ["方向性","ビジョン","ブランド","価値","文化"]): open_rings += [13,14,16]

    # normalize unique and bounds
    open_rings = sorted({r for r in open_rings if 1 <= r <= 16})
    stable = sorted({r for r in stable if 1 <= r <= 16})
    soft = sorted({r for r in soft if 1 <= r <= 16})

    return {
        "mode": "omega",
        "ring_state": {"open": open_rings, "stable": stable, "soft_closing": soft},
        "policy": "Q-WAY Ω: premature closure avoided; no recommendation; no full closure.",
        "ring_map_meta": {"ring_count": ring_map["ring_count"], "layers": ring_map["layers"]}
    }
