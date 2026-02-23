#!/usr/bin/env python3
"""
patch_folder_names_in_meta.py
- Patches legacy folder/archive/engine names in JSON/TXT/MD/YAML to Agastya variants.
- Creates .bak backups. Safe to run multiple times.
"""
from pathlib import Path
import re, shutil

# Customize here if必要
REPLACEMENTS = {
    "Agastia": "Agastya",
    "agastia": "agastya",
    "AGASTIA": "AGASTYA",
    "new update vr.zip": "Agastya_Update_vr.zip",
    "new update vr": "Agastya_Update_vr",
    "Agastia Core (Virtual)": "Agastya Core (Virtual)",
}

TEXT_EXTS = {".json",".txt",".md",".yaml",".yml"}

def main():
    root = Path(".").resolve()
    patched = 0
    for p in root.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in TEXT_EXTS:
            continue
        try:
            s = p.read_text(encoding="utf-8")
        except Exception:
            continue
        new = s
        for old, newstr in REPLACEMENTS.items():
            new = re.sub(re.escape(old), newstr, new)
        if new != s:
            bak = p.with_suffix(p.suffix + ".bak")
            if not bak.exists():
                try: shutil.copy2(p, bak)
                except Exception: pass
            p.write_text(new, encoding="utf-8")
            print(f"[UPDATED] {p}")
            patched += 1
    print(f"✅ meta patched files: {patched}")

if __name__ == "__main__":
    main()
