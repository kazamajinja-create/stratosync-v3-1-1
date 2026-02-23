from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Dict
import os, json
from engine.scoring import score_all

app = FastAPI(title="QCS Dental Plugin API", version="1.0")

BASE = os.path.dirname(os.path.dirname(__file__))
CONFIG_PATH = os.path.join(BASE, "configs", "weights.v1.json")

class Intake(BaseModel):
    clinic_profile: Dict[str, Any]
    kpis: Dict[str, Any]

@app.post("/score")
def score(intake: Intake):
    payload = intake.model_dump()
    result = score_all(payload, CONFIG_PATH)
    return result
