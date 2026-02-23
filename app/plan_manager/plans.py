from dataclasses import dataclass
from app.config import settings

@dataclass(frozen=True)
class CompanyPlan:
    key: str
    label: str
    api_access: bool
    v3_full: bool
    report_pack: str  # standardized/full

PROFESSIONAL = CompanyPlan(
    key="professional",
    label="Professional",
    api_access=False,
    v3_full=False,   # 7 items only
    report_pack="standardized",
)

ENTERPRISE = CompanyPlan(
    key="enterprise",
    label="Enterprise",
    api_access=True,
    v3_full=True,
    report_pack="full",
)

PLAN_BY_KEY = {
    PROFESSIONAL.key: PROFESSIONAL,
    ENTERPRISE.key: ENTERPRISE,
}

def plan_from_key(key: str) -> CompanyPlan:
    return PLAN_BY_KEY.get(key, PROFESSIONAL)
