
import json, uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from .generator import assemble

app = FastAPI(title="Kuzuryu Kotodama v2 API")

class Request(BaseModel):
    intent: str = "宣言"
    place: str = "富士"
    heav: str = "火"
    earth: str = "水"
    god_hint: str | None = None

@app.post("/generate")
def generate(req: Request):
    chant = assemble(req.intent, req.place, req.heav, req.earth, req.god_hint)
    return {"chant": chant}

def run():
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    run()
