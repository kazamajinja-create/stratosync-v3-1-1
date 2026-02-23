from __future__ import annotations
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from omega_qcs.models import (
    CaseCreate, IntakeSubmit, ReportBuildRequest,
    SessionStart, SessionNote, SessionFinalize
)
from omega_qcs.omega_case_registry import create_case, get_case, set_status
from omega_qcs.omega_intake import get_question_set, submit_intake, fetch_intake
from omega_qcs.omega_quantum_analyzer import analyze
from omega_qcs.omega_report_builder import build_report
from omega_qcs.omega_session_orchestrator import start_session, add_note, finalize
from omega_qcs.omega_meditation_micro import grounding, reset
from omega_qcs.omega_deliverables_pack import deliver
from omega_qcs.omega_contract_pack import build_contract_pack
from omega_qcs.kpi_profile_axis import AXIS_INDEPENDENCE_KPI, as_dict
from omega_qcs.external_view_simulator import simulate_for_scheme
from omega_qcs.quality_guard import evaluate as q_evaluate, findings_to_text
from omega_qcs.axis_independence_check import evaluate_independence

from omega_qcs.storage import get as db_get

app = FastAPI(title="Ω量子コンサルティングスキームモード v0.1")

@app.get("/omega/health")
def health():
    return {"ok": True}

# ---- Case ----
@app.post("/omega/case/create")
def api_create_case(payload: CaseCreate):
    return create_case(payload).model_dump()

@app.get("/omega/case/{case_id}")
def api_get_case(case_id: str):
    rec = get_case(case_id)
    if not rec:
        raise HTTPException(404, "case not found")
    return rec

# ---- Intake ----
@app.get("/omega/intake/questions")
def api_questions():
    return {"questions": get_question_set()}

@app.post("/omega/intake/submit")
def api_intake_submit(payload: IntakeSubmit):
    case = get_case(payload.case_id)
    if not case:
        raise HTTPException(404, "case not found")
    rec = submit_intake(payload)
    set_status(payload.case_id, __import__("omega_qcs.utils").utils.CaseStatus.INTAKE_DONE)
    return rec

@app.get("/omega/intake/{case_id}")
def api_intake_get(case_id: str):
    rec = fetch_intake(case_id)
    if not rec:
        raise HTTPException(404, "intake not found")
    return rec

# ---- Analyze ----
@app.post("/omega/analyze/{case_id}")
def api_analyze(case_id: str):
    try:
        res = analyze(case_id)
        return res.model_dump()
    except ValueError as e:
        raise HTTPException(400, str(e))

@app.get("/omega/analyze/{case_id}/result")
def api_analyze_get(case_id: str):
    rec = db_get("analyses", case_id)
    if not rec:
        raise HTTPException(404, "analysis not found")
    return rec

# ---- Report ----
@app.post("/omega/report/{case_id}/build")
def api_report_build(case_id: str, fmt: str = "both"):
    try:
        return build_report(ReportBuildRequest(case_id=case_id, format=fmt))
    except ValueError as e:
        raise HTTPException(400, str(e))

@app.get("/omega/report/{case_id}/md")
def api_report_md(case_id: str):
    rep = db_get("reports", case_id)
    if not rep or not rep.get("md_path"):
        raise HTTPException(404, "report not found")
    return FileResponse(rep["md_path"], media_type="text/markdown", filename=f"omega_report_{case_id}.md")

@app.get("/omega/report/{case_id}/pdf")
def api_report_pdf(case_id: str):
    rep = db_get("reports", case_id)
    if not rep or not rep.get("pdf_path"):
        raise HTTPException(404, "pdf not found")
    return FileResponse(rep["pdf_path"], media_type="application/pdf", filename=f"omega_report_{case_id}.pdf")

# ---- Session ----
@app.post("/omega/session/{case_id}/start")
def api_session_start(case_id: str, duration_min: int = 90):
    try:
        return start_session(SessionStart(case_id=case_id, duration_min=duration_min))
    except ValueError as e:
        raise HTTPException(400, str(e))

@app.post("/omega/session/{case_id}/note")
def api_session_note(case_id: str, step: str, note: str):
    try:
        return add_note(SessionNote(case_id=case_id, step=step, note=note))
    except ValueError as e:
        raise HTTPException(400, str(e))

@app.post("/omega/session/{case_id}/finalize")
def api_session_finalize(case_id: str, decisions_pending: list[str] = [], axis_criteria: list[str] = []):
    try:
        return finalize(SessionFinalize(case_id=case_id, decisions_pending=decisions_pending, axis_criteria=axis_criteria))
    except ValueError as e:
        raise HTTPException(400, str(e))

# ---- Meditation Micro ----
@app.get("/omega/micro/grounding")
def api_grounding(duration: int = 180):
    return grounding(duration)

@app.get("/omega/micro/reset")
def api_reset(duration: int = 240):
    return reset(duration)

# ---- Contract ----
@app.get("/omega/contract/pack")
def api_contract_pack():
    return build_contract_pack()


# ---- KPI / External View / Quality ----
@app.get("/omega/kpi/axis")
def api_kpi_axis():
    return as_dict(AXIS_INDEPENDENCE_KPI)

@app.get("/omega/external_view/simulate")
def api_external_view():
    return simulate_for_scheme()

@app.post("/omega/quality/check")
def api_quality_check(text: str):
    q = q_evaluate(text)
    return {"status": q.status, "findings": [f.__dict__ for f in q.findings], "text": findings_to_text(q)}

@app.get("/omega/axis/readiness/{case_id}")
def api_axis_readiness(case_id: str):
    sess = db_get("sessions", case_id)
    events = (sess or {}).get("events", [])
    return evaluate_independence(events)

# ---- Delivery ----
@app.post("/omega/deliver/{case_id}")
def api_deliver(case_id: str):
    try:
        return deliver(case_id)
    except ValueError as e:
        raise HTTPException(400, str(e))

@app.get("/omega/deliver/{case_id}/zip")
def api_deliver_zip(case_id: str):
    d = db_get("deliveries", case_id)
    if not d:
        raise HTTPException(404, "delivery not found")
    return FileResponse(d["zip_path"], media_type="application/zip", filename=f"omega_delivery_{case_id}.zip")
