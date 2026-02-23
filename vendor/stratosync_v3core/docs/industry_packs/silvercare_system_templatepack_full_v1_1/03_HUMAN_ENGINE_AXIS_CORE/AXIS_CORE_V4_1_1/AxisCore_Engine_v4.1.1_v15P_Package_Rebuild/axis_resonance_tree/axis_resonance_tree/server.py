from __future__ import annotations
import json, os, time, uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import urllib.request

def _load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _append_jsonl(path: str, obj: dict):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

def _read_jsonl(path: str, limit: int=200) -> list[dict]:
    if not os.path.exists(path):
        return []
    out=[]
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line=line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                pass
    return out[-limit:]

def _try_guard(text: str, url: str="http://127.0.0.1:8801/guard") -> dict | None:
    """
    Optional: if kabbalah_tree_kernel is running, we use it to prevent
    authority/enlightenment/justice runaway in relay texts.
    If not reachable, we simply skip.
    """
    try:
        data=json.dumps({"text": text}, ensure_ascii=False).encode("utf-8")
        req=urllib.request.Request(url, data=data, headers={"Content-Type":"application/json; charset=utf-8"}, method="POST")
        with urllib.request.urlopen(req, timeout=1.2) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None

def _pick_task(cfg: dict, seed: str | None=None) -> dict:
    tasks=cfg.get("income_tasks", [])
    if not tasks:
        return {"id":"income_default","title":"今日の収入に近い一歩","minutes":10,"prompt":"10分で、収入に近い一歩（連絡/提案/整備）を1つ実行。"}
    if seed:
        idx = abs(hash(seed)) % len(tasks)
    else:
        idx = int(time.time()) % len(tasks)
    return tasks[idx]

def _pick_loop(cfg: dict, seed: str | None=None) -> dict:
    loops=cfg.get("practice_loops", [])
    if not loops:
        return {"id":"loop_default","title":"解析→タスク→報告","steps":["解析","タスク","報告"]}
    idx = abs(hash(seed)) % len(loops) if seed else (int(time.time()) % len(loops))
    return loops[idx]

def _pick_relay(cfg: dict, seed: str | None=None) -> dict:
    relays=cfg.get("relay_templates", [])
    if not relays:
        return {"id":"relay_default","title":"ミニ解析質問","template":"目的/障害/今日の最小行動を教えてください。"}
    idx = abs(hash(seed)) % len(relays) if seed else (int(time.time()) % len(relays))
    return relays[idx]

class Handler(BaseHTTPRequestHandler):
    cfg = None
    log_path = None

    def _send(self, code: int, payload: dict):
        body=json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path=urlparse(self.path).path
        if path=="/health":
            return self._send(200, {"ok": True, "module":"axis_resonance_tree"})
        if path=="/config":
            return self._send(200, self.cfg)
        if path=="/events":
            qs=parse_qs(urlparse(self.path).query)
            limit=int(qs.get("limit",[200])[0])
            return self._send(200, {"ok": True, "events": _read_jsonl(self.log_path, limit=limit)})
        return self._send(404, {"error":"not_found","path":path})

    def do_POST(self):
        path=urlparse(self.path).path
        length=int(self.headers.get("Content-Length","0") or "0")
        raw=self.rfile.read(length) if length>0 else b"{}"
        try:
            data=json.loads(raw.decode("utf-8"))
        except Exception:
            return self._send(400, {"error":"invalid_json"})

        now=int(time.time())
        if path=="/resonance/intake":
            # record resonance evidence (lightweight)
            event={
                "id": str(uuid.uuid4()),
                "ts": now,
                "type":"intake",
                "actor_id": data.get("actor_id"),      # analyst (AXIS member)
                "target_id": data.get("target_id"),    # third party
                "meta": data.get("meta", {}),
                "text": data.get("text",""),
            }
            _append_jsonl(self.log_path, event)
            return self._send(200, {"ok": True, "event_id": event["id"]})

        if path=="/resonance/next":
            seed = (data.get("target_id") or data.get("actor_id") or "") + "|" + (data.get("phase") or "")
            task=_pick_task(self.cfg, seed=seed)
            loop=_pick_loop(self.cfg, seed=seed)
            out={
                "ok": True,
                "focus":"income_increase",
                "task": task,
                "loop": loop,
                "message":"共鳴を『収入に近い一歩』へ落として、反復で安定化させます。",
            }
            # log suggestion
            _append_jsonl(self.log_path, {"id": str(uuid.uuid4()), "ts": now, "type":"next", "seed": seed, "out": out})
            return self._send(200, out)

        if path=="/resonance/relay":
            seed = (data.get("actor_id") or "") + "|" + (data.get("target_id") or "") + "|" + (data.get("context") or "")
            relay=_pick_relay(self.cfg, seed=seed)
            # Optional safety gate on the generated text itself (if kernel is up)
            guard=_try_guard(relay.get("template",""))
            if guard and guard.get("level") in ("reframe","hold"):
                # rewrite to a more grounded version (no authority/enlightenment cues)
                relay = {
                    "id": relay.get("id","relay_safe"),
                    "title": "安定ベース質問（安全版）",
                    "template": "収入を増やすために：①誰に ②何を ③いくらで ④今日の最小行動（10分）を、1行ずつ教えてください。こちらで整理して返します。",
                }
            out={"ok": True, "focus":"income_increase", "relay": relay}
            _append_jsonl(self.log_path, {"id": str(uuid.uuid4()), "ts": now, "type":"relay", "seed": seed, "out": out})
            return self._send(200, out)

        return self._send(404, {"error":"not_found","path":path})

def run(host: str="0.0.0.0", port: int=8804):
    here=os.path.dirname(os.path.abspath(__file__))
    cfg_path=os.path.join(os.path.dirname(here), "config.json")
    Handler.cfg=_load_json(cfg_path)
    Handler.log_path=os.path.join(os.path.dirname(here), "data", "events.jsonl")
    httpd=HTTPServer((host, port), Handler)
    print(f"[axis_resonance_tree] listening on http://{host}:{port}  (POST /resonance/intake|next|relay)")
    httpd.serve_forever()

if __name__=="__main__":
    run()
