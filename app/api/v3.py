from fastapi import APIRouter, Depends, HTTPException, Header
from app.auth import require_api_key
from app.db.session import SessionLocal
from app.db.models import Company, Case, Analysis
from app.plan_manager.plans import plan_from_key
from app.core_engine.analyzer import run_analysis
from app.config import settings

router = APIRouter(prefix="/v3", tags=["v3"])

def _get_company(db, company_id: int) -> Company:
    c = db.query(Company).filter(Company.id==company_id).one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail="Company not found")
    return c

@router.post("/analyze")
def analyze(company_id: int, payload: dict, x_api_key: str | None = Header(default=None), _: None = Depends(require_api_key)):
    db = SessionLocal()
    try:
        company = _get_company(db, company_id)
        if settings.ENABLE_BILLING and company.subscription_status != "active":
            raise HTTPException(status_code=402, detail="Subscription inactive")
        plan = plan_from_key(company.plan)
        if not plan.v3_full:
            # Professional does not expose v3 analyze; still allows analysis but limited.
            pass
        case = Case(company_id=company.id, industry=payload.get("industry","generic"), title=payload.get("title","Case"), input_payload=payload)
        db.add(case); db.commit(); db.refresh(case)
        result = run_analysis(payload, plan)
        an = Analysis(case_id=case.id, result=result)
        db.add(an); db.commit(); db.refresh(an)
        return {"case_id": case.id, "analysis_id": an.id, "result": result}
    finally:
        db.close()
