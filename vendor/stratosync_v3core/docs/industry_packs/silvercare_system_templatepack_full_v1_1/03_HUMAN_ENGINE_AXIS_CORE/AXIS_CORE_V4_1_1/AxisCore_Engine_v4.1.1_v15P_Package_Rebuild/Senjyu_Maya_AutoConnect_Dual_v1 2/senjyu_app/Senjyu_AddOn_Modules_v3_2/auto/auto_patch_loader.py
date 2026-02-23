
import importlib, threading, time

def _watch_and_patch(timeout_sec: int = 60, interval_sec: float = 1.0):
    """
    Polls for `app.main` import and attaches the Maya router once available.
    Non‑blocking: runs in a daemon thread.
    """
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        try:
            mod = importlib.import_module("app.main")
            app = getattr(mod, "app", None)
            if app is not None:
                maya = importlib.import_module("senjyu_app.Senjyu_AddOn_Modules_v3_2.api.maya_router")
                router = getattr(maya, "router", None)
                if router is not None:
                    app.include_router(router, prefix="/api")
                    print("[AutoPatch] Registered /api/maya/* after app import.")
                    return
        except Exception:
            pass
        time.sleep(interval_sec)
    print("[AutoPatch] Gave up waiting for app.main (timeout).")

# Fire and forget
threading.Thread(target=_watch_and_patch, kwargs={"timeout_sec": 120}, daemon=True).start()
