from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SDLInputs(BaseModel):
    channels: float = Field(ge=0, default=3.0)
    frequency: float = Field(ge=0, default=2.0)
    quality: float = Field(ge=0, default=0.6)
    api_count: float = Field(ge=0, default=0.0)
    partners: float = Field(ge=0, default=0.0)
    sns_factor: float = Field(ge=0, default=0.4)
    brand_exposure: float = Field(ge=0, default=0.4)
    volume_proxy: Optional[float] = Field(default=None, ge=0)


class OmegaInputs(BaseModel):
    connections: float = Field(ge=0, default=5.0)
    cross_roles: float = Field(ge=0, default=2.0)
    info_flow: float = Field(ge=0, le=1, default=0.5)
    flexibility: float = Field(ge=0, le=1, default=0.5)


class V3AnalyzeRequest(BaseModel):
    """Unified v3.0 analysis request.

    This is designed to be *industry-template-first* and future-proof.
    - RCL uses the existing integrated case fields.
    - SDL/ΩCL can be provided explicitly or left default for demos.
    """

    case_id: str = Field(min_length=1)
    industry_template: str = Field(default="generic")

    # --- RCL fields (compatible with RCLRequest) ---
    degrees_of_freedom: int = Field(default=12, ge=1, le=500)
    data_coverage: float = Field(default=0.6, ge=0, le=1)
    kpi_timeseries: List[float] = Field(default_factory=list)
    interventions: List[Dict[str, Any]] = Field(default_factory=list)

    # optional: carry evaluate-style inputs if present (for board summary)
    political_score: Optional[float] = Field(default=None, ge=0, le=1)
    capital_score: Optional[float] = Field(default=None, ge=0, le=1)
    execution_score: Optional[float] = Field(default=None, ge=0, le=1)
    noise: Optional[float] = Field(default=None, ge=0, le=1)

    # --- new v3 layers ---
    sdl: SDLInputs = Field(default_factory=SDLInputs)
    omega: OmegaInputs = Field(default_factory=OmegaInputs)


class V3AnalyzeResponse(BaseModel):
    evaluation_id: str
    project_id: str
    version: str
    timestamp: str
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    audit: Dict[str, Any]
