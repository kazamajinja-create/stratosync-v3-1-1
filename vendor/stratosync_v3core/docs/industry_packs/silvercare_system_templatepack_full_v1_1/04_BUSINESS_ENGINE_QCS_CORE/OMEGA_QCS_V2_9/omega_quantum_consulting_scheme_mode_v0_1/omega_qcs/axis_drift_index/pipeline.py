from __future__ import annotations
import uuid
from datetime import datetime, timezone
from .models import AssessmentInput, AssessmentResult, Meta, FeaturePack
from .features import extract_features_basic
from .scoring import compute_scores
from .classify import build_classification
from .report import build_report

def run_assessment(inp: AssessmentInput) -> AssessmentResult:
    inp.validate()

    features: FeaturePack = extract_features_basic(inp.text)
    scores = compute_scores(inp.quant.answers)

    # Simple rationale (replace with LLM narration using evidence in production)
    rationale = (
        f"総合スコア{scores.total}/100。"
        f"中核固定度CF={scores.core_fixity}/20、"
        f"市場反応依存(逆点)MD={scores.market_dependency_stability}/20、"
        f"横展開(逆点)HS={scores.horizontal_spread_stability}/20、"
        f"摩耗(逆点)EE={scores.energy_erosion_stability}/20、"
        f"軸整合AC={scores.axis_coherence}/20。"
    )

    cls = build_classification(scores.total, rationale=rationale)
    report = build_report(inp.meta, scores, cls, features)

    return AssessmentResult(
        meta=inp.meta,
        features=features,
        scores=scores,
        classification=cls,
        report=report
    )

def new_meta(client_name: str = "", industry: str = "", language: str = "ja") -> Meta:
    return Meta(
        assessment_id=str(uuid.uuid4()),
        created_at=datetime.now(timezone.utc).isoformat(),
        version="1.0.0",
        language=language,  # type: ignore
        client={"name": client_name, "industry": industry}
    )
