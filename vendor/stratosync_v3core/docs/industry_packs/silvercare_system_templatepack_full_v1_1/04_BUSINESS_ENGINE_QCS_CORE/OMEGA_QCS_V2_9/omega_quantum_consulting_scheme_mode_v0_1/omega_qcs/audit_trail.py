from __future__ import annotations
import json, hashlib, datetime
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

@dataclass
class AuditEvent:
    ts_utc: str
    engine_version: str
    input_hash: str
    output_hash: str
    metadata: Dict[str, Any]

def _sha256_json(obj: Any) -> str:
    b = json.dumps(obj, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(b).hexdigest()

class AuditTrailLogger:
    def __init__(self, log_path: str | Path):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, engine_version: str, inputs: Dict[str, Any], outputs: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> AuditEvent:
        metadata = metadata or {}
        ts = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
        ih = _sha256_json(inputs)
        oh = _sha256_json(outputs)
        ev = AuditEvent(ts, engine_version, ih, oh, metadata)
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(ev.__dict__, ensure_ascii=False) + "\n")
        return ev
