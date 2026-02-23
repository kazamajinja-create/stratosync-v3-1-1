from __future__ import annotations
from dataclasses import asdict
from typing import List
import re
from .models import FeaturePack, EvidenceItem, TextInputs

MARKET_WORDS = [
    "稼ぐ", "売上", "集客", "マーケ", "広告", "LP", "申し込み", "収益", "単価",
    "フォロワー", "リール", "CTA", "セールス", "オファー"
]

def extract_features_basic(text: TextInputs) -> FeaturePack:
    """Baseline feature extraction without external LLMs.

    This is intentionally conservative: it provides helper signals and evidence
    pointers from the provided text inputs. Replace/augment with your LLM pipeline
    in production.
    """
    evidence: List[EvidenceItem] = []
    all_text = "\n".join([text.T1_business_overview, text.T2_offers] + [p.content for p in text.T3_posts])

    # core statement heuristic: first sentence of T1
    core_statement = re.split(r"[。.!?\n]", text.T1_business_overview.strip())[0].strip()
    core_present = len(core_statement) >= 10

    # market language ratio heuristic
    tokens = re.findall(r"\w+|[一-龥ぁ-んァ-ンー]+", all_text)
    market_hits = sum(1 for t in tokens for w in MARKET_WORDS if w in t)
    ratio = 0.0 if not tokens else min(1.0, market_hits / max(1, len(tokens)))

    # offer count heuristic: count bullets/lines
    offer_lines = [ln.strip() for ln in text.T2_offers.splitlines() if ln.strip()]
    offer_count = len(offer_lines)

    derived = {
        "core_statement_present": core_present,
        "core_statement": core_statement,
        "core_statement_clarity": 2 if core_present else 0,
        "method_documented": ("Step" in all_text or "手順" in all_text or "プロセス" in all_text),
        "process_steps_count": len(re.findall(r"Step\s*\d+", all_text)),
        "has_level_design": any(k in all_text for k in ["初級", "中級", "上級"]),
        "offer_count": offer_count,
        "offer_has_levels": any(k in text.T2_offers for k in ["初級", "中級", "上級"]),
        "theme_rotation_rate": 0,
        "market_language_ratio": float(round(ratio, 3)),
        "cta_intensity": "mid",
        "tone_shift": "mid",
        "axis_keywords": []
    }

    if core_present:
        evidence.append({"field": "core_statement", "source_ref": "T1_business_overview", "excerpt": core_statement[:350]})

    if market_hits > 0:
        # cite up to 2 posts where market words appear
        for idx, p in enumerate(text.T3_posts[:10]):
            if any(w in p.content for w in MARKET_WORDS):
                evidence.append({
                    "field": "market_language_ratio",
                    "source_ref": f"T3_posts[{idx}]",
                    "excerpt": p.content[:350]
                })
                if len([e for e in evidence if e["field"]=="market_language_ratio"]) >= 2:
                    break

    return FeaturePack(derived=derived, evidence=evidence)
