from __future__ import annotations
from pathlib import Path
from typing import Dict, Any
import datetime, json

def render_report_md(payload: Dict[str, Any]) -> str:
    dt = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    drift = payload.get("axis_drift")
    inj = payload.get("external_injection")

    drift_block = ""
    if drift is not None:
        drift_block = f"""

## 3.5 AXIS Drift Index (Optional)
```json
{json.dumps(drift, ensure_ascii=False, indent=2)}
```
"""

    inj_block = ""
    if inj is not None:
        top = inj.get("top_abs_impacts", [])
        inj_block = f"""

## 3.6 External Injection (M, C, R_ext) → 12 Variables (Internal Computation)
- strategy: {inj.get("strategy")}
- inputs: {json.dumps(inj.get("inputs", {}), ensure_ascii=False)}
- top_abs_impacts: {json.dumps(top, ensure_ascii=False)}

> 注意: 本セクションは外部環境が内部構造に与える増幅/減衰を整理するもので、予測保証ではありません。
"""

    return f"""# Ω Strategic Collision Report (Non-Decision)
- generated_utc: {dt}

## 1. Snapshot / Indices
```json
{json.dumps(payload.get("snapshot"), ensure_ascii=False, indent=2)}
```
```json
{json.dumps(payload.get("indices"), ensure_ascii=False, indent=2)}
```

## 2. Market Context
```json
{json.dumps(payload.get("market_context"), ensure_ascii=False, indent=2)}
```

## 3. Collision Outputs
```json
{json.dumps(payload.get("collision_outputs"), ensure_ascii=False, indent=2)}
```{drift_block}{inj_block}

## 4. Strategic Priority (Collision Points)
```json
{json.dumps(payload.get("strategic_priority"), ensure_ascii=False, indent=2)}
```

## 5. Notes
- 本資料は推奨・決定・成果保証を行いません。
- 投資助言・会計判断・税務判断・監査意見・法的助言を構成しません。
"""

def save_md(text: str, path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p

def save_pdf_from_md(md_text: str, path: str | Path) -> Path:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(str(p), pagesize=A4)
    width, height = A4
    y = height - 40
    for line in md_text.splitlines():
        if y < 40:
            c.showPage()
            y = height - 40
        c.drawString(40, y, (line[:120]))
        y -= 12
    c.save()
    return p
