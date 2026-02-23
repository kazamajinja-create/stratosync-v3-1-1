from __future__ import annotations
from typing import Dict, Any
from .utils import now_iso

DB: Dict[str, Dict[str, Any]] = {
    "cases": {},
    "intakes": {},
    "analyses": {},
    "reports": {},
    "sessions": {},
    "deliveries": {},
}

def put(table: str, key: str, value: Any) -> None:
    DB[table][key] = value

def get(table: str, key: str):
    return DB[table].get(key)

def all_items(table: str):
    return list(DB[table].values())
