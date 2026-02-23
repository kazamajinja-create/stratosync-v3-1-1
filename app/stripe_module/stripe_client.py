from app.config import settings

def stripe_enabled() -> bool:
    return bool(settings.STRIPE_SECRET_KEY)
