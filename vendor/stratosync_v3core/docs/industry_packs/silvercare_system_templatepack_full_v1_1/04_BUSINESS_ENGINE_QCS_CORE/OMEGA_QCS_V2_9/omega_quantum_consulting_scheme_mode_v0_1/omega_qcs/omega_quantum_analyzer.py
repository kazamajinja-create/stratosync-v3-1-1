from __future__ import annotations
from typing import Dict, Any, List
from .storage import get, put
from .models import AnalysisResult
from .utils import enforce_no_prediction, CaseStatus
from .omega_case_registry import set_status

from .language_business import business_lines
from .qway_adapter import suggest_ring_focus
from .agastya_adapter import quantum_observe, gamma_language_observe, epsilon_causality, helios_synthesize
from .voynich_adapter import symbolic_overlay
from .vedanta_adapter import vedanta_lens

def _split_sentences(text: str) -> List[str]:
    parts: List[str] = []
    for p in text.replace("\n", "。").split("。"):
        p = p.strip()
        if p:
            parts.append(p)
    return parts[:12]

def analyze(case_id: str) -> AnalysisResult:
    """
    Business-edition analyzer:
    - Produces structural decision material (no prediction / no recommendation / no decision delegation)
    - Adds optional enrichers (Q-WAY rings, Agastya meta, Voynich symbolic overlay, Veda lens)
    """
    case = get("cases", case_id)
    intake = get("intakes", case_id)
    if not case or not intake:
        raise ValueError("case or intake not found")

    premises: List[str] = []
    premises += [f"テーマ: {case['theme']}"]
    c = (intake.get("constraints") or {})
    for k, v in c.items():
        if v:
            premises.append(f"制約({k}): {v}")
    if intake.get("stakeholders"):
        premises.append(f"利害関係者: {intake['stakeholders']}")
    premises += _split_sentences(intake.get("background",""))[:6]

    options_explicit = intake.get("options_known") or []
    options_hidden = intake.get("avoid_options") or []
    if not options_explicit:
        options_explicit = ["現状を維持しながら小さく試す", "方針を切り替えて集中する"]
    if not options_hidden:
        options_hidden = ["撤退/縮小を選ぶ（言いづらい選択肢）"]

    do_nothing = "保留（期限を定め、追加情報を揃えてから判断）"

    tendencies: Dict[str, List[str]] = {}
    base_impacts = [
        "短期: 意思決定コストが下がる傾向があります。",
        "中期: 組織・関係性の調整負荷が増える傾向があります。",
        "留意点: 過去成功体験の延長のみで選ぶと、判断が歪む可能性があります。",
    ]
    for opt in options_explicit + options_hidden + [do_nothing]:
        tendencies[opt] = business_lines([enforce_no_prediction(x) for x in base_impacts])

    distortions = business_lines([
        "恐れ由来（失うことの過大評価が入りやすい）",
        "過去成功体験の固定（同じ打ち手に寄りやすい）",
        "役割圧力（期待に合わせて本音がズレやすい）",
    ])

    notes = business_lines([
        "本解析は未来予測・結果断定を行わず、「起こりやすさ」「構造的帰結」を扱います。",
        "レポートには結論・推奨を記載しません（意思決定責任を奪わないため）。",
        "意思決定・実行・結果責任はクライアント側に帰属します。",
    ])

    # ---- Enrichers (optional) ----
    qway = suggest_ring_focus(case.get("theme",""), c)

    # Agastya meta: use theme as seed, chapter as a stable small integer
    seed = (case.get("theme","") + "|" + (intake.get("success_definition") or "")).strip()
    chapter = (abs(hash(seed)) % 64) + 1
    quantum = quantum_observe(seed=seed, chapter=chapter)
    gamma = gamma_language_observe(text=intake.get("background","")[:200], seed=seed, chapter=chapter)
    events = [case.get("theme",""), intake.get("success_definition") or "守りたいもの"][:2]
    epsilon = epsilon_causality(events=[e for e in events if e], seed=seed, chapter=chapter)
    helios = helios_synthesize(gamma=gamma, epsilon=epsilon, quantum=quantum)
    agastya = {"seed_note": "deterministic meta (for structuring only)", "chapter": chapter, "quantum": quantum, "gamma": gamma, "epsilon": epsilon, "helios": helios}

    voynich = symbolic_overlay(case.get("theme",""))
    vedanta = vedanta_lens(intake.get("success_definition") or "本案件の成功定義")

    result = AnalysisResult(
        case_id=case_id,
        premises=premises,
        options_explicit=options_explicit,
        options_hidden=options_hidden,
        option_do_nothing=do_nothing,
        tendencies=tendencies,
        distortions=distortions,
        notes=notes,
        qway=qway,
        agastya=agastya,
        voynich=voynich,
        vedanta=vedanta,
    )

    put("analyses", case_id, result.model_dump())
    set_status(case_id, CaseStatus.ANALYZED)
    return result
