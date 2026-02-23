# render/routes/agastya_quantum_routes.py
# -*- coding: utf-8 -*-
from __future__ import annotations
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

from agastya.layers.Gamma_LanguageObserver import analyze as gamma_analyze
from agastya.layers.Epsilon_CausalityMatrix import infer as eps_infer
from agastya.layers.Helios_SynthesisEngine import synthesize
from agastya.layers.Agastya_QuantumLayer import observe as q_observe

router = APIRouter(prefix="/api/agastya", tags=["agastya-quantum"])

class Request(BaseModel):
    seed: str = Field(..., description="相談IDなど再現性のためのキー")
    chapter: int = Field(1, ge=1, le=100)
    text: str = Field(..., description="霊視文（葉文）")
    events: Optional[List[str]] = Field(default=None, description="因果候補（任意）")

@router.post("/quantum")
def agastya_quantum(req: Request):
    try:
        gamma = gamma_analyze(req.text, req.seed, req.chapter)
        events = req.events or [req.text[:12], req.text[12:24], req.text[24:36]]
        epsilon = eps_infer(events, req.seed, req.chapter)
        quantum = q_observe(req.seed, req.chapter)
        result = synthesize(gamma, epsilon, quantum)
        return {
            "ok": True,
            "seed": req.seed,
            "chapter": req.chapter,
            "gamma": gamma,
            "quantum": quantum,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
