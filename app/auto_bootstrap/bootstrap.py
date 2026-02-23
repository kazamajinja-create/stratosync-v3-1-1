import os

from app.db.init_db import init_db
from app.config import settings
from app.auto_bootstrap.registry import build_runtime_registry
from app.auto_bootstrap.template_installer import install_template_archives

def bootstrap():
    # Ensure local storage exists (sqlite fallback uses ./data/local.db)
    os.makedirs("data", exist_ok=True)

    # Optional: auto-install industry template packs dropped as archives.
    # Place *.zip files under industry_packs_inbox/ and they will be extracted
    # into industry_packs_runtime/<pack_id>/ at startup.
    install_template_archives()

    # Create tables and validate env
    init_db()

    # Build runtime registries for no-code template growth.
    # Dropping a new folder under industry_packs_runtime/<id>/ with manifest.json
    # will be discovered automatically on startup.
    build_runtime_registry()
    # Optional: validate Stripe config presence if billing enabled
    if settings.ENABLE_BILLING:
        missing=[]
        if not settings.STRIPE_SECRET_KEY: missing.append("STRIPE_SECRET_KEY")
        if not settings.PRICE_ID_PROFESSIONAL: missing.append("PRICE_ID_PROFESSIONAL")
        if not settings.PRICE_ID_ENTERPRISE: missing.append("PRICE_ID_ENTERPRISE")
        if missing:
            raise RuntimeError(f"Billing enabled but missing env vars: {', '.join(missing)}")
