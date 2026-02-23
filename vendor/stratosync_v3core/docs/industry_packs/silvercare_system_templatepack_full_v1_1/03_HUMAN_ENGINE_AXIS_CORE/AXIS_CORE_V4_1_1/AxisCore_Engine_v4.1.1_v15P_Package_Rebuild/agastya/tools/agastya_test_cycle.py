#!/usr/bin/env python3
# tools/agastya_test_cycle.py
# -*- coding: utf-8 -*-
"""
Agastya Quantum Test Cycle
- /api/agastya/quantum を章番号・テキストで反復テスト
Env:
  BASE_URL, SEED, TEXT, CH_START, CH_END
"""
from __future__ import annotations
import os, json, urllib.request

BASE = (os.getenv("BASE_URL") or "http://localhost:8000").rstrip("/")
SEED = os.getenv("SEED", "client_demo")
TEXT = os.getenv("TEXT", "あなたの魂の旅路は境界を超え、新しい出会いと知恵の扉を開きます。")
CH_START = int(os.getenv("CH_START", "1"))
CH_END   = int(os.getenv("CH_END", "5"))

def post_json(url: str, payload: dict):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        s = r.read().decode("utf-8", errors="ignore")
        return json.loads(s)

def main():
    endpoint = f"{BASE}/api/agastya/quantum"
    rows = []
    for ch in range(CH_START, CH_END+1):
        payload={"seed":SEED, "chapter":ch, "text":TEXT}
        out = post_json(endpoint, payload)
        rows.append({"chapter": ch, "confidence": out["quantum"]["confidence"], "theme": out["gamma"]["theme"]})
        print(f"[ch{ch}] conf={out['quantum']['confidence']} theme={out['gamma']['theme']}")
    with open("agastya_cycle_result.json","w",encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print("saved: agastya_cycle_result.json")

if __name__ == "__main__":
    main()
