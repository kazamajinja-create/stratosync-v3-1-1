# csde/agastya_loader.py
# -*- coding: utf-8 -*-
from __future__ import annotations
import json, hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "data" / "agastya" / "H-3.7"

def _leaf_hash(seed: str, mod=10**8) -> int:
    h = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    return int(h[:8], 16) % mod

def load_dicts():
    with open(ROOT / "karma_leaf_dict.json", encoding="utf-8") as f:
        karma = json.load(f)
    with open(ROOT / "prophecy_leaf_dict.json", encoding="utf-8") as f:
        prophecy = json.load(f)
    with open(ROOT / "dharma_leaf_dict.json", encoding="utf-8") as f:
        dharma = json.load(f)
    return karma, prophecy, dharma

def read_agastya(soul_seed: str):
    leaf_id = _leaf_hash(soul_seed)
    karma, prophecy, dharma = load_dicts()
    k = next((x for x in karma if x.get("leaf_id")==leaf_id), None)
    p = prophecy[0] if prophecy else None
    d = dharma[0] if dharma else None
    return {"leaf_id": leaf_id, "karma": k or karma[0], "prophecy": p, "dharma": d}
