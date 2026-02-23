"""AXIS Drift Index™ — Drift Detection Model (v1.0.0)

Modules:
  - schema: JSON schema and data contracts
  - scoring: scoring logic (stable score with inverse components)
  - classify: label classification thresholds
  - features: feature extraction interfaces (LLM/heuristics)
  - report: report template + renderer (A4 style)
  - cli: command-line entrypoints (optional)
"""

__version__ = "1.0.0"

from .models import AssessmentInput, AssessmentResult
from .scoring import compute_scores
from .classify import classify_total
from .report import render_report_text
