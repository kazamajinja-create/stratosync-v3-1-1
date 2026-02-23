#!/usr/bin/env python3
# Agastia_Dispatcher.py
import os, sys, json, argparse, subprocess, shlex, uuid, datetime
from pathlib import Path
ROOT = Path(__file__).resolve().parent
CORE = ROOT / "agastia_resonant_formatter_core.py"
PDF_DIR = ROOT / "PDF_4Layer_Renderers"
def run(cmd: str):
    print(f"[RUN] {cmd}")
    p = subprocess.run(shlex.split(cmd), capture_output=True, text=True)
    if p.returncode != 0:
        print(p.stdout)
        print(p.stderr, file=sys.stderr)
        raise SystemExit(f"Command failed: {cmd}")
    return p.stdout.strip()
def ensure_dirs(job_id: str):
    out_dir = ROOT / "out" / job_id
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir
def pick_plan_from_webhook(payload: dict) -> str:
    plan = payload.get("plan") or payload.get("lookup_key") or "premium"
    plan = plan.lower()
    if plan not in ("lite","standard","premium"):
        plan = "premium"
    return plan
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", required=True, choices=["subscription","session"])
    ap.add_argument("--payload")
    ap.add_argument("--plan")
    ap.add_argument("--birth")
    ap.add_argument("--latlon")
    ap.add_argument("--source_dir", default="../agastya_100_filed")
    ap.add_argument("--font", default=None)
    args = ap.parse_args()
    job_id = uuid.uuid4().hex[:12]
    out_dir = ensure_dirs(job_id)
    if args.mode == "subscription":
        if not args.payload or not os.path.exists(args.payload):
            raise SystemExit("subscriptionモードには --payload が必要です")
        payload = json.load(open(args.payload,"r",encoding="utf-8"))
        plan = pick_plan_from_webhook(payload)
        birth = payload.get("birth") or "1967-04-21T11:20"
        latlon = payload.get("latlon") or "37.91,139.04"
        user_name = payload.get("user_name","Guest")
    else:
        plan = (args.plan or "premium").lower()
        birth = args.birth or "1967-04-21T11:20"
        latlon = args.latlon or "37.91,139.04"
        user_name = "SessionUser"
    json_out = out_dir / f"agastia_4layers_{plan}_core.json"
    core_cmd = f'python3 "{CORE}" --dir "{args.source_dir}" --plan {plan} --birth "{birth}" --latlon "{latlon}" --out "{json_out}"'
    run(core_cmd)
    if plan == "lite":
        pdf_script = PDF_DIR / "pdf_lite.py"; pdf_name = out_dir / f"agastia_{plan.capitalize()}.pdf"
    elif plan == "standard":
        pdf_script = PDF_DIR / "pdf_standard.py"; pdf_name = out_dir / f"agastia_{plan.capitalize()}.pdf"
    else:
        pdf_script = PDF_DIR / "pdf_premium.py"; pdf_name = out_dir / f"agastia_{plan.capitalize()}.pdf"
    pdf_cmd = f'python3 "{pdf_script}" --json "{json_out}" --out "{pdf_name}"'
    if args.font: pdf_cmd += f' --font "{args.font}"'
    run(pdf_cmd)
    meta = {"jobId": job_id,"mode": args.mode,"plan": plan,"user": user_name,"birth": birth,"latlon": latlon,"json": str(json_out),"pdf": str(pdf_name),"createdAt": datetime.datetime.utcnow().isoformat()+"Z","status": "ok"}
    meta_path = out_dir / "meta.json"; json.dump(meta, open(meta_path,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps(meta, ensure_ascii=False))
if __name__ == "__main__":
    main()
