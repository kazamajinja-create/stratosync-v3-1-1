from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.health import router as health_router
from app.api.v3 import router as v3_router
from app.api.admin_ui import router as admin_ui_router
from app.api.demo_ui import router as demo_ui_router
from app.auto_bootstrap.bootstrap import bootstrap
from app.config import settings

app = FastAPI(title="STRATOSYNC v3.1 Commercial No-Code", version="3.1.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def _startup():
    bootstrap()

app.include_router(health_router)
app.include_router(v3_router)
app.include_router(admin_ui_router)
app.include_router(demo_ui_router)

# Billing endpoints are only exposed when enabled.
# This keeps the "deploy-and-run" demo flow zero-config.
if settings.ENABLE_BILLING:
    # Lazy import to avoid import-time failures when billing is disabled.
    from app.stripe_module.billing import router as billing_router
    app.include_router(billing_router)
