from __future__ import annotations
from typing import Dict, Any
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from .quality_guard import evaluate as q_evaluate, findings_to_text
from .kpi_profile_axis import AXIS_INDEPENDENCE_KPI, as_dict
from .external_view_simulator import simulate_for_scheme

from .storage import get, put
from .models import ReportBuildRequest
from .utils import CaseStatus
from .omega_case_registry import set_status

OUT_DIR = Path(__file__).resolve().parent.parent / "out"
OUT_DIR.mkdir(exist_ok=True)

def build_markdown(case_id: str) -> str:
    analysis = get("analyses", case_id)
    case = get("cases", case_id)
    intake = get("intakes", case_id)
    if not analysis or not case:
        raise ValueError("analysis or case not found")

    md = []
    md.append(f"# Ω量子ロジック解析レポート（法人向け / v0.3）\n")
    md.append(f"**Case ID**: {case_id}\n")
    md.append(f"**テーマ**: {case['theme']}\n")
    md.append("\n---\n")
    md.append("## 0. レポートの位置づけ（重要）\n")
    md.append("- 本レポートは、意思決定のための情報整理・構造可視化を目的とします。\n")
    md.append("- 未来予測・結果断定・推奨は行いません。\n")
    md.append("- 意思決定・実行・結果責任はクライアント側に帰属します。\n")

    md.append("\n## 1. 前提条件（Premises）\n")
    for p in analysis["premises"]:
        md.append(f"- {p}\n")

    md.append("\n## 2. 選択肢（Options）\n")
    md.append("### 2.1 明示的選択肢\n")
    for o in analysis["options_explicit"]:
        md.append(f"- {o}\n")
    md.append("\n### 2.2 隠れた選択肢（避けられがち）\n")
    for o in analysis["options_hidden"]:
        md.append(f"- {o}\n")
    md.append(f"\n### 2.3 やらない／保留\n- {analysis['option_do_nothing']}\n")

    md.append("\n## 3. 構造的傾向（短期 / 中期 / 副作用 / 説明責任）\n")
    for opt, impacts in analysis["tendencies"].items():
        md.append(f"### {opt}\n")
        for imp in impacts:
            md.append(f"- {imp}\n")
        md.append("\n")

    md.append("## 4. 判断を歪めやすい要因（Distortions）\n")
    for d in analysis["distortions"]:
        md.append(f"- {d}\n")

    # ---- Q-WAY rings (optional) ----
    if analysis.get("qway"):
        q = analysis["qway"]
        rs = q.get("ring_state", {})
        md.append("\n## 5. Q-WAY 16Ring（論点配置 / Ωモード）\n")
        md.append("- このセクションは「決めるため」ではなく、「論点の抜け漏れ防止」を目的とします。\n")
        md.append(f"- モード: {q.get('mode','omega')}\n")
        md.append(f"- オープン論点（open ring ids）: {rs.get('open',[])}\n")
        md.append(f"- 軽い収束（soft_closing ring ids）: {rs.get('soft_closing',[])}\n")
        md.append(f"- ポリシー: {q.get('policy')}\n")

    # ---- Agastya enrichers (optional) ----
    if analysis.get("agastya"):
        a = analysis["agastya"]
        md.append("\n## 6. Agastya 多層メタ（構造化補助）\n")
        md.append("- このセクションは、対話上の観点整理を補助するための“構造メタ”です（事実断定ではありません）。\n")
        md.append(f"- chapter: {a.get('chapter')}\n")
        helios = (a.get("helios") or {})
        md.append(f"- 統合サマリー: {helios.get('summary')}\n")
        cons = helios.get("considerations") or []
        if cons:
            md.append("### 検討観点（considerations）\n")
            for x in cons:
                md.append(f"- {x}\n")
        gamma = (a.get("gamma") or {})
        md.append("\n### 言語観測（Gamma）\n")
        md.append(f"- 極性: {gamma.get('polarity')}\n")
        md.append(f"- 時間軸: {gamma.get('tense')}\n")
        md.append(f"- 主題: {gamma.get('theme')}\n")
        md.append(f"- 記号: {gamma.get('symbols')}\n")

    # ---- Voynich overlay ----
    if analysis.get("voynich"):
        v = analysis["voynich"]
        md.append("\n## 7. Voynich オーバーレイ（問いのテンプレ）\n")
        md.append("- 本セクションは翻訳・真偽判定ではなく、議論の問いを生成するための枠です。\n")
        for p in v.get("prompts", []):
            md.append(f"- {p}\n")

    # ---- Veda lens ----
    if analysis.get("vedanta"):
        ve = analysis["vedanta"]
        md.append("\n## 8. Vedaレンズ（価値・目的の再記述）\n")
        md.append(f"- {ve.get('text')}\n")
        md.append(f"- ポリシー: {ve.get('policy')}\n")

    md.append("\n## 9. 業務上の留意点（Policy）\n")
    for n in analysis["notes"]:
        md.append(f"- {n}\n")

    md.append("\n---\n")
    md.append("（本レポートは意思決定の材料整理です。決断・実行・結果責任はクライアントに帰属します。）\n")
    return "".join(md)

def _pdf_wrap_text(c: canvas.Canvas, text: str, x: int, y: int, max_width: int, leading: int=14):
    for line in text.splitlines():
        if not line:
            y -= leading
            continue
        while len(line) > 70:
            c.drawString(x, y, line[:70])
            line = line[70:]
            y -= leading
        c.drawString(x, y, line)
        y -= leading
    return y

def build_pdf(case_id: str, md_text: str) -> Path:
    pdf_path = OUT_DIR / f"omega_report_{case_id}.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=A4)
    width, height = A4
    y = height - 48
    c.setFont("Helvetica", 12)
    y = _pdf_wrap_text(c, md_text, 48, y, int(width-96))
    c.showPage()
    c.save()
    return pdf_path

def build_report(req: ReportBuildRequest) -> Dict[str, Any]:
    md = build_markdown(req.case_id)
    md_path = OUT_DIR / f"omega_report_{req.case_id}.md"
    md_path.write_text(md, encoding="utf-8")

    pdf_path = None
    if req.format in ("pdf", "both"):
        pdf_path = build_pdf(req.case_id, md)

    record = {"case_id": req.case_id, "md_path": str(md_path), "pdf_path": str(pdf_path) if pdf_path else None}
    put("reports", req.case_id, record)
    set_status(req.case_id, CaseStatus.SESSION_READY)
    return record
