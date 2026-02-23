from __future__ import annotations
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import urllib.request

DEFAULT_TARGETS = [
    {"name": "kabbalah_tree_kernel", "url": "http://127.0.0.1:8801/guard"},
    {"name": "kabbalah_policy_lab", "url": "http://127.0.0.1:8802/health"},
    {"name": "axis_resonance_tree", "url": "http://127.0.0.1:8804/health"},
]


def _request(url: str, payload: dict | None=None, timeout: int=2):
    data=None
    headers={}
    method="GET"
    if payload is not None:
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"]="application/json; charset=utf-8"
        method="POST"
    req=urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.getcode()

class Handler(BaseHTTPRequestHandler):
    targets = None

    def _send(self, code: int, payload: dict):
        body=json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path=urlparse(self.path).path
        if path not in ("/health", "/status"):
            return self._send(404, {"error":"not_found","path":path})

        statuses=[]
        ok=True
        for t in self.targets:
            name=t["name"]
            url=t["url"]
            try:
                if url.endswith("/guard"):
                    code=_request(url, {"text":"ping"})
                else:
                    code=_request(url, None)
                up = (200 <= code < 300)
            except Exception:
                up=False
            statuses.append({"name": name, "url": url, "up": up})
            ok = ok and up
        return self._send(200, {"ok": ok, "modules": statuses})

def run(host: str="0.0.0.0", port: int=8803):
    Handler.targets = DEFAULT_TARGETS
    httpd=HTTPServer((host, port), Handler)
    print(f"[module_health] listening on http://{host}:{port}  (GET /health)")
    httpd.serve_forever()

if __name__=="__main__":
    run()
