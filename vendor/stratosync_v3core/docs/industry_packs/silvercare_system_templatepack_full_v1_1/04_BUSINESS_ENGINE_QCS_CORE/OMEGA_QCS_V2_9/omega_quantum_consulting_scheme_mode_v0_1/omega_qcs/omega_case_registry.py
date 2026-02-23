from __future__ import annotations
from typing import Dict, Any
import uuid
from .models import CaseCreate, CaseRecord
from .storage import put, get
from .utils import CaseStatus, now_iso

def create_case(payload: CaseCreate) -> CaseRecord:
    case_id = uuid.uuid4().hex[:12]
    now = now_iso()
    rec = CaseRecord(
        case_id=case_id,
        client_type=payload.client_type,
        theme=payload.theme.strip(),
        status=CaseStatus.DRAFT,
        created_at=now,
        updated_at=now,
        notes=payload.notes,
    )
    put("cases", case_id, rec.model_dump())
    return rec

def get_case(case_id: str):
    return get("cases", case_id)

def set_status(case_id: str, status: CaseStatus):
    rec = get("cases", case_id)
    if not rec:
        return None
    rec["status"] = status.value
    rec["updated_at"] = now_iso()
    put("cases", case_id, rec)
    return rec
