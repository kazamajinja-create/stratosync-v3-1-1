from __future__ import annotations
from typing import Dict, List
from .models import Report, Scores, Classification, Meta, FeaturePack

def _label_ja(label: str) -> str:
    return {
        "stable": "安定",
        "exploration": "探索",
        "mild_drift": "軽度迷走",
        "reaction_driven": "反応駆動"
    }.get(label, label)

def build_report(meta: Meta, scores: Scores, cls: Classification, features: FeaturePack) -> Report:
    """Build a minimal, production-safe report object (template-driven).

    In production, replace diagnosis/top causes with your two-stage LLM pipeline:
    1) extract -> structured JSON (features/evidence)
    2) narrate -> report sections
    """
    summary = (
        f"現在の状態：{_label_ja(cls.label)}（信頼度 {cls.confidence}）\n"
        f"総合スコア：{scores.total}/100\n"
        f"内訳：CF {scores.core_fixity}/20, MD(逆点) {scores.market_dependency_stability}/20, "
        f"HS(逆点) {scores.horizontal_spread_stability}/20, EE(逆点) {scores.energy_erosion_stability}/20, "
        f"AC {scores.axis_coherence}/20"
    )

    diagnosis = {
        "core_fixity": "中核の明文化・手順化・階層化を強化してください。",
        "market_dependency": "市場反応での即時変更を減らし、検証サイクルを固定してください。",
        "horizontal_spread": "横展開の増殖を止め、既存テーマの深化・階層化へ寄せてください。",
        "energy_erosion": "摩耗の兆候が強い場合、イベント頻度と表現強度を落として回復期間を設けてください。",
        "axis_coherence": "過去の理念/主張と現在の打ち出しが一致する形で軸を再定義してください。"
    }

    top3_causes = [
        {"cause": "中核定義が短文化されていない", "evidence_refs": ["T1_business_overview"], "impact": "商品と発信が拡散しやすくなる"},
        {"cause": "市場反応による即時ピボット", "evidence_refs": [e["source_ref"] for e in features.evidence[:2]] or [], "impact": "一貫性が落ち、疲弊しやすい"},
        {"cause": "横展開による整理不足", "evidence_refs": ["T2_offers"], "impact": "リピート構造が作れずイベント回転になる"}
    ]

    plan_30d = [
        {"week": 1, "actions": ["中核定義を1文で固定", "『何をしないか』を3つ書く"], "expected_outcome": "軸が固定される"},
        {"week": 2, "actions": ["提供プロセスをStep1-5で文書化", "初級/中級/上級の階層を作る"], "expected_outcome": "体系の可視化"},
        {"week": 3, "actions": ["商品を3つに絞る（入口/本編/上位）", "告知文を『軸→対象→成果→方法』順に統一"], "expected_outcome": "導線の安定"},
        {"week": 4, "actions": ["同一テーマで切り口を変えた投稿を3本", "反応ではなくKPIで検証"], "expected_outcome": "反応駆動から検証駆動へ"}
    ]

    kpi = [
        "申込率（LP→申込）",
        "継続率（リピート/継続購入）",
        "軸KPI：中核定義の一致率（投稿/商品説明の整合）",
        "迷走警戒：テーマ変更回数（30日）"
    ]

    taboos = [
        "反応が悪いだけでテーマを即変更する",
        "商品を増やして整理しないまま回転させる",
        "断定口調・煽りを強めて短期反応だけを追う"
    ]

    questions = [
        "あなたの中核価値を1文で言うと？（誰に何を戻す？）",
        "この30日で『反応が理由で変えたこと』は何？",
        "最も再現性が高い手順はどれ？Stepで書ける？",
        "入口商品から上位までの階層は作れる？最短の形は？",
        "あなたが『絶対にやらない』ことは何？"
    ]

    appendix = {
        "axis_integrity": None,
        "market_fit": None,
        "drift_pressure": None
    }

    return Report(
        summary=summary,
        diagnosis=diagnosis,
        top3_causes=top3_causes,
        plan_30d=plan_30d,
        kpi=kpi,
        taboos=taboos,
        questions_for_next_session=questions,
        appendix=appendix
    )

def render_report_text(meta: Meta, scores: Scores, cls: Classification, report: Report) -> str:
    # A4-ish plain text output (2-4 pages when printed)
    header = (
        f"AXIS Drift Index™ 診断レポート\n"
        f"作成日：{meta.created_at} / バージョン：{meta.version}\n"
        f"対象：{meta.client.get('name','(unknown)')}\n"
        f"{'-'*50}\n"
    )

    body = []
    body.append("1. サマリー\n" + report.summary + "\n")
    body.append("2. 判定の要点\n" + cls.rationale + "\n")
    body.append("3. 5軸診断\n" + "\n".join([f"- {k}: {v}" for k, v in report.diagnosis.items()]) + "\n")
    body.append("4. 迷走原因Top3\n" + "\n".join([f"{i+1}) {c['cause']}（影響：{c['impact']} / 根拠：{', '.join(c['evidence_refs'])}）" for i, c in enumerate(report.top3_causes)]) + "\n")
    body.append("5. 30日プラン\n" + "\n".join([f"Week{w['week']}: " + " / ".join(w['actions']) + f" → {w['expected_outcome']}" for w in report.plan_30d]) + "\n")
    body.append("6. KPI\n" + "\n".join([f"- {k}" for k in report.kpi]) + "\n")
    body.append("7. 禁忌\n" + "\n".join([f"- {t}" for t in report.taboos]) + "\n")
    body.append("8. 次回質問\n" + "\n".join([f"{i+1}. {q}" for i, q in enumerate(report.questions_for_next_session)]) + "\n")
    return header + "\n".join(body)
