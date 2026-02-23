from __future__ import annotations
import json, os
from engine.scoring import score_all

BASE = os.path.dirname(os.path.dirname(__file__))
config_path = os.path.join(BASE, "configs", "weights.v1.json")
sample_path = os.path.join(BASE, "samples", "sample_clinic.json")
out_dir = os.path.join(BASE, "outputs")
os.makedirs(out_dir, exist_ok=True)

with open(sample_path, "r", encoding="utf-8") as f:
    payload = json.load(f)

result = score_all(payload, config_path)

with open(os.path.join(out_dir, "sample_scores.json"), "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

# simple report rendering
template_path = os.path.join(BASE, "reports", "template_report.md")
with open(template_path, "r", encoding="utf-8") as f:
    tpl = f.read()

rep = tpl.format(
    clinic_name=result["clinic"]["clinic_name"],
    region=result["clinic"]["region"],
    period_start=result["clinic"]["period_start"],
    period_end=result["clinic"]["period_end"],
    global_score=result["scores"]["GLOBAL"]["score_0_100"],
    global_grade=result["scores"]["GLOBAL"]["grade"],
    drs=result["scores"]["DRS"]["score_0_100"],
    drs_grade=result["scores"]["DRS"]["grade"],
    ddi=result["scores"]["DDI"]["score_0_100"],
    ddi_grade=result["scores"]["DDI"]["grade"],
    ders=result["scores"]["DeRS"]["score_0_100"],
    ders_grade=result["scores"]["DeRS"]["grade"],
    sci=result["scores"]["SCI"]["score_0_100"],
    sci_grade=result["scores"]["SCI"]["grade"],
)

with open(os.path.join(out_dir, "sample_report.md"), "w", encoding="utf-8") as f:
    f.write(rep)

print("Generated:", os.path.join(out_dir, "sample_scores.json"))
print("Generated:", os.path.join(out_dir, "sample_report.md"))
