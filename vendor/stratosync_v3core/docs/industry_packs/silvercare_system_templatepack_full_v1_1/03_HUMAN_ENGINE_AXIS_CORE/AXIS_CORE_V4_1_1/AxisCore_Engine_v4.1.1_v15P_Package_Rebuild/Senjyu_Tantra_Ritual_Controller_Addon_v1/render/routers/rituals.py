# -*- coding: utf-8 -*-
"""FastAPI Router: Tantra Ritual Planner (Lite/Explicit with consent & age gate)
Mount path: /rituals
Depends on module: core.extend.Senjyu_Tantra_SexRitual_Extend_v1
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import os

# Import the module from .app
try:
    from core.extend.Senjyu_Tantra_SexRitual_Extend_v1.modules import plan_rituals
except Exception as e:
    raise RuntimeError("Tantra module not found. Place Senjyu_Tantra_SexRitual_Extend_v1 under .app/core/extend/") from e

router = APIRouter(prefix="/rituals", tags=["rituals"])

class PairCtx(BaseModel):
    adult_confirmed: bool = Field(..., description="18歳以上の自己申告（UIチェック）")
    mutual_consent: bool = Field(..., description="双方の明示的合意（UIチェック）")
    boundaries: list[str] = Field(default_factory=list, description="例: ['口使用可','手使用可','痛みNG']")
    health_flags: list[str] = Field(default_factory=list, description="医療・安全面の留意")
    goals: list[str] = Field(default_factory=list, description="例: ['チャクラ活性','信頼深化']")
    birth_yyyymmdd: str | None = Field(None, description="例: '19800622'")

class ScoresIn(BaseModel):
    overall: int = 75
    kundalini: int = 75
    scores: dict = Field(default_factory=dict)

class PlanIn(BaseModel):
    pair_context: PairCtx
    scores: ScoresIn
    mode: str = Field("lite", description="lite|explicit")

@router.post("/plan")
def plan(payload: PlanIn):
    # 管理者スイッチ（Renderの環境変数で設定）
    explicit_enabled = os.getenv("EXPLICIT_RITUALS_ENABLED","false").lower() in ("1","true","yes","on")
    req_mode = payload.mode.lower()
    # 明示的に explicit 要求だが、管理側がOFFなら警告つきで Lite に矯正
    if req_mode == "explicit" and not explicit_enabled:
        req_mode = "lite"

    try:
        result = plan_rituals(
            payload.pair_context.model_dump(),
            payload.scores.model_dump(),
            {"mode": req_mode, "lang": "ja"}
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ritual planning failed: {e}")
    return result
