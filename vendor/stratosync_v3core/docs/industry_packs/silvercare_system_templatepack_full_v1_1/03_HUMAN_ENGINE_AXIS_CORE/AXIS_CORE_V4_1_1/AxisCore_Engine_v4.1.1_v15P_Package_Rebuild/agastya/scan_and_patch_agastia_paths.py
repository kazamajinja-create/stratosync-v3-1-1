#!/usr/bin/env python3
"""
scan_and_patch_agastia_paths.py
- Scans source tree for legacy 'agastia' occurrences in imports and string paths.
- Writes CSV report; with --apply, performs safe replacements with .bak backups.

Usage:
  python3 scan_and_patch_agastia_paths.py .                # dry-run & CSV
  python3 scan_and_patch_agastia_paths.py . --apply        # perform replacements
"""
import argparse, csv, re, shutil
from pathlib import Path

TEXT_EXTS = {".py",".json",".yml",".yaml",".ini",".cfg",".toml",".md",".txt",".sh",".js",".ts",".tsx"}
SKIP_DIRS = {".git","node_modules","__pycache__",".idea",".venv"}

PATTERNS = [
    (re.compile(r'(?m)^(\\s*from\\s+)agastia([\\w\\._]*)\\s+import\\s+'), r'\\1agastya\\2 import '),
    (re.compile(r'(?m)^(\\s*import\\s+)agastia([\\w\\._]*)'), r'\\1agastya\\2'),
    (re.compile(r'agastia_'), 'agastya_'),
    (re.compile(r'["\\\']agastia([\\w_\\-/]*)["\\\']'), r'"agastya\\1"'),
    (re.compile(r"['\\\"]Agastia Core\\b"), '"Agastya Core'),
]

def is_text(p: Path) -> bool:
    return p.suffix.lower() in TEXT_EXTS

def scan(root: Path):
    findings = []
    for base, dirs, files in os.walk(root):
        basep = Path(base)
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            p = basep / f
            if not is_text(p): continue
            try:
                s = p.read_text(encoding="utf-8")
            except Exception:
                continue
            if "agastia" in s or "Agastia" in s:
                findings.append(str(p))
    return sorted(set(findings))

def apply_changes(paths, apply=False):
    total = 0
    for p in paths:
        s = p.read_text(encoding="utf-8")
        new = s
        for rx, repl in PATTERNS:
            new = rx.sub(repl, new)
        if new != s:
            total += 1
            if apply:
                bak = p.with_suffix(p.suffix + ".bak")
                if not bak.exists():
                    try: shutil.copy2(p, bak)
                    except Exception: pass
                p.write_text(new, encoding="utf-8")
            print(f"[PATCH] {p}")
    print(f"files changed: {total}{' (APPLY)' if apply else ' (DRY)'}")

def main():
    import os
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    targets = []
    for p in root.rglob("*"):
        if p.is_file() and is_text(p):
            try:
                s = p.read_text(encoding="utf-8")
            except Exception:
                continue
            if "agastia" in s or "Agastia" in s:
                targets.append(p)
    targets = sorted(set(targets))
    # CSV report
    csvp = root / "agastya_path_audit.csv"
    with csvp.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["path"])
        for p in targets: w.writerow([str(p)])
    print(f"[REPORT] {csvp} ({len(targets)} files)")
    apply_changes(targets, apply=args.apply)

if __name__ == "__main__":
    main()
