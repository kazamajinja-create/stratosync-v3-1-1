from __future__ import annotations
from typing import Dict

def normalize(financials: Dict) -> Dict:
    """Normalize and derive minimal fields for structural extraction.
    This function does NOT validate accounting correctness, and does NOT provide advice.
    """
    pl = financials.get("pl", {}) or {}
    cf = financials.get("cf", {}) or {}
    derived = dict(financials.get("derived", {}) or {})

    rev = float(pl.get("revenue", 0) or 0)
    sga = float(pl.get("sg_and_a", 0) or 0)
    if "fixed_cost_ratio" not in derived and rev > 0:
        derived["fixed_cost_ratio"] = max(0.0, min(1.0, sga / rev))

    op = float(cf.get("operating_cf", 0) or 0)
    inv = float(cf.get("investing_cf", 0) or 0)
    fin = float(cf.get("financing_cf", 0) or 0)

    def s(x: float) -> str:
        return "+" if x > 0 else "-" if x < 0 else "0"

    if "cf_pattern" not in derived:
        derived["cf_pattern"] = f"OP{s(op)} / INV{s(inv)} / FIN{s(fin)}"

    ni = float(pl.get("net_income", 0) or 0)
    if "variance" not in derived and rev > 0:
        derived["variance"] = abs(ni) / max(rev, 1.0)

    out = dict(financials)
    out["derived"] = derived
    return out
