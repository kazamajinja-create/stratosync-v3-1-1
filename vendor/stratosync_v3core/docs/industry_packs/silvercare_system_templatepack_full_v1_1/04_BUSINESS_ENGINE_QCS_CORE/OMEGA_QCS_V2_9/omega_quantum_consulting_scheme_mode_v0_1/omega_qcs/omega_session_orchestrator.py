from __future__ import annotations
from typing import Dict, Any, List, Literal
from .storage import get, put
from .models import SessionStart, SessionNote, SessionFinalize
from .utils import now_iso, CaseStatus
from .omega_case_registry import set_status

STEPS = ["READ", "APPLY", "DEEPEN", "AXIS", "FINAL"]

def start_session(payload: SessionStart) -> Dict[str, Any]:
    if not get("reports", payload.case_id):
        raise ValueError("report not built")
    rec = {
        "case_id": payload.case_id,
        "duration_min": payload.duration_min,
        "started_at": now_iso(),
        "step": "READ",
        "events": [],
        "notes": [],
    }
    put("sessions", payload.case_id, rec)
    return rec

def add_note(payload: SessionNote) -> Dict[str, Any]:
    sess = get("sessions", payload.case_id)
    if not sess:
        raise ValueError("session not started")
    if payload.step not in STEPS:
        raise ValueError("invalid step")
    event = {"ts": now_iso(), "step": payload.step, "note": payload.note}
    sess["events"].append(event)
    sess["step"] = payload.step
    put("sessions", payload.case_id, sess)
    return sess

def finalize(payload: SessionFinalize) -> Dict[str, Any]:
    sess = get("sessions", payload.case_id)
    analysis = get("analyses", payload.case_id)
    case = get("cases", payload.case_id)
    if not sess or not analysis or not case:
        raise ValueError("missing session/analysis/case")

    # lightweight summary
    summary_lines = []
    summary_lines.append(f"テーマ: {case['theme']}")
    if payload.axis_criteria:
        summary_lines.append("判断軸: " + " / ".join(payload.axis_criteria))
    if payload.decisions_pending:
        summary_lines.append("保留/追加判断: " + " / ".join(payload.decisions_pending))
    summary_lines.append("重要: 本スキームは結論提示ではなく、判断材料の構造化。決断はクライアント。")

    sess["finalized_at"] = now_iso()
    sess["step"] = "FINAL"
    sess["final_summary"] = "\n".join(summary_lines)
    sess["axis_criteria"] = payload.axis_criteria
    sess["decisions_pending"] = payload.decisions_pending
    put("sessions", payload.case_id, sess)
    return sess
