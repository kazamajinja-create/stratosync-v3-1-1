from __future__ import annotations
from typing import Dict, Any
from pathlib import Path
import zipfile
from .storage import get, put
from .utils import CaseStatus
from .omega_case_registry import set_status

OUT_DIR = Path(__file__).resolve().parent.parent / "out"
OUT_DIR.mkdir(exist_ok=True)

def deliver(case_id: str) -> Dict[str, Any]:
    report = get("reports", case_id)
    session = get("sessions", case_id)
    analysis = get("analyses", case_id)
    if not report or not analysis:
        raise ValueError("report/analysis not found")
    # allow delivery even if session not finalized (but include what exists)
    summary = (session or {}).get("final_summary") or "（セッション要約未確定）"

    summary_path = OUT_DIR / f"omega_summary_{case_id}.txt"
    summary_path.write_text(summary, encoding="utf-8")

    zip_path = OUT_DIR / f"omega_delivery_{case_id}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(report["md_path"], arcname=Path(report["md_path"]).name)
        if report.get("pdf_path"):
            z.write(report["pdf_path"], arcname=Path(report["pdf_path"]).name)
        z.write(summary_path, arcname=summary_path.name)

    rec = {"case_id": case_id, "zip_path": str(zip_path)}
    put("deliveries", case_id, rec)
    set_status(case_id, CaseStatus.DELIVERED)
    return rec
