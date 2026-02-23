import os
from fastapi import Header, HTTPException, Depends
from app.config import settings

def require_api_key(x_api_key: str | None = Header(default=None)):
    if not settings.API_KEY:
        return
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
