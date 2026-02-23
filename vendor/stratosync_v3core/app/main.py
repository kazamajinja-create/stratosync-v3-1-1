from __future__ import annotations
import os
import uuid
from datetime import datetime
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import HTMLResponse, FileResponse
from app.config import settings
from app.models import EvaluateRequest, OverrideRequest
from app.core import EvalParams, evaluate
from app.audit import append_audit_record, filter_records_by_project, verify_hash_chain, export_evidence_bundle, export_evidence_bundle_with_attachments
from app.state_store import upsert_project_state, get_project_state
from app.charts import render_trend_png
from app.reporting import render_board_pdf, render_industry_report_pdf
from app.industry_registry import load_rcl_params_for
from app.rcl.models import RCLRequest
from app.rcl.orchestrator import run_rcl
from app.sdl.sdi import calculate_sdi
from app.omega.ipi import calculate_ipi
from app.v3.models import V3AnalyzeRequest
from app.v3.synthesis import synthesize_v3

def _load_industry_params(industry_template: str) -> dict:
    """Load industry params (future-proof).

    New industries are supported by adding a runtime pack under:
      industry_packs_runtime/<industry_id>/rcl_params.json

    Legacy fallback (older packs) remains supported via docs mapping if present.
    """
    params = load_rcl_params_for(industry_template)
    if params:
        return params
    # legacy fallback
    try:
        import json
        path = os.path.join("docs", "industry_packs", "rcl_industry_params.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                bank = json.load(f)
            return dict(bank.get(industry_template) or bank.get("generic") or {})
    except Exception:
        pass
    return {}

app = FastAPI(
    title="STRATOSYNC v3.0 — Ω-Surface Architecture (RCL + SDL + ΩCL)",
    version=settings.VERSION,
)

# --- RCL (Ramanujan Convergence Layer) ---

@app.post("/rcl/analyze")
def rcl_analyze(req: RCLRequest):
    """Run the RCL layer on an integrated case.

    This endpoint is designed for business-consulting templates (e.g., SilverCare).
    It returns four cross-cutting diagnostics: BEI/ECE/TCD/RSM.
    """

    industry_params = _load_industry_params(req.industry_template)
    rcl_out = run_rcl(req.model_dump(), industry_params=industry_params)

    evaluation_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat() + "Z"
    project_id = f"case:{req.case_id}"

    record = {
        "evaluation_id": evaluation_id,
        "project_id": project_id,
        "version": settings.VERSION,
        "timestamp": now,
        "inputs": req.model_dump(),
        "outputs": {"rcl": rcl_out},
        "audit": {},
    }
    record_hash, prev = append_audit_record(settings.AUDIT_LOG_PATH, record)
    record["audit"] = {"record_hash": record_hash, "prev_hash": prev}
    upsert_project_state(settings.STATE_DB_PATH, project_id, record)
    return record


# --- v3 Unified Analysis (RCL + SDL + ΩCL + Synthesis) ---

@app.post("/v3/analyze")
def v3_analyze(req: V3AnalyzeRequest):
    """Run STRATOSYNC v3.0 unified analysis.

    Accepts:
      - RCL compatible fields (degrees_of_freedom/data_coverage/kpi_timeseries/interventions)
      - SDL inputs (boundary surface)
      - ΩCL inputs (combinatorial entropy)

    Returns a single record with outputs: rcl, sdl, omega, v3.
    """

    # 1) RCL
    industry_params = _load_industry_params(req.industry_template)
    rcl_payload = {
        "case_id": req.case_id,
        "industry_template": req.industry_template,
        "degrees_of_freedom": req.degrees_of_freedom,
        "data_coverage": req.data_coverage,
        "kpi_timeseries": req.kpi_timeseries,
        "interventions": req.interventions,
    }
    rcl_out = run_rcl(rcl_payload, industry_params=industry_params)

    # 2) SDL
    sdl_in = req.sdl.model_dump()
    sdl_out = calculate_sdi(**sdl_in)

    # 3) ΩCL
    omega_in = req.omega.model_dump()
    omega_out = calculate_ipi(**omega_in)

    # 4) Optional internal evaluate (only if provided)
    eval_out = None
    if req.political_score is not None and req.capital_score is not None and req.execution_score is not None and req.noise is not None:
        params = EvalParams()
        eval_out, _ = evaluate(
            P=req.political_score,
            C=req.capital_score,
            E=req.execution_score,
            eta=req.noise,
            params=params,
        )

    # 5) Synthesis
    v3 = synthesize_v3(
        evaluate_outputs=eval_out,
        rcl_outputs=rcl_out,
        sdl_outputs=sdl_out,
        omega_outputs=omega_out,
    )

    evaluation_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat() + "Z"
    project_id = f"case:{req.case_id}"

    outputs = {
        "rcl": rcl_out,
        "sdl": sdl_out,
        "omega": omega_out,
        "v3": v3,
    }
    # If internal evaluate was computed, include it for existing board/report fields.
    if isinstance(eval_out, dict):
        outputs.update(eval_out)

    record = {
        "evaluation_id": evaluation_id,
        "project_id": project_id,
        "version": settings.VERSION,
        "timestamp": now,
        "inputs": req.model_dump(),
        "outputs": outputs,
        "audit": {},
    }

    record_hash, prev = append_audit_record(settings.AUDIT_LOG_PATH, record)
    record["audit"] = {"record_hash": record_hash, "prev_hash": prev}
    upsert_project_state(settings.STATE_DB_PATH, project_id, record)
    return record


def health():
    return {"status": "ok", "version": settings.VERSION}

@app.post("/evaluate")
def post_evaluate(req: EvaluateRequest):
    params = EvalParams()
    if req.weights is not None:
        params.wp, params.wc, params.we = req.weights.wp, req.weights.wc, req.weights.we
    params.alpha = float(req.alpha or params.alpha)

    outputs, _ = evaluate(
        P=req.political_score,
        C=req.capital_score,
        E=req.execution_score,
        eta=req.noise,
        params=params,
    )

    evaluation_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat() + "Z"
    project_id = req.project_id or f"anon:{evaluation_id}"

    record = {
        "evaluation_id": evaluation_id,
        "project_id": project_id,
        "version": settings.VERSION,
        "timestamp": now,
        "inputs": req.model_dump(),
        "outputs": outputs,
        "audit": {},  # filled by audit logger
    }

    record_hash, prev = append_audit_record(settings.AUDIT_LOG_PATH, record)
    record["audit"] = {"record_hash": record_hash, "prev_hash": prev}

    upsert_project_state(settings.STATE_DB_PATH, project_id, record)
    return record

@app.get("/state/{project_id}")
def get_state(project_id: str):
    rec = get_project_state(settings.STATE_DB_PATH, project_id)
    if not rec:
        raise HTTPException(status_code=404, detail="project_id not found")
    return rec

@app.get("/delta-trend/{project_id}")
def delta_trend(project_id: str, n: int = 50):
    records = filter_records_by_project(settings.AUDIT_LOG_PATH, project_id, limit=max(1, min(n, 2000)))
    if not records:
        raise HTTPException(status_code=404, detail="project_id not found in audit log")
    series = []
    for r in records[-n:]:
        o = r.get("outputs", {})
        series.append({
            "timestamp": r.get("timestamp"),
            "delta_index": o.get("delta_index"),
            "synchronization_score": o.get("synchronization_score"),
            "system_state": o.get("system_state"),
        })
    return {"project_id": project_id, "count": len(series), "series": series}

@app.get("/trend/png/{project_id}")
def trend_png(project_id: str, n: int = 50):
    # Build series and render a png for embedding in board view
    records = filter_records_by_project(settings.AUDIT_LOG_PATH, project_id, limit=max(1, min(n, 2000)))
    if not records:
        raise HTTPException(status_code=404, detail="project_id not found in audit log")
    series = []
    for r in records[-n:]:
        o = r.get("outputs", {})
        series.append({
            "timestamp": r.get("timestamp"),
            "delta_index": o.get("delta_index"),
            "synchronization_score": o.get("synchronization_score"),
            "system_state": o.get("system_state"),
        })
    out_path = f"data/trend_{project_id.replace(':','_')}.png"
    render_trend_png(out_path, series, title=f"Trend — {project_id}")
    return FileResponse(out_path, media_type="image/png", filename="trend.png")


@app.get("/report/pdf/{project_id}")
def report_pdf(project_id: str, kind: str = "executive", industry: str | None = None):
    """Generate an industry-aware PDF report.

    - If `industry` is not provided, the server tries to infer it from
      the latest project state (RCL request: inputs.industry_template).
    - If no industry pack exists, it falls back to the default layout.

    This endpoint is the key to future growth: adding new industry templates
    does not require code changes—only a new runtime pack folder.
    """
    rec = get_project_state(settings.STATE_DB_PATH, project_id)
    if not rec:
        raise HTTPException(status_code=404, detail="project_id not found")

    inferred = None
    try:
        inferred = (rec.get("inputs", {}) or {}).get("industry_template")
    except Exception:
        inferred = None

    industry_template = industry or inferred or "generic"

    out_path = f"data/report_{kind}_{project_id.replace(':','_')}.pdf"
    render_industry_report_pdf(out_path, project_id, rec, industry_template=industry_template, report_kind=kind)
    return FileResponse(out_path, media_type="application/pdf", filename=os.path.basename(out_path))

@app.get("/audit/verify/{project_id}")
def audit_verify(project_id: str, n: int = 200):
    records = filter_records_by_project(settings.AUDIT_LOG_PATH, project_id, limit=max(1, min(n, 2000)))
    if not records:
        raise HTTPException(status_code=404, detail="project_id not found in audit log")
    return verify_hash_chain(records)

@app.post("/evidence/export/{project_id}")
def evidence_export(project_id: str, n: int = 500, x_admin_token: str = Header(default="")):
    if x_admin_token != settings.ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="forbidden")
    now = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    out_zip = f"data/evidence_{project_id.replace(':','_')}_{now}.zip"

    # Generate attachments (trend png + board pdf) first
    # Trend series
    records = filter_records_by_project(settings.AUDIT_LOG_PATH, project_id, limit=max(1, min(n, 5000)))
    series = []
    for r in records[-min(50, len(records)):]:  # cap to 50 points for chart
        o = r.get("outputs", {})
        series.append({
            "timestamp": r.get("timestamp"),
            "delta_index": o.get("delta_index"),
            "synchronization_score": o.get("synchronization_score"),
            "system_state": o.get("system_state"),
        })
    trend_png_path = f"data/trend_{project_id.replace(':','_')}.png"
    if series:
        render_trend_png(trend_png_path, series, title=f"Trend — {project_id}")

    # Board PDF (uses latest state)
    rec_latest = get_project_state(settings.STATE_DB_PATH, project_id)
    board_pdf_path = None
    if rec_latest:
        board_pdf_path = f"data/board_{project_id.replace(':','_')}.pdf"
        render_board_pdf(board_pdf_path, project_id, rec_latest, chart_png_path=trend_png_path if os.path.exists(trend_png_path) else None)

    manifest = export_evidence_bundle_with_attachments(
        settings.AUDIT_LOG_PATH,
        settings.STATE_DB_PATH,
        project_id,
        out_zip,
        limit=max(1, min(n, 5000)),
        attachments={
            "trend.png": trend_png_path if os.path.exists(trend_png_path) else None,
            "board.pdf": board_pdf_path if board_pdf_path and os.path.exists(board_pdf_path) else None,
        }
    )
    return {"status": "ok", "bundle_path": out_zip, "manifest": manifest}

@app.get("/board/{project_id}", response_class=HTMLResponse)
def board_view(project_id: str):
    rec = get_project_state(settings.STATE_DB_PATH, project_id)
    if not rec:
        raise HTTPException(status_code=404, detail="project_id not found")

    o = rec.get("outputs", {}) or {}
    i = rec.get("inputs", {}) or {}
    state = o.get("system_state", "UNKNOWN")
    light = {"GO":"🟢", "CONDITIONAL":"🟡", "FREEZE":"🔴"}.get(state, "⚪")

    # embed chart
    chart_url = f"/trend/png/{project_id}?n=50"

    # industry-aware report links
    inferred_industry = (i or {}).get("industry_template") or "generic"
    report_exec_url = f"/report/pdf/{project_id}?kind=executive&industry={inferred_industry}"
    report_agent_url = f"/report/pdf/{project_id}?kind=agent&industry={inferred_industry}"

    rcl = o.get("rcl") if isinstance(o, dict) else None
    rcl_html = ""
    if isinstance(rcl, dict):
        bei = (rcl.get("branch_explosion") or {})
        ece = (rcl.get("convergence") or {})
        tcd = (rcl.get("twin_cause") or {})
        rsm = (rcl.get("residual") or {})
        rcl_html = f"""
        <h3>RCL — Convergence Intelligence</h3>
        <table>
          <tr><th>Module</th><th>Key output</th></tr>
          <tr><td>BEI</td><td>score={bei.get('bei_score')} level={bei.get('risk_level')}</td></tr>
          <tr><td>ECE</td><td>confidence={ece.get('confidence_score')} next={', '.join(ece.get('next_best_questions') or [])}</td></tr>
          <tr><td>TCD</td><td>ambiguity={tcd.get('ambiguity_flag')} causes={len(tcd.get('possible_causes') or [])}</td></tr>
          <tr><td>RSM</td><td>residual_index={rsm.get('residual_index')} anomaly={rsm.get('anomaly_flag')}</td></tr>
        </table>
        """

    html = f"""
    <html><head><meta charset='utf-8'/><title>STRATOSYNC Board View</title>
    <style>
      body {{ font-family: Arial, sans-serif; margin: 24px; }}
      .state {{ font-size: 28px; font-weight: 700; }}
      table {{ border-collapse: collapse; width: 720px; margin-top: 12px; }}
      td, th {{ border: 1px solid #ccc; padding: 8px; }}
      .reasons li {{ margin-bottom: 6px; }}
      .mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; }}
      .chart {{ margin-top: 16px; }}
      .links a {{ margin-right: 12px; }}
    </style></head>
    <body>
      <div class='state'>{light} SYSTEM STATE: {state}</div>
      <div>Project: <span class='mono'>{project_id}</span></div>
      <div>Timestamp: <span class='mono'>{rec.get("timestamp")}</span> | Version: <span class='mono'>{rec.get("version")}</span></div>

      <div class='links'>
        <a href='/board/pdf/{project_id}' target='_blank'>Download Board PDF</a>
        <a href='{report_exec_url}' target='_blank'>Executive Report PDF</a>
        <a href='{report_agent_url}' target='_blank'>Agent Brief PDF</a>
        <a href='{chart_url}' target='_blank'>Open Trend PNG</a>
      </div>

      <table>
        <tr><th>Metric</th><th>Value</th></tr>
        <tr><td>Political (input)</td><td>{i.get("political_score")}</td></tr>
        <tr><td>Capital (input)</td><td>{i.get("capital_score")}</td></tr>
        <tr><td>Execution (input)</td><td>{i.get("execution_score")}</td></tr>
        <tr><td>Noise η</td><td>{i.get("noise")}</td></tr>
        <tr><td>Synchronization Score S</td><td>{o.get("synchronization_score")}</td></tr>
        <tr><td>Δ-Index</td><td>{o.get("delta_index")}</td></tr>
        <tr><td>Ψ adjusted</td><td>{o.get("psi_adjusted_execution")}</td></tr>
      </table>

      <h3>Rationale (top)</h3>
      <ul class='reasons'>
        {''.join([f"<li>{r}</li>" for r in (o.get("reasons") or [])[:6]])}
      </ul>

      {rcl_html}

      <div class='chart'>
        <h3>Trend (recent)</h3>
        <img src='{chart_url}' width='720' alt='trend chart'/>
      </div>

      <h3>Audit</h3>
      <div>record_hash: <span class='mono'>{rec.get("audit", {}).get("record_hash")}</span></div>
      <div>prev_hash: <span class='mono'>{rec.get("audit", {}).get("prev_hash")}</span></div>
    </body></html>
    """
    return html

@app.get("/board/pdf/{project_id}")
def board_pdf(project_id: str, n: int = 50):
    rec = get_project_state(settings.STATE_DB_PATH, project_id)
    if not rec:
        raise HTTPException(status_code=404, detail="project_id not found")

    # render trend png first
    records = filter_records_by_project(settings.AUDIT_LOG_PATH, project_id, limit=max(1, min(n, 2000)))
    series = []
    for r in records[-n:]:
        o = r.get("outputs", {})
        series.append({
            "timestamp": r.get("timestamp"),
            "delta_index": o.get("delta_index"),
            "synchronization_score": o.get("synchronization_score"),
            "system_state": o.get("system_state"),
        })
    png_path = f"data/trend_{project_id.replace(':','_')}.png"
    if series:
        render_trend_png(png_path, series, title=f"Trend — {project_id}")

    out_pdf = f"data/board_{project_id.replace(':','_')}.pdf"
    render_board_pdf(out_pdf, project_id, rec, chart_png_path=png_path if os.path.exists(png_path) else None)
    return FileResponse(out_pdf, media_type="application/pdf", filename="board.pdf")

@app.post("/override-lock")
def override_lock(req: OverrideRequest, x_admin_token: str = Header(default="")):
    if x_admin_token != settings.ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="forbidden")

    evaluation_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat() + "Z"

    record = {
        "evaluation_id": evaluation_id,
        "project_id": req.project_id,
        "version": settings.VERSION,
        "timestamp": now,
        "inputs": {"override": req.model_dump()},
        "outputs": {
            "system_state": req.override_state,
            "reasons": [f"Override: {req.reason}", f"Expires at: {req.expires_at}"]
        },
        "audit": {},
        "governance": {"type": "override", "expires_at": req.expires_at},
    }
    record_hash, prev = append_audit_record(settings.AUDIT_LOG_PATH, record)
    record["audit"] = {"record_hash": record_hash, "prev_hash": prev}

    upsert_project_state(settings.STATE_DB_PATH, req.project_id, record)
    return record
