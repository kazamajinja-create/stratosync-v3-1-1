from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Literal
import re

class ClientType(str, Enum):
    personal = "personal"
    corporate = "corporate"

class CaseStatus(str, Enum):
    DRAFT = "DRAFT"
    INTAKE_DONE = "INTAKE_DONE"
    ANALYZED = "ANALYZED"
    SESSION_READY = "SESSION_READY"
    DELIVERED = "DELIVERED"
    CLOSED = "CLOSED"

FORBIDDEN_CERTAINTY_PHRASES = [
    "必ず", "確実に", "100%", "絶対", "保証", "断言", "成功する", "失敗する"
]

def enforce_no_prediction(text: str) -> str:
    """
    Very lightweight safeguard:
    - remove/soften strong certainty language
    - ensure the output stays in "tendency/likelihood/structure" mode
    """
    if not text:
        return text
    out = text
    for p in FORBIDDEN_CERTAINTY_PHRASES:
        out = out.replace(p, "（断定回避）")
    # soften "will" like phrases in Japanese
    out = re.sub(r"〜?になる。", "〜になりやすい。", out)
    return out

def now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"
