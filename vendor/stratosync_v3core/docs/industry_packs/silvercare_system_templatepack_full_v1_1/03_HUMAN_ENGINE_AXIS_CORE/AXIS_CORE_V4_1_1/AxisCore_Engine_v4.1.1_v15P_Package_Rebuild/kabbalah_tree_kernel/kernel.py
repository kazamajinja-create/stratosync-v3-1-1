from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple, Any
import json
import os

@dataclass
class Flag:
    name: str
    score: float
    evidence: List[str]

@dataclass
class GuardResult:
    ok: bool
    level: str  # "pass" | "reframe" | "hold"
    flags: List[Flag]
    next_step: Dict[str, Any]

def _score_hits(text: str, lexicon: Dict[str, List[str]], norm_divisor: int) -> Tuple[float, List[str]]:
    t = (text or "").lower()
    hits: List[str] = []
    for group, patterns in lexicon.items():
        for p in patterns:
            if p.lower() in t:
                hits.append(f"{group}:{p}")
    score = min(1.0, len(hits) / max(1, norm_divisor))
    return score, hits

def load_policy(policy_path: str | None = None) -> Dict[str, Any]:
    if policy_path is None:
        # default: ../policy.json (module root)
        here = os.path.dirname(os.path.abspath(__file__))
        policy_path = os.path.join(os.path.dirname(here), "policy.json")
    with open(policy_path, "r", encoding="utf-8") as f:
        return json.load(f)

def guard_text(text: str, policy: Dict[str, Any]) -> GuardResult:
    """
    Kabbalah Tree Kernel (non-religious, non-Ω) for AXIS:
      - CERTAINTY_AUTHORITY_STASIS  (Daat-stasis equivalent)
      - OVEREXPANSION_RESCUE_BUBBLE (Chesed equivalent)
      - PUNITIVE_JUSTICE_PURGE      (Gevurah equivalent)
    Output is always: pass / reframe / hold
    """
    flags: List[Flag] = []
    norm = int(policy.get("norm_divisor", 6))

    # certainty/auth stasis
    score, hits = _score_hits(text, policy["lexicon"]["certainty"], norm)
    if score >= policy["thresholds"]["certainty"]:
        flags.append(Flag("CERTAINTY_AUTHORITY_STASIS", score, hits))

    # overexpansion/rescue bubble
    score, hits = _score_hits(text, policy["lexicon"]["overexpansion"], norm)
    if score >= policy["thresholds"]["overexpansion"]:
        flags.append(Flag("OVEREXPANSION_RESCUE_BUBBLE", score, hits))

    # punitive justice purge
    score, hits = _score_hits(text, policy["lexicon"]["punitive"], norm)
    if score >= policy["thresholds"]["punitive"]:
        flags.append(Flag("PUNITIVE_JUSTICE_PURGE", score, hits))

    max_score = max([f.score for f in flags], default=0.0)
    if max_score >= policy["levels"]["hold_at"]:
        level = "hold"
    elif max_score >= policy["levels"]["reframe_at"]:
        level = "reframe"
    else:
        level = "pass"

    # UX: "診断"ではなく"調律"
    if level == "pass":
        next_step = {"action": "continue", "message": "次工程へ進めます。"}
        ok = True
    elif level == "reframe":
        next_step = {
            "action": "reframe",
            "message": "今は結論を固定せず、現実側の小タスクに落とします。",
            "task": {
                "type": "micro_task",
                "duration_min": 10,
                "prompt": "10分で生活側の1つだけ片付けてください（洗い物/返信/片付け等）。終えたら短文で報告。",
            },
        }
        ok = False
    else:
        next_step = {
            "action": "hold",
            "message": "安全のため、少し時間を置いてから再入力してください。",
            "cooldown_hours": int(policy.get("cooldown_hours", 24)),
        }
        ok = False

    return GuardResult(ok=ok, level=level, flags=flags, next_step=next_step)
