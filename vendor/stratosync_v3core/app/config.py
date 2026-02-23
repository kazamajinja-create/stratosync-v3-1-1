import os
from pydantic import BaseModel

class Settings(BaseModel):
    # v3.0.0 adds SDL (Surface Dominance) + ΩCL (Combinatorial) on top of RCL.
    VERSION: str = "3.0.0"
    AUDIT_LOG_PATH: str = os.getenv("AUDIT_LOG_PATH", "data/audit_log.jsonl")
    STATE_DB_PATH: str = os.getenv("STATE_DB_PATH", "data/state_db.json")
    ADMIN_TOKEN: str = os.getenv("ADMIN_TOKEN", "CHANGE_ME")

settings = Settings()
