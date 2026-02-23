#!/usr/bin/env python3
"""
rename_agastia_to_agastya.py
- Safely renames files/directories containing 'agastia' -> 'agastya' (depth-first)
- Replaces text contents (utf-8) 'agastia/Agastia/AGASTIA' to 'agastya/Agastya/AGASTYA'
- Skips common binary formats; creates .bak backups for edited files

Usage:
  python3 rename_agastia_to_agastya.py . --dry-run
  python3 rename_agastia_to_agastya.py . --apply
  python3 rename_agastia_to_agastya.py . --apply --no-rename  # edit contents only
"""
import argparse, os, shutil
from pathlib import Path

LOW,LOW_TO = "agastia","agastya"
CAP,CAP_TO = "Agastia","Agastya"
UP,UP_TO   = "AGASTIA","AGASTYA"

TEXT_EXTS = {".py",".json",".yml",".yaml",".md",".txt",".ini",".cfg",".toml",".sh",".js",".ts",".tsx",".css",".html",".xml",".csv"}
SKIP_EXTS = {".zip",".gz",".tar",".tgz",".rar",".7z",".pdf",".png",".jpg",".jpeg",".gif",".webp",".ttf",".otf",".woff",".woff2",".mo",".so",".dll",".dylib",".bin"}

def is_text(p: Path) -> bool:
    if p.suffix.lower() in SKIP_EXTS: return False
    if p.suffix.lower() in TEXT_EXTS: return True
    try:
        if p.stat().st_size > 3_000_000: return False
        with p.open("rb") as f: f.read(2048).decode("utf-8")
        return True
    except Exception: return False

def replace_contents(p: Path, dry: bool):
    try:
        s = p.read_text(encoding="utf-8")
    except Exception:
        return 0
    cnt = s.count(LOW)+s.count(CAP)+s.count(UP)
    s = s.replace(LOW,LOW_TO).replace(CAP,CAP_TO).replace(UP,UP_TO)
    if cnt and not dry:
        bak = p.with_suffix(p.suffix + ".bak")
        if not bak.exists():
            try: shutil.copy2(p, bak)
            except Exception: pass
        p.write_text(s, encoding="utf-8")
    return cnt

def rename_path(p: Path, dry: bool) -> bool:
    newname = p.name.replace(LOW,LOW_TO).replace(CAP,CAP_TO).replace(UP,UP_TO)
    if newname != p.name:
        target = p.with_name(newname)
        if not dry:
            try: p.rename(target)
            except Exception as e:
                print(f"[WARN] rename failed: {p} -> {target}: {e}")
                return False
        print(f"[RENAME] {p} -> {target}")
        return True
    return False

def walk_depth_first(root: Path):
    files, dirs = [], []
    for base, dnames, fnames in os.walk(root):
        base_p = Path(base)
        for f in fnames: files.append(base_p / f)
        for d in dnames: dirs.append(base_p / d)
    # rename dirs/files depth-first to avoid path issues
    dirs.sort(key=lambda p: len(p.as_posix()), reverse=True)
    return files + dirs

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", help="root directory to process")
    ap.add_argument("--dry-run", action="store_true", help="report only")
    ap.add_argument("--apply", action="store_true", help="write changes")
    ap.add_argument("--no-rename", action="store_true", help="do not rename paths")
    args = ap.parse_args()

    if args.dry_run and args.apply:
        print("[ERR] choose either --dry-run or --apply"); return
    if not (args.dry_run or args.apply):
        args.dry_run = True

    root = Path(args.root).resolve()
    total_edit = total_ren = 0

    for p in walk_depth_first(root):
        if p.is_file() and is_text(p):
            c = replace_contents(p, dry=not args.apply)
            if c: print(f"[EDIT]  {p} (+{c} repl)"); total_edit += c
        if not args.no-rename and (LOW in p.name or CAP in p.name or UP in p.name):
            if rename_path(p, dry=not args.apply): total_ren += 1

    print("\n=== SUMMARY ===")
    print(f"root: {root}")
    print(f"replacements in text: {total_edit}")
    print(f"paths renamed: {total_ren}")
    print(f"mode: {'APPLY' if args.apply else 'DRY-RUN'}")

if __name__ == "__main__":
    main()
