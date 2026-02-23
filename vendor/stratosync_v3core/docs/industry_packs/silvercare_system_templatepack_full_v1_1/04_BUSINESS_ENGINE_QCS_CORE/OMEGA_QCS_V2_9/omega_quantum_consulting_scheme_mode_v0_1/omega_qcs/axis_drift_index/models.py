from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, TypedDict

Label = Literal["stable", "exploration", "mild_drift", "reaction_driven"]

@dataclass
class Meta:
    assessment_id: str
    created_at: str  # ISO8601 datetime
    version: str = "1.0.0"
    language: Literal["ja", "en"] = "ja"
    client: Dict[str, Any] = field(default_factory=dict)

@dataclass
class QuantAnswers:
    # Q1..Q20, each 0..4
    answers: Dict[str, int]

    def validate(self) -> None:
        required = [f"Q{i}" for i in range(1, 21)]
        missing = [k for k in required if k not in self.answers]
        if missing:
            raise ValueError(f"Missing quant answers: {missing}")
        for k in required:
            v = self.answers[k]
            if not isinstance(v, int) or v < 0 or v > 4:
                raise ValueError(f"Invalid {k}: {v} (expected int 0..4)")

@dataclass
class TextPost:
    source_type: Literal["paste", "url"]
    content: str

@dataclass
class TextInputs:
    T1_business_overview: str
    T2_offers: str
    T3_posts: List[TextPost]
    attachments: List[Dict[str, Any]] = field(default_factory=list)

    def validate(self) -> None:
        if len(self.T1_business_overview) < 50:
            raise ValueError("T1_business_overview too short (min 50 chars).")
        if len(self.T2_offers) < 20:
            raise ValueError("T2_offers too short (min 20 chars).")
        if not (3 <= len(self.T3_posts) <= 10):
            raise ValueError("T3_posts must have 3..10 items.")
        for p in self.T3_posts:
            if len(p.content) < 10:
                raise ValueError("Each post content must be >=10 chars.")

@dataclass
class AssessmentInput:
    meta: Meta
    quant: QuantAnswers
    text: TextInputs

    def validate(self) -> None:
        self.quant.validate()
        self.text.validate()

class DerivedFeatures(TypedDict, total=False):
    core_statement_present: bool
    core_statement: str
    core_statement_clarity: int  # 0..4
    method_documented: bool
    process_steps_count: int
    has_level_design: bool
    offer_count: int
    offer_has_levels: bool
    theme_rotation_rate: int  # per 30 days (estimated)
    market_language_ratio: float  # 0..1
    cta_intensity: Literal["low", "mid", "high"]
    tone_shift: Literal["low", "mid", "high"]
    axis_keywords: List[str]

class EvidenceItem(TypedDict):
    field: str
    source_ref: str
    excerpt: str

@dataclass
class FeaturePack:
    derived: DerivedFeatures = field(default_factory=dict)
    evidence: List[EvidenceItem] = field(default_factory=list)

@dataclass
class Scores:
    core_fixity: int
    market_dependency_stability: int
    horizontal_spread_stability: int
    energy_erosion_stability: int
    axis_coherence: int
    total: int

    # raw (optional for debugging)
    market_dependency_raw: int = 0
    horizontal_spread_raw: int = 0
    energy_erosion_raw: int = 0

@dataclass
class Classification:
    label: Label
    confidence: float
    rationale: str

@dataclass
class Report:
    summary: str
    diagnosis: Dict[str, str]
    top3_causes: List[Dict[str, Any]]
    plan_30d: List[Dict[str, Any]]
    kpi: List[str]
    taboos: List[str]
    questions_for_next_session: List[str]
    appendix: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AssessmentResult:
    meta: Meta
    features: FeaturePack
    scores: Scores
    classification: Classification
    report: Report
