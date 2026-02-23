#!/usr/bin/env python3
"""
patch_meta_to_agastya.py
- Quickly patch JSON-like text files that contain engine/name/version metadata.
- Use when you want to update visible labels without renaming paths yet.
Usage:
  python3 patch_meta_to_agastya.py . --apply
"""
import argparse, os, json
from pathlib import Path

TARGET_HINTS = ("meta", "appraisal", "output", "report", "config")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    count = 0
    for p in root.rglob("*.json"):
        if not any(h in p.name for h in TARGET_HINTS): 
            continue
        try:
            s = p.read_text(encoding="utf-8")
        except Exception:
            continue
        if "Agastia" in s or "agastia" in s or "AGASTIA" in s:
            s2 = s.replace("Agastia","Agastya").replace("agastia","agastya").replace("AGASTIA","AGASTYA")
            if args.apply and s2 != s:
                p.write_text(s2, encoding="utf-8")
            print(f"[META] {p}")
            count += 1
    print(f"patched meta targets: {count} (mode={'APPLY' if args.apply else 'DRY'})")

if __name__ == "__main__":
    main()
