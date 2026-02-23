import os
from pydantic import BaseModel

class Settings(BaseModel):
    ENV: str = os.getenv("ENV","development")
    API_KEY: str | None = os.getenv("API_KEY")
    ENABLE_BILLING: bool = os.getenv("ENABLE_BILLING","0") == "1"
    DATABASE_URL: str | None = os.getenv("DATABASE_URL")
    STRIPE_SECRET_KEY: str | None = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_WEBHOOK_SECRET: str | None = os.getenv("STRIPE_WEBHOOK_SECRET")
    PRICE_ID_PROFESSIONAL: str | None = os.getenv("PRICE_ID_PROFESSIONAL")
    PRICE_ID_ENTERPRISE: str | None = os.getenv("PRICE_ID_ENTERPRISE")

    # AXIS license is handled outside company plans; keep for admin display only.
    AXIS_LICENSE_JPY_EX_TAX: int = int(os.getenv("AXIS_LICENSE_JPY_EX_TAX","48900"))
    PRO_JPY_EX_TAX: int = int(os.getenv("PRO_JPY_EX_TAX","300000"))
    ENT_JPY_EX_TAX: int = int(os.getenv("ENT_JPY_EX_TAX","600000"))

settings = Settings()
