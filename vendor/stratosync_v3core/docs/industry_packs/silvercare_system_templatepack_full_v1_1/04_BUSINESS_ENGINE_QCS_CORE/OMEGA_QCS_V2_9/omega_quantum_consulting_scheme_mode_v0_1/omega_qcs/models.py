from __future__ import annotations
from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field
from .utils import ClientType, CaseStatus

class Constraints(BaseModel):
    money: Optional[str] = None
    people: Optional[str] = None
    time: Optional[str] = None
    role: Optional[str] = None

class CaseCreate(BaseModel):
    client_type: ClientType = ClientType.corporate
    theme: str = Field(..., description="1セッション＝1テーマを推奨。できるだけ具体に。")
    notes: Optional[str] = None

class CaseRecord(BaseModel):
    case_id: str
    client_type: ClientType
    theme: str
    status: CaseStatus
    created_at: str
    updated_at: str
    notes: Optional[str] = None

class IntakeSubmit(BaseModel):
    case_id: str
    background: str = Field(..., description="現状・背景（できるだけ事実ベース）")
    constraints: Constraints = Constraints()
    stakeholders: Optional[str] = Field(None, description="利害関係者（任意）")
    options_known: Optional[List[str]] = Field(default=None, description="現時点で考えている選択肢（任意）")
    avoid_options: Optional[List[str]] = Field(default=None, description="無意識に避けている/言いづらい選択肢（任意）")
    success_definition: Optional[str] = Field(None, description="このテーマでの成功/守りたいもの（任意）")
    risk_tolerance: Optional[str] = Field(None, description="許容できる損失/リスク（任意）")

class AnalysisResult(BaseModel):
    case_id: str
    premises: List[str]
    options_explicit: List[str]
    options_hidden: List[str]
    option_do_nothing: str
    tendencies: Dict[str, List[str]]  # option -> impacts
    distortions: List[str]
    notes: List[str]

    # Optional enrichers (business edition)
    qway: Optional[Dict[str, Any]] = None
    agastya: Optional[Dict[str, Any]] = None
    voynich: Optional[Dict[str, Any]] = None
    vedanta: Optional[Dict[str, Any]] = None

class ReportBuildRequest(BaseModel):
    case_id: str
    format: Literal["md", "pdf", "both"] = "both"

class SessionStart(BaseModel):
    case_id: str
    duration_min: int = 90

class SessionNote(BaseModel):
    case_id: str
    step: Literal["READ", "APPLY", "DEEPEN", "AXIS", "FINAL"] = "READ"
    note: str

class SessionFinalize(BaseModel):
    case_id: str
    decisions_pending: List[str] = []
    axis_criteria: List[str] = []  # 守る/捨てる/責任 等
