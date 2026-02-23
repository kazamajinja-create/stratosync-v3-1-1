from __future__ import annotations
import argparse, json
from pathlib import Path
from .models import AssessmentInput, Meta, QuantAnswers, TextInputs, TextPost
from .pipeline import run_assessment
from .report import render_report_text

def main():
    p = argparse.ArgumentParser(description="AXIS Drift Index™ CLI")
    p.add_argument("--input", required=True, help="Path to input JSON (meta+inputs)")
    p.add_argument("--out", required=False, help="Path to write report text")
    args = p.parse_args()

    data = json.loads(Path(args.input).read_text(encoding="utf-8"))

    meta = Meta(**data["meta"])
    quant = QuantAnswers(answers=data["inputs"]["quant"])
    posts = [TextPost(**x) for x in data["inputs"]["text"]["T3_posts"]]
    text = TextInputs(
        T1_business_overview=data["inputs"]["text"]["T1_business_overview"],
        T2_offers=data["inputs"]["text"]["T2_offers"],
        T3_posts=posts,
        attachments=data["inputs"]["text"].get("attachments", []),
    )

    inp = AssessmentInput(meta=meta, quant=quant, text=text)
    res = run_assessment(inp)
    txt = render_report_text(res.meta, res.scores, res.classification, res.report)

    if args.out:
        Path(args.out).write_text(txt, encoding="utf-8")
    else:
        print(txt)

if __name__ == "__main__":
    main()
