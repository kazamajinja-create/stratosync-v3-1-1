"""Template archive auto-installer.

Goal: Make industry template expansion fully no-code.

Operator drops a template pack archive (zip) into:

    industry_packs_inbox/

On startup we will:
  - extract it
  - detect one or more packs containing manifest.json
  - install into industry_packs_runtime/<pack_id>/
  - move processed archives into industry_packs_archive/

This keeps Render deployments simple: attach a persistent disk and upload
archives (e.g., via SFTP / dashboard file manager / git pull) without touching code.
"""

from __future__ import annotations

import json
import os
import shutil
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional


@dataclass
class InstalledPack:
    pack_id: str
    source_archive: str
    installed_path: str


def _now_stamp() -> str:
    return datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")


def _safe_mkdir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _find_manifest_dirs(root: Path) -> list[Path]:
    """Return directories under root that contain manifest.json."""
    manifests: list[Path] = []
    for p in root.rglob("manifest.json"):
        if p.is_file():
            manifests.append(p.parent)
    # Prefer shallower manifests first
    manifests.sort(key=lambda x: len(x.parts))
    # Deduplicate nested duplicates: keep unique dirs
    uniq: list[Path] = []
    seen = set()
    for d in manifests:
        if str(d) not in seen:
            uniq.append(d)
            seen.add(str(d))
    return uniq


def _read_pack_id(manifest_path: Path, fallback: str) -> str:
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        pack_id = data.get("id") or data.get("pack_id") or data.get("industry_id")
        if isinstance(pack_id, str) and pack_id.strip():
            return pack_id.strip()
    except Exception:
        pass
    return fallback


def _install_pack_dir(pack_dir: Path, runtime_dir: Path, source_archive: Path) -> InstalledPack:
    # Determine id
    fallback = pack_dir.name
    pack_id = _read_pack_id(pack_dir / "manifest.json", fallback=fallback)

    target = runtime_dir / pack_id
    if target.exists():
        # Avoid overwrite; install as a versioned sibling.
        target = runtime_dir / f"{pack_id}__{_now_stamp()}"

    shutil.copytree(pack_dir, target)
    return InstalledPack(pack_id=pack_id, source_archive=str(source_archive), installed_path=str(target))


def install_template_archives(
    inbox: str = "industry_packs_inbox",
    runtime: str = "industry_packs_runtime",
    archive: str = "industry_packs_archive",
    exts: Iterable[str] = (".zip",),
) -> list[InstalledPack]:
    """Install any template archives found in inbox.

    This function is intentionally conservative:
      - If an archive does not contain any manifest.json, it is moved to archive
        with a `.rejected` suffix so operators can inspect it.
    """
    inbox_dir = Path(inbox)
    runtime_dir = Path(runtime)
    archive_dir = Path(archive)
    _safe_mkdir(str(inbox_dir))
    _safe_mkdir(str(runtime_dir))
    _safe_mkdir(str(archive_dir))

    installed: list[InstalledPack] = []
    candidates = [p for p in inbox_dir.iterdir() if p.is_file() and p.suffix.lower() in set(exts)]
    if not candidates:
        return installed

    for arc in sorted(candidates):
        stamp = _now_stamp()
        workdir = inbox_dir / f"._extract_{arc.stem}_{stamp}"
        if workdir.exists():
            shutil.rmtree(workdir)
        workdir.mkdir(parents=True, exist_ok=True)

        try:
            if arc.suffix.lower() == ".zip":
                with zipfile.ZipFile(arc, "r") as zf:
                    zf.extractall(workdir)
            else:
                # Unsupported extension (should not happen due to filter)
                raise ValueError(f"Unsupported archive extension: {arc.suffix}")

            pack_dirs = _find_manifest_dirs(workdir)
            if not pack_dirs:
                # Move archive as rejected
                rejected = archive_dir / f"{arc.name}.{stamp}.rejected"
                shutil.move(str(arc), str(rejected))
                continue

            # Install each pack directory found
            for pack_dir in pack_dirs:
                installed.append(_install_pack_dir(pack_dir, runtime_dir, arc))

            # Move processed archive
            processed = archive_dir / f"{arc.name}.{stamp}.processed"
            shutil.move(str(arc), str(processed))

        except Exception:
            # Move archive as error
            errored = archive_dir / f"{arc.name}.{stamp}.error"
            try:
                shutil.move(str(arc), str(errored))
            except Exception:
                pass
        finally:
            try:
                shutil.rmtree(workdir)
            except Exception:
                pass

    return installed
