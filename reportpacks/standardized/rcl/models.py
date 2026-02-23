from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class Context(BaseModel):
    company_size: int = Field(ge=1)
    departments: int = Field(ge=1)
    decision_makers: int = Field(ge=1)
    locations: int = Field(ge=1)


class DegreesOfFreedom(BaseModel):
    strategy_options: int = Field(ge=1)
    affected_departments: int = Field(ge=0)
    uncertainty_index: float = Field(ge=0.0, le=1.0)
    change_scope: float = Field(ge=0.0, le=1.0)


class DataCoverage(BaseModel):
    financial: float = Field(ge=0.0, le=1.0)
    human: float = Field(ge=0.0, le=1.0)
    organization: float = Field(ge=0.0, le=1.0)
    market: float = Field(ge=0.0, le=1.0)


class KPIRecord(BaseModel):
    month: str
    revenue: Optional[float] = None
    profit: Optional[float] = None
    other: Dict[str, Any] = Field(default_factory=dict)


class Intervention(BaseModel):
    date: str
    type: str
    meta: Dict[str, Any] = Field(default_factory=dict)


class RCLRequest(BaseModel):
    case_id: str
    industry_template: str = Field(default="generic")
    context: Context
    degrees_of_freedom: DegreesOfFreedom
    data_coverage: DataCoverage
    kpi_timeseries: List[KPIRecord] = Field(default_factory=list)
    interventions: List[Intervention] = Field(default_factory=list)
    mode_outputs: Dict[str, Any] = Field(default_factory=dict)


class RCLResponse(BaseModel):
    case_id: str
    industry_template: str
    branch_explosion: Dict[str, Any]
    convergence: Dict[str, Any]
    twin_cause: Dict[str, Any]
    residual: Dict[str, Any]
    notes: List[str] = Field(default_factory=list)
