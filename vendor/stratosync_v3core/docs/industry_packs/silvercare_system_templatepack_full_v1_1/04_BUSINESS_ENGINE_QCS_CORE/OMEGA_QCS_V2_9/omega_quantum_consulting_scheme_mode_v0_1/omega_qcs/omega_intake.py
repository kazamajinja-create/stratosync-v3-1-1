from __future__ import annotations
from typing import Dict, Any, List
from .models import IntakeSubmit
from .storage import put, get
from .utils import now_iso

DEFAULT_QUESTION_SET = [
    "今回のテーマ（1つ）を一文で。",
    "現状の事実（数字/制約/期限/役割）。",
    "選択肢A/B/やらない の3つがあるとしたら？",
    "何を守りたいか（価値/信用/人/資金/時間）。",
    "許容できる損失はどこまでか。",
]

def get_question_set() -> List[str]:
    return DEFAULT_QUESTION_SET

def submit_intake(payload: IntakeSubmit) -> Dict[str, Any]:
    record = payload.model_dump()
    record["submitted_at"] = now_iso()
    put("intakes", payload.case_id, record)
    return record

def fetch_intake(case_id: str):
    return get("intakes", case_id)
