from __future__ import annotations
from typing import Dict, Any, Optional
from pathlib import Path

from .integrated_market_pipeline import run_integrated_market_pipeline
from .market_context_injector import apply_external_factors, InjectorParams
from .external_factor_sensitivity_defaults import DEFAULT_SENSITIVITY_MATRIX
from .industry_injection_router import resolve_injection_policy
from .collision_model import run_collision_suite
from .strategic_priority_generator import generate_strategic_priorities
from .market_data_connector import get_provider
from .audit_trail import AuditTrailLogger
from .report_generator import render_report_md, save_md, save_pdf_from_md
from . import __version__

def run_commercial_analysis(
    axis_drift_payload: Optional[Dict[str, Any]] = None,
    external_M: float = 2.0,
    external_C: float = 2.0,
    external_R_ext: float = 2.0,
    external_strategy: str = "A",
    competitor_velocity: float = 0.0,
    external_sensitivity_matrix: Optional[Dict[str, Dict[str, float]]] = None,
    injector_params: Optional[InjectorParams] = None,
    financials: Optional[Dict[str, Any]] = None,
    structure: Optional[Dict[str, Any]] = None,
    market_provider: str = "stub",
    market_file: Optional[str] = None,
    internal_scores: Optional[Dict[str, float]] = None,
    hssi: float = 60.0,
    market_volatility: float = 2.0,
    growth_momentum: float = 2.0,
    sensitivity_map: Optional[Dict[str, float]] = None,
    out_dir: str = "outputs",
    audit_log: str = "outputs/audit/audit_log.jsonl",
) -> Dict[str, Any]:
    structure = structure or {}
    internal_scores = internal_scores or {}
    sensitivity_map = sensitivity_map or {}

    provider = get_provider(market_provider, path=market_file)
    mdp = provider.fetch({"entity": structure.get("name", "unknown")})

    base = run_integrated_market_pipeline(financials=financials, structure=structure, market_inputs={
        "MVI": mdp.MVI, "IGM": mdp.IGM, "CPI": mdp.CPI, "RFI": mdp.RFI
    })

# --- External factor injection into 12 variables (internal computation) ---
# If industry_key is provided, automatically select strategy/matrix conservatively (audit-friendly).
industry_key = (structure.get("industry_key") or structure.get("industry") or "").strip().lower()
policy = resolve_injection_policy(
    industry_key=industry_key,
    competitor_velocity=competitor_velocity,
    override_strategy=(external_strategy if external_strategy else None),
    override_matrix=(external_sensitivity_matrix if external_sensitivity_matrix else None),
    override_params=injector_params,
)
ext_matrix = policy.sensitivity_matrix

adjusted_scores_0_100, injection_explain = apply_external_factors(
    internal_0_100=structure.get("vars_12", {}) or structure.get("internal_12", {}) or {},
    M=external_M, C=external_C, R_ext=external_R_ext,
    sensitivity_matrix=ext_matrix,
    strategy=policy.strategy,
    params=injector_params,
    competitor_velocity=competitor_velocity,
)
    injection_explain["resolved_policy"] = {"industry_key": industry_key, "strategy": policy.strategy}
structure = dict(structure)
structure["vars_12_adjusted"] = adjusted_scores_0_100



    collision = run_collision_suite(
        internal_scores=internal_scores,
        hssi=hssi,
        market_volatility=mdp.mvi_score if mdp else market_volatility,
        growth_momentum=mdp.igm_score if mdp else growth_momentum,
        sensitivity_map=sensitivity_map,
    )

    priority = generate_strategic_priorities(collision.collision_intensity)

    
# Optional AXIS Drift Index integration (non-mandatory)
axis_drift = axis_drift_payload
if axis_drift is None:
    # Best-effort dynamic import if drift pack is bundled
    try:
        import importlib
        # common module names - adjust if different
        for mod_name in ["axis_drift_index", "axis_drift", "AXIS_Drift_Index", "axis_drift_index_module"]:
            try:
                m = importlib.import_module(mod_name)
                axis_drift = {"note": "Drift module imported", "module": mod_name}
                break
            except Exception:
                continue
    except Exception:
        pass

payload = {
        "snapshot": base.get("snapshot"),
        "indices": base.get("indices"),
        "market_context": base.get("market_context"),
        "axis_drift": axis_drift,
        "external_injection": injection_explain,
        "collision_outputs": {
            "collision_intensity": collision.collision_intensity,
            "collision_band": collision.collision_band,
            "structural_resilience": collision.structural_resilience,
            "amplification_index": collision.amplification_index,
            "explainability": collision.explainability,
        },
        "strategic_priority": priority,
        "policy": "Non-Decision / Non-Advisory",
        "engine_version": __version__,
    }

    out_dir_p = Path(out_dir)
    out_dir_p.mkdir(parents=True, exist_ok=True)
    md_text = render_report_md(payload)
    md_path = save_md(md_text, out_dir_p / "report.md")
    pdf_path = save_pdf_from_md(md_text, out_dir_p / "report.pdf")

    logger = AuditTrailLogger(audit_log)
    audit_event = logger.log(__version__, inputs={
        "financials": financials,
        "structure": structure,
        "market_packet": mdp.__dict__,
        "internal_scores": internal_scores,
        "external_factors": {"M": external_M, "C": external_C, "R_ext": external_R_ext, "strategy": external_strategy, "competitor_velocity": competitor_velocity},
        "external_injection": injection_explain,
        "hssi": hssi,
        "sensitivity_map": sensitivity_map,
    }, outputs=payload, metadata={"md": str(md_path), "pdf": str(pdf_path)})

    payload["audit_event"] = audit_event.__dict__
    payload["artifacts"] = {"md": str(md_path), "pdf": str(pdf_path), "audit_log": audit_log}
    return payload
