
from __future__ import annotations

import io
import json
import os
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, Response, RedirectResponse

from app.config import settings
from app.auto_bootstrap.registry import discover_industry_packs
from app.db.session import SessionLocal
from app.db.models import Company, Case, Analysis
from app.plan_manager.plans import plan_from_key
from app.core_engine.analyzer import run_analysis

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

router = APIRouter(tags=["demo-ui"])

DATA_REPORT_DIR = "data/reports"

def _require_key(request: Request) -> None:
    if not settings.API_KEY:
        return
    k = request.query_params.get("k")
    if k != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")

def _k_suffix(request: Request) -> str:
    if not settings.API_KEY:
        return ""
    k = request.query_params.get("k")
    if not k:
        return ""
    return f"?k={k}"

def _wrap(request: Request, title: str, body: str) -> str:
    suffix = _k_suffix(request)
    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <style>
    body{{font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Noto Sans JP", sans-serif; margin: 24px;}}
    header{{display:flex; gap:16px; align-items:baseline; margin-bottom:16px;}}
    a{{color:#0b57d0; text-decoration:none;}}
    a:hover{{text-decoration:underline;}}
    .card{{border:1px solid #ddd; border-radius:10px; padding:16px; margin: 12px 0;}}
    label{{display:block; margin: 10px 0 6px; font-weight:600;}}
    input, select, textarea{{width:100%; padding:10px; border:1px solid #ccc; border-radius:8px;}}
    textarea{{min-height: 120px;}}
    .row{{display:grid; grid-template-columns:1fr 1fr; gap:12px;}}
    @media (max-width: 820px){{ .row{{grid-template-columns:1fr;}} }}
    .muted{{color:#666;}}
    .btn{{display:inline-block; padding:10px 14px; border:1px solid #0b57d0; border-radius:8px; background:white; cursor:pointer;}}
    .btn:hover{{background:#f3f7ff;}}
    code{{background:#f6f8fa; padding:2px 6px; border-radius:6px;}}
  </style>
</head>
<body>
<header>
  <h2 style="margin:0;">STRATOSYNC Demo</h2>
  <nav class="muted">
    <a href="/demo{suffix}">Demo</a>
    &nbsp;|&nbsp;
    <a href="/admin/packs{suffix}">Templates</a>
    &nbsp;|&nbsp;
    <a href="/docs">API Docs</a>
  </nav>
</header>
{body}
</body>
</html>"""

def _pdf_bytes(title: str, payload: dict, result: dict) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    y = height - 48

    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "STRATOSYNC Demo Report")
    y -= 22
    c.setFont("Helvetica", 10)
    c.drawString(40, y, f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    y -= 18
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, title)
    y -= 22

    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, y, "Input Summary")
    y -= 14
    c.setFont("Helvetica", 9)

    def line(k, v):
        nonlocal y
        txt = f"{k}: {v}"
        c.drawString(44, y, txt[:120])
        y -= 12

    line("Company", payload.get("company_name"))
    line("Industry", payload.get("industry"))
    line("Revenue (JPY)", payload.get("revenue_jpy"))
    line("Employees", payload.get("employees"))
    line("Challenges", (payload.get("challenges") or "")[:200])

    y -= 8
    c.setFont("Helvetica-Bold", 10)

# Key scores
y -= 8
c.setFont("Helvetica-Bold", 10)
c.drawString(40, y, "Key Scores")
y -= 14
c.setFont("Helvetica", 9)

fusion = result.get("mode_fusion", {}) or {}
surface = result.get("omega_surface", {}) or {}
omega = result.get("omega_combination", {}) or {}

def sline(k, v):
    nonlocal y
    if y < 70:
        c.showPage()
        y = height - 48
        c.setFont("Helvetica", 9)
    c.drawString(44, y, f"{k}: {v}")
    y -= 12

sline("SOS (Strategic Output Score)", fusion.get("SOS", "n/a"))
sline("BI / HI / OI", f'{fusion.get("BI","n/a")} / {fusion.get("HI","n/a")} / {fusion.get("OI","n/a")}')
sline("SE (Surface Efficiency, normalized)", fusion.get("SE", "n/a"))
sline("OPI (ln(Omega), normalized)", fusion.get("OPI", "n/a"))
sline("Surface A / V / SE_raw", f'{surface.get("A_surface","n/a")} / {surface.get("V_volume","n/a")} / {surface.get("SE_surface_efficiency","n/a")}')
sline("Omega_pairs / n_effective", f'{omega.get("Omega_pairs","n/a")} / {omega.get("n_effective","n/a")}')

    c.drawString(40, y, "Analysis Result (JSON excerpt)")
    y -= 14
    c.setFont("Helvetica", 8)

    pretty = json.dumps(result, ensure_ascii=False, indent=2)
    # draw first ~120 lines to keep it safe
    for ln in pretty.splitlines()[:120]:
        if y < 60:
            c.showPage()
            y = height - 48
            c.setFont("Helvetica", 8)
        c.drawString(44, y, ln[:160])
        y -= 10

    c.showPage()
    c.save()
    return buf.getvalue()


@router.get("/demo", response_class=HTMLResponse, include_in_schema=False)
def demo_form(request: Request):
    _require_key(request)
    packs = discover_industry_packs()
    options = "\n".join([f'<option value="{p["industry_id"]}">{p["title"]}</option>' for p in packs]) or '<option value="generic">Generic</option>'
    suffix = _k_suffix(request)
    body = f"""
<div class="card">
  <h3>デモ入力 → PDF出力</h3>
  <p class="muted">最小UIです。<code>/docs</code> でも同じ処理が可能です。</p>
  <form action="/demo/run{suffix}" method="post">
    <label>会社名</label>
    <input name="company_name" placeholder="例）株式会社サンプル" required />
    <label>業態テンプレ</label>
    <select name="industry" required>
      {options}
    </select>
    <div class="row">
      <div>
        <label>売上（円）</label>
        <input name="revenue_jpy" type="number" min="0" placeholder="例）80000000" />
      </div>
      <div>
        <label>従業員数</label>
        <input name="employees" type="number" min="0" placeholder="例）12" />
      </div>
    </div>
    <label>主な課題（自由記述）</label>
    <textarea name="challenges" placeholder="例）採用が安定しない、現場負荷が高い、離職率が…"></textarea>
    <div style="margin-top:12px;">
      <button class="btn" type="submit">PDFを生成</button>
    </div>
  </form>
</div>
"""
    return HTMLResponse(_wrap(request, "Demo", body))


@router.post("/demo/run", include_in_schema=False)
def demo_run(
    request: Request,
    company_name: str = Form(...),
    industry: str = Form("generic"),
    revenue_jpy: Optional[int] = Form(None),
    employees: Optional[int] = Form(None),
    challenges: str = Form(""),
):
    _require_key(request)
    db = SessionLocal()
    try:
        # find or create a demo company for this name (non-billing)
        company = db.query(Company).filter(Company.name==company_name).one_or_none()
        if not company:
            company = Company(name=company_name, plan="professional", subscription_status="active")
            db.add(company); db.commit(); db.refresh(company)

        plan = plan_from_key(company.plan)
        payload = {
            "company_name": company_name,
            "industry": industry,
            "revenue_jpy": revenue_jpy,
            "employees": employees,
            "challenges": challenges,
            "title": f"Demo: {company_name}",
        }
        case = Case(company_id=company.id, industry=industry, title=payload["title"], input_payload=payload)
        db.add(case); db.commit(); db.refresh(case)

        result = run_analysis(payload, plan)
        an = Analysis(case_id=case.id, result=result)
        db.add(an); db.commit(); db.refresh(an)

        os.makedirs(DATA_REPORT_DIR, exist_ok=True)
        filename = f"demo_report_{case.id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.pdf"
        pdf = _pdf_bytes(payload["title"], payload, result)
        with open(os.path.join(DATA_REPORT_DIR, filename), "wb") as f:
            f.write(pdf)

        return Response(
            content=pdf,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    finally:
        db.close()
    c.drawString(40, y, "Analysis Result (JSON excerpt)")
    y -= 14
    c.setFont("Helvetica", 8)

    pretty = json.dumps(result, ensure_ascii=False, indent=2)
    # draw first ~120 lines to keep it safe
    for ln in pretty.splitlines()[:120]:
        if y < 60:
            c.showPage()
            y = height - 48
            c.setFont("Helvetica", 8)
        c.drawString(44, y, ln[:160])
        y -= 10

    c.showPage()
    c.save()
    return buf.getvalue()


@router.get("/demo", response_class=HTMLResponse, include_in_schema=False)
def demo_form(request: Request):
    _require_key(request)
    packs = discover_industry_packs()
    options = "\n".join([f'<option value="{p["industry_id"]}">{p["title"]}</option>' for p in packs]) or '<option value="generic">Generic</option>'
    suffix = _k_suffix(request)
    body = f"""
<div class="card">
  <h3>デモ入力 → PDF出力</h3>
  <p class="muted">最小UIです。<code>/docs</code> でも同じ処理が可能です。</p>
  <form action="/demo/run{suffix}" method="post">
    <label>会社名</label>
    <input name="company_name" placeholder="例）株式会社サンプル" required />
    <label>業態テンプレ</label>
    <select name="industry" required>
      {options}
    </select>
    <div class="row">
      <div>
        <label>売上（円）</label>
        <input name="revenue_jpy" type="number" min="0" placeholder="例）80000000" />
      </div>
      <div>
        <label>従業員数</label>
        <input name="employees" type="number" min="0" placeholder="例）12" />
      </div>
    </div>
    <label>主な課題（自由記述）</label>
    <textarea name="challenges" placeholder="例）採用が安定しない、現場負荷が高い、離職率が…"></textarea>
    <div style="margin-top:12px;">
      <button class="btn" type="submit">PDFを生成</button>
    </div>
  </form>
</div>
"""
    return HTMLResponse(_wrap(request, "Demo", body))


@router.post("/demo/run", include_in_schema=False)
def demo_run(
    request: Request,
    company_name: str = Form(...),
    industry: str = Form("generic"),
    revenue_jpy: Optional[int] = Form(None),
    employees: Optional[int] = Form(None),
    challenges: str = Form(""),
):
    _require_key(request)
    db = SessionLocal()
    try:
        # find or create a demo company for this name (non-billing)
        company = db.query(Company).filter(Company.name==company_name).one_or_none()
        if not company:
            company = Company(name=company_name, plan="professional", subscription_status="active")
            db.add(company); db.commit(); db.refresh(company)

        plan = plan_from_key(company.plan)
        payload = {
            "company_name": company_name,
            "industry": industry,
            "revenue_jpy": revenue_jpy,
            "employees": employees,
            "challenges": challenges,
            "title": f"Demo: {company_name}",
        }
        case = Case(company_id=company.id, industry=industry, title=payload["title"], input_payload=payload)
        db.add(case); db.commit(); db.refresh(case)

        result = run_analysis(payload, plan)
        an = Analysis(case_id=case.id, result=result)
        db.add(an); db.commit(); db.refresh(an)

        os.makedirs(DATA_REPORT_DIR, exist_ok=True)
        filename = f"demo_report_{case.id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.pdf"
        pdf = _pdf_bytes(payload["title"], payload, result)
        with open(os.path.join(DATA_REPORT_DIR, filename), "wb") as f:
            f.write(pdf)

        return Response(
            content=pdf,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    finally:
        db.close()
