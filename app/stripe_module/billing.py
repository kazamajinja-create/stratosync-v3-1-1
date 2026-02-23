import os
from fastapi import APIRouter, HTTPException, Request
from app.config import settings
from app.db.session import SessionLocal
from app.db.models import Company, AuditLog
from app.plan_manager.plans import PROFESSIONAL, ENTERPRISE

router = APIRouter(prefix="/billing", tags=["billing"])

try:
    import stripe
except Exception:
    stripe = None

def _ensure_stripe():
    if stripe is None:
        raise HTTPException(status_code=500, detail="stripe package not installed")
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(status_code=400, detail="STRIPE_SECRET_KEY not set")
    stripe.api_key = settings.STRIPE_SECRET_KEY

@router.post("/create-checkout-session")
def create_checkout_session(plan_key: str, company_name: str):
    _ensure_stripe()
    if plan_key not in (PROFESSIONAL.key, ENTERPRISE.key):
        raise HTTPException(status_code=400, detail="Invalid plan_key")
    price_id = settings.PRICE_ID_PROFESSIONAL if plan_key == PROFESSIONAL.key else settings.PRICE_ID_ENTERPRISE
    if not price_id:
        raise HTTPException(status_code=400, detail="Price ID not configured for plan")
    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=os.getenv("CHECKOUT_SUCCESS_URL","https://example.com/success"),
        cancel_url=os.getenv("CHECKOUT_CANCEL_URL","https://example.com/cancel"),
        metadata={"company_name": company_name, "plan_key": plan_key},
    )
    return {"checkout_url": session.url, "id": session.id}

@router.post("/webhook")
async def webhook(request: Request):
    _ensure_stripe()
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    event = None
    if settings.STRIPE_WEBHOOK_SECRET:
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Webhook signature verification failed: {e}")
    else:
        # DEV fallback: accept unsigned events (not recommended in production)
        import json
        event = json.loads(payload.decode("utf-8"))

    evt_type = event["type"] if isinstance(event, dict) else event.type
    data = event["data"]["object"] if isinstance(event, dict) else event.data.object

    # Minimal: when subscription becomes active, upsert company by stripe customer + set plan.
    db = SessionLocal()
    try:
        db.add(AuditLog(event=evt_type, payload={"raw": data}))
        db.commit()
        if evt_type in ("checkout.session.completed","customer.subscription.created","customer.subscription.updated"):
            customer_id = data.get("customer") or data.get("customer_id")
            plan_key = None
            # Try to infer plan by price id
            items = (data.get("items") or {}).get("data") if isinstance(data, dict) else None
            if not items and data.get("lines") and data["lines"].get("data"):
                items = data["lines"]["data"]
            price_id = None
            if items and len(items)>0:
                price_id = items[0].get("price", {}).get("id") or items[0].get("price")
            if price_id == settings.PRICE_ID_PROFESSIONAL:
                plan_key = PROFESSIONAL.key
            elif price_id == settings.PRICE_ID_ENTERPRISE:
                plan_key = ENTERPRISE.key

            company_name = (data.get("metadata") or {}).get("company_name","Company")
            if customer_id and plan_key:
                c = db.query(Company).filter(Company.stripe_customer_id==customer_id).one_or_none()
                if not c:
                    c = Company(name=company_name, stripe_customer_id=customer_id)
                    db.add(c)
                c.plan = plan_key
                c.subscription_status = "active"
                db.commit()
    finally:
        db.close()
    return {"ok": True}
