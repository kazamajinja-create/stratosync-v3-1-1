# -*- coding: utf-8 -*-
"""Auto integrator
- Places the rituals router into your FastAPI app and auto-registers it.
Assumptions:
- Your project root has .app/render/main.py (or .app/main.py) acting as FastAPI entry.
- Routers live under .app/render/routers/ (or .app/routers/).
Run:
  python tools/auto_integrate_controller.py
"""
import sys, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # .../Senjyu_Tantra_Ritual_Controller_Addon_v1
APP = Path.cwd()  # expected to be project root where .app exists
APP_ROOT = APP / ".app"
CANDIDATE_MAIN = [
    APP_ROOT / "render" / "main.py",
    APP_ROOT / "main.py",
]
TARGET_ROUTERS = [
    APP_ROOT / "render" / "routers",
    APP_ROOT / "routers",
]

SRC_ROUTER = ROOT / "render" / "routers" / "rituals.py"

def insert_include_router(main_path: Path) -> bool:
    text = main_path.read_text(encoding="utf-8")
    import_line = "from routers import rituals as rituals_router"
    include_line = "app.include_router(rituals_router.router)"
    changed = False
    if import_line not in text:
        # naive inject after FastAPI app creation
        if "app = FastAPI(" in text:
            text = text.replace("app = FastAPI(", f"{import_line}\napp = FastAPI(")
            changed = True
    if include_line not in text:
        # append near the bottom
        text = text + f"\n\n# Auto-added by auto_integrate_controller.py\n{include_line}\n"
        changed = True
    if changed:
        backup = main_path.with_suffix(".bak")
        backup.write_text(main_path.read_text(encoding="utf-8"), encoding="utf-8")
        main_path.write_text(text, encoding="utf-8")
    return changed

def main():
    if not APP_ROOT.exists():
        print("[X] .app not found in current working directory.")
        sys.exit(1)

    # choose routers dir
    for tdir in TARGET_ROUTERS:
        try:
            tdir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SRC_ROUTER, tdir / "rituals.py")
            print(f"[OK] Copied rituals.py -> {tdir}")
            break
        except Exception as e:
            last_err = e
    else:
        print(f"[X] Failed to place router: {last_err}")
        sys.exit(2)

    # patch main.py
    patched = False
    for m in CANDIDATE_MAIN:
        if m.exists():
            if insert_include_router(m):
                print(f"[OK] Patched main.py -> {m}")
                patched = True
                break
    if not patched:
        print("[!] Could not find main.py to patch automatically. Please import & include the router manually:")
        print("    from routers import rituals as rituals_router")
        print("    app.include_router(rituals_router.router)")
        sys.exit(3)

    print("[DONE] Ritual controller integrated.")

if __name__ == "__main__":
    main()
