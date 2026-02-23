"""Runtime registry builder (no-code template growth).

Goal:
  - Allow adding new industry templates by dropping folders under
    `industry_packs_runtime/<industry_id>/`.
  - On startup, discover available packs and write a lightweight
    `industry_packs_runtime/registry.json` for UI/admin display.

This file is optional for engine correctness (discovery works without it),
but it makes operations and UI simpler, and keeps the product "no-code".
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List


def _safe_read_json(path: str) -> Dict[str, Any] | None:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def discover_industry_packs(base_dir: str = "industry_packs_runtime") -> List[Dict[str, Any]]:
    packs: List[Dict[str, Any]] = []
    if not os.path.isdir(base_dir):
        return packs

    for name in sorted(os.listdir(base_dir)):
        root = os.path.join(base_dir, name)
        if not os.path.isdir(root):
            continue
        manifest_path = os.path.join(root, "manifest.json")
        if not os.path.exists(manifest_path):
            continue
        manifest = _safe_read_json(manifest_path) or {}
        packs.append(
            {
                "industry_id": name,
                "title": manifest.get("title") or manifest.get("name") or name,
                "version": manifest.get("version"),
                "category": manifest.get("category"),
                "tags": manifest.get("tags", []),
                "description": manifest.get("description"),
            }
        )
    return packs


def build_runtime_registry(
    base_dir: str = "industry_packs_runtime",
    out_path: str = "industry_packs_runtime/registry.json",
) -> None:
    """Write a runtime registry.json for installed industry packs."""
    packs = discover_industry_packs(base_dir=base_dir)
    os.makedirs(base_dir, exist_ok=True)
    payload = {
        "base_dir": base_dir,
        "count": len(packs),
        "packs": packs,
    }
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    except Exception:
        # Registry is optional; don't block startup.
        return
