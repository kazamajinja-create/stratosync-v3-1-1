from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class IndustryPack:
    """Runtime industry pack.

    Design goal: adding a new industry template must be achievable by
    dropping a new folder under `industry_packs_runtime/<industry_id>/`.

    Minimal structure:
      industry_packs_runtime/<industry_id>/
        manifest.json
        rcl_params.json              (optional)
        report_layout.executive.json (optional)
        report_layout.agent.json     (optional)

    This keeps the core product stable while templates grow.
    """

    industry_id: str
    root_dir: str
    manifest: Dict[str, Any]

    def load_json(self, rel_path: str) -> Optional[Dict[str, Any]]:
        p = os.path.join(self.root_dir, rel_path)
        if not os.path.exists(p):
            return None
        try:
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def rcl_params(self) -> Dict[str, Any]:
        return self.load_json("rcl_params.json") or {}

    def report_layout(self, kind: str) -> Optional[Dict[str, Any]]:
        # kind: "executive" | "agent" | ...
        return self.load_json(f"report_layout.{kind}.json")


def discover_industry_pack(industry_id: str, base_dir: str = "industry_packs_runtime") -> Optional[IndustryPack]:
    root = os.path.join(base_dir, industry_id)
    manifest_path = os.path.join(root, "manifest.json")
    if not os.path.exists(manifest_path):
        return None
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        return IndustryPack(industry_id=industry_id, root_dir=root, manifest=manifest)
    except Exception:
        return None


def load_rcl_params_for(industry_id: str) -> Dict[str, Any]:
    """Return industry-calibrated parameters for RCL.

    - If a runtime pack exists: use its rcl_params.json.
    - Else: return empty dict (RCL will use defaults).
    """
    pack = discover_industry_pack(industry_id)
    if not pack:
        return {}
    return pack.rcl_params() or {}
