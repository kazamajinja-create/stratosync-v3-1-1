from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import datetime, json

from .commercial_runner import run_commercial_analysis

@dataclass
class PortfolioResult:
    generated_utc: str
    entity_count: int
    priority_distribution: Dict[str, int]
    top_collision_points: List[Tuple[str, float]]  # (key, score)
    entity_summaries: List[Dict[str, Any]]
    artifacts: Dict[str, Any]

def _aggregate_priority(summaries: List[Dict[str, Any]]) -> Dict[str, int]:
    dist = {"衝突優先度レベル1": 0, "衝突優先度レベル2": 0, "衝突優先度レベル3": 0}
    for s in summaries:
        band = s.get("collision_outputs", {}).get("collision_band")
        if band in dist:
            dist[band] += 1
    return dist

def _aggregate_collision_points(summaries: List[Dict[str, Any]], top_k: int = 10) -> List[Tuple[str, float]]:
    scores: Dict[str, float] = {}
    for s in summaries:
        top = s.get("collision_outputs", {}).get("explainability", {}).get("collision", {}).get("top_contributors_raw", [])
        for k, v in top:
            scores[k] = scores.get(k, 0.0) + float(v)
    return sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:top_k]

def run_portfolio_mode(
    entities: List[Dict[str, Any]],
    out_dir: str = "outputs/portfolio",
    market_provider: str = "stub",
    market_file: Optional[str] = None,
) -> PortfolioResult:
    dt = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    out_dir_p = Path(out_dir)
    out_dir_p.mkdir(parents=True, exist_ok=True)

    summaries: List[Dict[str, Any]] = []
    for i, ent in enumerate(entities, start=1):
        # Each entity can pass: financials, structure, internal_scores, hssi, sensitivity_map
        payload = run_commercial_analysis(
            financials=ent.get("financials"),
            structure=ent.get("structure"),
            market_provider=ent.get("market_provider", market_provider),
            market_file=ent.get("market_file", market_file),
            internal_scores=ent.get("internal_scores"),
            hssi=float(ent.get("hssi", 60.0)),
            sensitivity_map=ent.get("sensitivity_map"),
            out_dir=str(out_dir_p / f"entity_{i}"),
            audit_log=str(out_dir_p / f"entity_{i}" / "audit_log.jsonl"),
        )
        summaries.append(payload)

    dist = _aggregate_priority(summaries)
    top_cp = _aggregate_collision_points(summaries, top_k=10)

    portfolio_json = {
        "generated_utc": dt,
        "entity_count": len(summaries),
        "priority_distribution": dist,
        "top_collision_points": top_cp,
        "entities": [
            {
                "engine_version": s.get("engine_version"),
                "structure": (s.get("collision_outputs") or {}).get("explainability", {}).get("inputs", {}),
                "collision_band": (s.get("collision_outputs") or {}).get("collision_band"),
                "artifacts": s.get("artifacts"),
            } for s in summaries
        ]
    }

    json_path = out_dir_p / "portfolio_summary.json"
    json_path.write_text(json.dumps(portfolio_json, ensure_ascii=False, indent=2), encoding="utf-8")

    return PortfolioResult(
        generated_utc=dt,
        entity_count=len(summaries),
        priority_distribution=dist,
        top_collision_points=top_cp,
        entity_summaries=summaries,
        artifacts={"portfolio_json": str(json_path)},
    )
