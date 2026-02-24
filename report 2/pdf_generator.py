from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

from .textgen import executive_one_liner
from .actions import top3_actions

# Register Japanese font (CID)
pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))

@dataclass
class ReportData:
    company_name: str
    plan: str
    date_iso: str

    surface_axes: dict[str, float]
    SI: float
    IRI: float
    SE: float

    omega_index: float
    actual_links: int
    max_links: int

    decision_axes: dict[str, float]
    DAF: float
    market_risk: float
    adjusted_risk: float

    surface_power: float
    resilience: float

def _bar(c: canvas.Canvas, x: float, y: float, w: float, h: float, pct: float):
    # Outline
    c.rect(x, y, w, h, stroke=1, fill=0)
    fill_w = max(0.0, min(w, w * (pct/100.0)))
    c.rect(x, y, fill_w, h, stroke=0, fill=1)

def generate_pdf(path: str, data: ReportData) -> str:
    c = canvas.Canvas(path, pagesize=A4)
    c.setFont('HeiseiKakuGo-W5', 18)
    c.drawString(20*mm, 280*mm, "STRATOSYNC v3.1.1 Executive Report")
    c.setFont('HeiseiKakuGo-W5', 12)
    c.drawString(20*mm, 270*mm, f"企業名: {data.company_name}")
    c.drawString(20*mm, 262*mm, f"プラン: {data.plan}")
    c.drawString(20*mm, 254*mm, f"解析日: {data.date_iso}")
    c.setFont('HeiseiKakuGo-W5', 10)
    c.drawString(20*mm, 246*mm, "Ω-Surface Architecture™ — 境界面優位 × 組み合わせ爆発 × 意思決定増幅")

    # Page 1 summary scores
    c.setFont('HeiseiKakuGo-W5', 12)
    c.drawString(20*mm, 232*mm, "1. Executive Summary")
    one = executive_one_liner(data.surface_power, data.resilience, data.adjusted_risk, data.omega_index, data.SE)
    c.setFont('HeiseiKakuGo-W5', 10)
    c.drawString(20*mm, 224*mm, one)

    metrics = [
        ("Surface Power", data.surface_power),
        ("Resilience", data.resilience),
        ("Adjusted Risk", data.adjusted_risk),
        ("Ω Index", data.omega_index),
        ("Surface Efficiency", data.SE),
    ]
    y = 210*mm
    c.setFont('HeiseiKakuGo-W5', 10)
    for name, val in metrics:
        c.drawString(20*mm, y, f"{name}: {val:.1f}")
        _bar(c, 60*mm, y-3*mm, 120*mm, 5*mm, val)
        y -= 10*mm

    c.showPage()

    # Page 2 Surface
    c.setFont('HeiseiKakuGo-W5', 12)
    c.drawString(20*mm, 280*mm, "2. Surface Analysis（境界面解析）")
    c.setFont('HeiseiKakuGo-W5', 10)
    c.drawString(20*mm, 270*mm, f"SI: {data.SI:.1f} / IRI: {data.IRI:.1f} / SE: {data.SE:.1f}")
    y = 255*mm
    for k in ["CT","AL","PN","BE","DC"]:
        v = float(data.surface_axes.get(k, 0.0))
        c.drawString(20*mm, y, f"{k}: {v:.1f}")
        _bar(c, 40*mm, y-3*mm, 140*mm, 5*mm, v)
        y -= 10*mm

    c.showPage()

    # Page 3 Ω
    c.setFont('HeiseiKakuGo-W5', 12)
    c.drawString(20*mm, 280*mm, "3. Ω Organizational Dynamics（組織接続）")
    c.setFont('HeiseiKakuGo-W5', 10)
    c.drawString(20*mm, 270*mm, f"Ω Index: {data.omega_index:.1f}  (ActualLinks={data.actual_links} / MaxLinks={data.max_links})")
    _bar(c, 20*mm, 260*mm, 160*mm, 6*mm, data.omega_index)
    c.drawString(20*mm, 248*mm, f"サイロ指数（Silo Index）: {100.0-data.omega_index:.1f}")

    c.showPage()

    # Page 4 Decision
    c.setFont('HeiseiKakuGo-W5', 12)
    c.drawString(20*mm, 280*mm, "4. Decision Amplification（意思決定増幅）")
    c.setFont('HeiseiKakuGo-W5', 10)
    c.drawString(20*mm, 270*mm, f"DAF: {data.DAF:.2f} / MarketRisk: {data.market_risk:.1f} / AdjustedRisk: {data.adjusted_risk:.1f}")
    y = 255*mm
    for k in ["RA","BI","SV","SP"]:
        v = float(data.decision_axes.get(k, 0.0))
        c.drawString(20*mm, y, f"{k}: {v:.1f}")
        _bar(c, 40*mm, y-3*mm, 140*mm, 5*mm, v)
        y -= 10*mm

    c.showPage()

    # Page 5 Actions
    c.setFont('HeiseiKakuGo-W5', 12)
    c.drawString(20*mm, 280*mm, "5. Priority Actions（優先アクション 3項目）")
    acts = top3_actions(data.surface_axes, data.omega_index, data.DAF)
    c.setFont('HeiseiKakuGo-W5', 11)
    y = 265*mm
    for i,a in enumerate(acts, start=1):
        c.drawString(20*mm, y, f"{i}. {a}")
        y -= 12*mm

    c.setFont('HeiseiKakuGo-W5', 9)
    c.drawString(20*mm, 30*mm, "※本レポートは条件付き分岐の意思決定補助であり、最終判断は経営者に委ねられます。")
    c.save()
    return path
