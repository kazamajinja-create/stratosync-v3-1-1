from __future__ import annotations
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
from .kernel import guard_text, load_policy

class Handler(BaseHTTPRequestHandler):
    policy = None

    def _send(self, code: int, payload: dict):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        path = urlparse(self.path).path
        if path not in ("/guard", "/api/guard"):
            return self._send(404, {"error": "not_found", "path": path})
        length = int(self.headers.get("Content-Length", "0") or "0")
        raw = self.rfile.read(length) if length > 0 else b"{}"
        try:
            data = json.loads(raw.decode("utf-8"))
        except Exception:
            return self._send(400, {"error": "invalid_json"})

        text = data.get("text", "") or ""
        res = guard_text(text, self.policy)
        out = {
            "ok": res.ok,
            "level": res.level,
            "flags": [{"name": f.name, "score": f.score, "evidence": f.evidence} for f in res.flags],
            "next_step": res.next_step,
        }
        return self._send(200, out)

def run(host: str="0.0.0.0", port: int=8801, policy_path: str | None=None):
    Handler.policy = load_policy(policy_path)
    httpd = HTTPServer((host, port), Handler)
    print(f"[kabbalah_tree_kernel] listening on http://{host}:{port}  (POST /guard)")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
