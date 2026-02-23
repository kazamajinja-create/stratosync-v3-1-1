from __future__ import annotations
from typing import Dict, Any, List
from datetime import datetime
import os

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

from app.industry_registry import discover_industry_pack
from app.report_templates import compile_report_fields, merge_layout


DEFAULT_EXECUTIVE_LAYOUT = {
    "title": "STRATOSYNC — Executive Report",
    "sections": [
        {
            "heading": "Core Metrics",
            "items": [
                {"label": "Synchronization Score S", "path": "outputs.synchronization_score", "fmt": "float2"},
                {"label": "Δ-Index", "path": "outputs.delta_index", "fmt": "float2"},
                {"label": "System State", "path": "outputs.system_state", "fmt": "str"},
            ],
        },
        {
            "heading": "RCL — Convergence Intelligence",
            "items": [
                {"label": "BEI Score", "path": "outputs.rcl.branch_explosion.bei_score", "fmt": "float2"},
                {"label": "BEI Level", "path": "outputs.rcl.branch_explosion.risk_level", "fmt": "str"},
                {"label": "ECE Confidence", "path": "outputs.rcl.convergence.confidence_score", "fmt": "float2"},
                {"label": "TCD Ambiguity", "path": "outputs.rcl.twin_cause.ambiguity_flag", "fmt": "bool"},
                {"label": "RSM Residual Index", "path": "outputs.rcl.residual.residual_index", "fmt": "float3"},
                {"label": "RSM Anomaly", "path": "outputs.rcl.residual.anomaly_flag", "fmt": "bool"},
            ],
        },
        {
            "heading": "SDL — Surface Dominance (Holographic)",
            "items": [
                {"label": "Surface Index (SDI)", "path": "outputs.sdl.surface_index", "fmt": "float2"},
                {"label": "Surface Expansion Potential", "path": "outputs.sdl.surface_expansion_potential", "fmt": "float3"},
                {"label": "Volume/Surface Ratio", "path": "outputs.sdl.volume_surface_ratio", "fmt": "float3"},
            ],
        },
        {
            "heading": "ΩCL — Combinatorial Innovation",
            "items": [
                {"label": "Innovation Index (IPI)", "path": "outputs.omega.innovation_index", "fmt": "float2"},
                {"label": "Silo Index", "path": "outputs.omega.silo_index", "fmt": "float3"},
                {"label": "Rigidity Level", "path": "outputs.omega.rigidity_level", "fmt": "str"},
            ],
        },
        {
            "heading": "Executive Synthesis v3",
            "items": [
                {"label": "v3 Score", "path": "outputs.v3.v3_score", "fmt": "float2"},
                {"label": "Top Roadmap 1", "path": "outputs.v3.roadmap.0", "fmt": "str"},
                {"label": "Top Roadmap 2", "path": "outputs.v3.roadmap.1", "fmt": "str"},
            ],
        },
    ],
}


def render_industry_report_pdf(
    out_path: str,
    project_id: str,
    record: Dict[str, Any],
    industry_template: str,
    report_kind: str = "executive",
) -> str:
    """Render an industry-aware report PDF using a template layout.

    Future-proofing: When you add a new industry template, you only need to
    drop a new folder under `industry_packs_runtime/<industry_id>/` with
    `report_layout.<kind>.json`.
    """
    ensure_dir(out_path)
    pack = discover_industry_pack(industry_template)
    overlay = pack.report_layout(report_kind) if pack else None
    layout = merge_layout(DEFAULT_EXECUTIVE_LAYOUT, overlay)
    compiled = compile_report_fields(record, layout)

    c = canvas.Canvas(out_path, pagesize=A4)
    w, h = A4

    ts = record.get("timestamp")
    version = record.get("version")

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(18 * mm, h - 20 * mm, compiled.get("title") or "STRATOSYNC Report")
    c.setFont("Helvetica", 10)
    c.drawString(18 * mm, h - 27 * mm, f"Project: {project_id}")
    c.drawString(18 * mm, h - 33 * mm, f"Industry: {industry_template}   |   Kind: {report_kind}")
    c.drawString(18 * mm, h - 39 * mm, f"Timestamp: {ts}   |   Version: {version}")

    y = h - 52 * mm
    for sec in compiled.get("sections") or []:
        heading = sec.get("heading") or ""
        c.setFont("Helvetica-Bold", 12)
        c.drawString(18 * mm, y, heading)
        y -= 7 * mm
        c.setFont("Helvetica", 10)
        for it in sec.get("items") or []:
            c.drawString(18 * mm, y, f"{it.get('label')}: {it.get('value')}")
            y -= 6 * mm
            # simple page break
            if y < 22 * mm:
                c.showPage()
                y = h - 20 * mm

        y -= 3 * mm

    # Optional: reasons block if present
    o = record.get("outputs", {}) or {}
    reasons: List[str] = (o.get("reasons") or [])[:8]
    if reasons:
        if y < 45 * mm:
            c.showPage()
            y = h - 20 * mm
        c.setFont("Helvetica-Bold", 12)
        c.drawString(18 * mm, y, "Rationale (top)")
        y -= 7 * mm
        c.setFont("Helvetica", 10)
        for r in reasons:
            c.drawString(22 * mm, y, f"• {r}")
            y -= 6 * mm
            if y < 22 * mm:
                c.showPage()
                y = h - 20 * mm

    c.showPage()
    c.save()
    return out_path

def ensure_dir(path: str) -> None:
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)

def render_board_pdf(out_path: str, project_id: str, record: Dict[str, Any], chart_png_path: str | None = None) -> str:
    """Render a 1-page board PDF for the latest project state."""
    ensure_dir(out_path)
    c = canvas.Canvas(out_path, pagesize=A4)
    w, h = A4

    o = record.get("outputs", {}) or {}
    i = record.get("inputs", {}) or {}
    ts = record.get("timestamp") or datetime.utcnow().isoformat() + "Z"
    version = record.get("version") or "2.6.2"
    state = o.get("system_state", "UNKNOWN")

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(18*mm, h - 20*mm, "STRATOSYNC — Board Decision Sheet")
    c.setFont("Helvetica", 10)
    c.drawString(18*mm, h - 27*mm, f"Project: {project_id}")
    c.drawString(18*mm, h - 33*mm, f"Timestamp: {ts}   |   Version: {version}")

    # State
    c.setFont("Helvetica-Bold", 14)
    c.drawString(18*mm, h - 45*mm, f"SYSTEM STATE: {state}")

    # Metrics table-like
    y = h - 58*mm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(18*mm, y, "Core Metrics")
    y -= 7*mm
    c.setFont("Helvetica", 10)

    rows = [
        ("Political (input)", i.get("political_score")),
        ("Capital (input)", i.get("capital_score")),
        ("Execution (input)", i.get("execution_score")),
        ("Noise η", i.get("noise")),
        ("Synchronization Score S", o.get("synchronization_score")),
        ("Δ-Index", o.get("delta_index")),
        ("Ψ adjusted", o.get("psi_adjusted_execution")),
    ]
    for k, v in rows:
        c.drawString(18*mm, y, f"{k}: {v}")
        y -= 6*mm

    # Reasons
    y -= 2*mm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(18*mm, y, "Rationale (top)")
    y -= 7*mm
    c.setFont("Helvetica", 10)
    reasons: List[str] = (o.get("reasons") or [])[:6]
    for r in reasons:
        c.drawString(22*mm, y, f"• {r}")
        y -= 6*mm

    # RCL section (optional)
    rcl = None
    if isinstance(o, dict):
        rcl = o.get("rcl")
    if isinstance(rcl, dict):
        y -= 2*mm
        c.setFont("Helvetica-Bold", 11)
        c.drawString(18*mm, y, "RCL — Convergence Intelligence")
        y -= 7*mm
        c.setFont("Helvetica", 9)
        bei = (rcl.get("branch_explosion") or {})
        ece = (rcl.get("convergence") or {})
        tcd = (rcl.get("twin_cause") or {})
        rsm = (rcl.get("residual") or {})
        lines = [
            f"BEI: score={bei.get('bei_score')} level={bei.get('risk_level')} dof={bei.get('effective_dof')}",
            f"ECE: confidence={ece.get('confidence_score')} next={', '.join((ece.get('next_best_questions') or [])[:3])}",
            f"TCD: ambiguity={tcd.get('ambiguity_flag')} causes={len(tcd.get('possible_causes') or [])}",
            f"RSM: residual_index={rsm.get('residual_index')} anomaly={rsm.get('anomaly_flag')}",
        ]
        for line in lines:
            c.drawString(18*mm, y, line)
            y -= 5*mm

    # SDL + ΩCL section (optional)
    sdl = o.get("sdl") if isinstance(o, dict) else None
    omega = o.get("omega") if isinstance(o, dict) else None
    if isinstance(sdl, dict) or isinstance(omega, dict):
        y -= 2*mm
        c.setFont("Helvetica-Bold", 11)
        c.drawString(18*mm, y, "v3 Layers — Surface (SDL) & Ω (Combinatorial)")
        y -= 7*mm
        c.setFont("Helvetica", 9)
        if isinstance(sdl, dict):
            c.drawString(18*mm, y, f"SDL: SDI={sdl.get('surface_index')} headroom={sdl.get('surface_expansion_potential')} V/S={sdl.get('volume_surface_ratio')}")
            y -= 5*mm
        if isinstance(omega, dict):
            c.drawString(18*mm, y, f"ΩCL: IPI={omega.get('innovation_index')} silo={omega.get('silo_index')} rigidity={omega.get('rigidity_level')}")
            y -= 5*mm

    # Audit hashes
    y -= 2*mm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(18*mm, y, "Audit")
    y -= 7*mm
    c.setFont("Helvetica", 9)
    audit = record.get("audit", {}) or {}
    c.drawString(18*mm, y, f"record_hash: {audit.get('record_hash')}")
    y -= 5*mm
    c.drawString(18*mm, y, f"prev_hash:   {audit.get('prev_hash')}")

    # Chart
    if chart_png_path and os.path.exists(chart_png_path):
        # place chart at bottom half
        try:
            img_w = 170*mm
            img_h = 65*mm
            c.drawImage(chart_png_path, 18*mm, 18*mm, width=img_w, height=img_h, preserveAspectRatio=True, anchor='sw')
            c.setFont("Helvetica", 8)
            c.drawString(18*mm, 15*mm, "Trend: Δ-Index & Synchronization Score (recent evaluations)")
        except Exception:
            pass

    c.showPage()
    c.save()
    return out_path
