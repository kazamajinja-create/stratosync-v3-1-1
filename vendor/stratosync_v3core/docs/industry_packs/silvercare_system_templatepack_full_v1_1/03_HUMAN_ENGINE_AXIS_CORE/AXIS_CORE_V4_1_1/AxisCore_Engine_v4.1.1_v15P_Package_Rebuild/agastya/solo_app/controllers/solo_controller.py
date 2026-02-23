from fastapi import APIRouter
from pydantic import BaseModel
from engine.senjyu_light_quantum import run_pipeline
from runtime.simple_renderer import render_text
router = APIRouter()
class Input(BaseModel):
    client_code: str
    dob: str
    tob: str | None = None
    pob: str | None = None
    addr: str | None = None
    plan: str = "C"
@router.post("/report")
def report(data: Input):
    layers = run_pipeline(data.model_dump())
    text = render_text(layers, plan=data.plan)
    return {"ok": True, "plan": data.plan, "preview": text[:500], "chars": len(text)}
