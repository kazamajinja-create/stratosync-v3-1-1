from __future__ import annotations
from typing import Optional, Dict
from pydantic import BaseModel, Field

class Weights(BaseModel):
    wp: float = 0.4
    wc: float = 0.3
    we: float = 0.3

class EvaluateRequest(BaseModel):
    project_id: Optional[str] = Field(default=None, description="Project identifier (optional). If absent, evaluation is anonymous.")
    political_score: float = Field(ge=0.0, le=1.0)
    capital_score: float = Field(ge=0.0, le=1.0)
    execution_score: float = Field(ge=0.0, le=1.0)
    noise: float = Field(ge=0.0, le=1.0)
    weights: Optional[Weights] = None
    alpha: Optional[float] = Field(default=0.2, ge=0.0, le=5.0)

class OverrideRequest(BaseModel):
    project_id: str
    override_state: str = Field(pattern="^(GO|CONDITIONAL|FREEZE)$")
    reason: str
    expires_at: str  # ISO-8601
