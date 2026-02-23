from __future__ import annotations
import json, os
from typing import Any, Dict, Optional
from datetime import datetime

def _ensure_dir(path: str) -> None:
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)

def load_db(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(path: str, db: Dict[str, Any]) -> None:
    _ensure_dir(path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def upsert_project_state(path: str, project_id: str, evaluation: Dict[str, Any]) -> None:
    db = load_db(path)
    db[project_id] = evaluation
    save_db(path, db)

def get_project_state(path: str, project_id: str) -> Optional[Dict[str, Any]]:
    db = load_db(path)
    return db.get(project_id)
