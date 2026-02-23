from __future__ import annotations
import json, os, hashlib, zipfile
from datetime import datetime
from typing import Any, Dict, Optional, Tuple, List, Iterable

def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def ensure_dir(path: str) -> None:
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)

def read_last_hash(audit_log_path: str) -> Optional[str]:
    if not os.path.exists(audit_log_path):
        return None
    last = None
    with open(audit_log_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                last = obj.get("audit", {}).get("record_hash") or last
            except Exception:
                continue
    return last

def append_audit_record(audit_log_path: str, record: Dict[str, Any]) -> Tuple[str, Optional[str]]:
    ensure_dir(audit_log_path)
    prev = read_last_hash(audit_log_path)

    payload = json.dumps(record, sort_keys=True, separators=(",", ":"))
    record_hash = _sha256((prev or "") + payload)

    record.setdefault("audit", {})
    record["audit"]["prev_hash"] = prev
    record["audit"]["record_hash"] = record_hash

    with open(audit_log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return record_hash, prev

def iter_audit_records(audit_log_path: str) -> Iterable[Dict[str, Any]]:
    if not os.path.exists(audit_log_path):
        return
    with open(audit_log_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except Exception:
                continue

def filter_records_by_project(audit_log_path: str, project_id: str, limit: int = 200) -> List[Dict[str, Any]]:
    # read all and filter; for very large logs consider an index
    out: List[Dict[str, Any]] = []
    for rec in iter_audit_records(audit_log_path):
        if rec.get("project_id") == project_id:
            out.append(rec)
    out.sort(key=lambda r: r.get("timestamp",""))
    if limit and len(out) > limit:
        out = out[-limit:]
    return out

def verify_hash_chain(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    # Verify per-record hash correctness and continuity given the stored prev_hash.
    # Note: Chain is global in the log, so for a filtered subset we verify:
    # - record_hash matches recomputation using stored prev_hash and record payload
    # - we report continuity within subset where possible
    ok = True
    details = []
    for rec in records:
        audit = rec.get("audit", {})
        prev = audit.get("prev_hash") or ""
        stored = audit.get("record_hash") or ""
        # recompute using the record as stored (including audit placeholders) — to avoid recursion,
        # recompute against a copy with current audit removed, then add empty audit.
        rec_copy = dict(rec)
        rec_copy["audit"] = {}
        payload = json.dumps(rec_copy, sort_keys=True, separators=(",", ":"))
        recomputed = _sha256(prev + payload)
        if recomputed != stored:
            ok = False
            details.append({
                "evaluation_id": rec.get("evaluation_id"),
                "timestamp": rec.get("timestamp"),
                "status": "FAIL",
                "reason": "record_hash mismatch",
                "stored": stored,
                "recomputed": recomputed,
                "prev_hash": prev,
            })
        else:
            details.append({
                "evaluation_id": rec.get("evaluation_id"),
                "timestamp": rec.get("timestamp"),
                "status": "OK",
                "prev_hash": prev,
                "record_hash": stored,
            })
    return {"ok": ok, "count": len(records), "details": details[-50:]}  # cap detail size

def export_evidence_bundle(audit_log_path: str, state_db_path: str, project_id: str, out_zip_path: str, limit: int = 500) -> Dict[str, Any]:
    ensure_dir(out_zip_path)
    records = filter_records_by_project(audit_log_path, project_id, limit=limit)
    verification = verify_hash_chain(records)
    bundle_manifest = {
        "project_id": project_id,
        "exported_at": datetime.utcnow().isoformat() + "Z",
        "record_count": len(records),
        "verification_ok": verification["ok"],
        "note": "Hash chain is global; verification checks record_hash correctness using each record's stored prev_hash.",
    }

    # write temp files
    tmp_dir = os.path.join(os.path.dirname(out_zip_path), f"_bundle_{project_id.replace(':','_')}")
    os.makedirs(tmp_dir, exist_ok=True)
    rec_path = os.path.join(tmp_dir, "audit_records.jsonl")
    with open(rec_path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    ver_path = os.path.join(tmp_dir, "verification_report.json")
    with open(ver_path, "w", encoding="utf-8") as f:
        json.dump(verification, f, ensure_ascii=False, indent=2)
    man_path = os.path.join(tmp_dir, "manifest.json")
    with open(man_path, "w", encoding="utf-8") as f:
        json.dump(bundle_manifest, f, ensure_ascii=False, indent=2)

    # include latest state snapshot if exists
    if os.path.exists(state_db_path):
        with open(state_db_path, "r", encoding="utf-8") as f:
            db = json.load(f)
        latest = db.get(project_id)
        if latest:
            with open(os.path.join(tmp_dir, "latest_state.json"), "w", encoding="utf-8") as f2:
                json.dump(latest, f2, ensure_ascii=False, indent=2)

    # zip bundle
    with zipfile.ZipFile(out_zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for fn in os.listdir(tmp_dir):
            z.write(os.path.join(tmp_dir, fn), arcname=fn)

    # cleanup temp dir
    for fn in os.listdir(tmp_dir):
        os.remove(os.path.join(tmp_dir, fn))
    os.rmdir(tmp_dir)

    return bundle_manifest


def export_evidence_bundle_with_attachments(
    audit_log_path: str,
    state_db_path: str,
    project_id: str,
    out_zip_path: str,
    limit: int = 500,
    attachments: dict | None = None,
) -> Dict[str, Any]:
    """Export evidence bundle and optionally include attachments like board.pdf and trend.png."""
    ensure_dir(out_zip_path)
    records = filter_records_by_project(audit_log_path, project_id, limit=limit)
    verification = verify_hash_chain(records)
    bundle_manifest = {
        "project_id": project_id,
        "exported_at": datetime.utcnow().isoformat() + "Z",
        "record_count": len(records),
        "verification_ok": verification["ok"],
        "attachments": [],
        "note": "Hash chain is global; verification checks record_hash correctness using each record's stored prev_hash.",
    }

    tmp_dir = os.path.join(os.path.dirname(out_zip_path), f"_bundle_{project_id.replace(':','_')}")
    os.makedirs(tmp_dir, exist_ok=True)

    rec_path = os.path.join(tmp_dir, "audit_records.jsonl")
    with open(rec_path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    ver_path = os.path.join(tmp_dir, "verification_report.json")
    with open(ver_path, "w", encoding="utf-8") as f:
        json.dump(verification, f, ensure_ascii=False, indent=2)

    man_path = os.path.join(tmp_dir, "manifest.json")
    with open(man_path, "w", encoding="utf-8") as f:
        json.dump(bundle_manifest, f, ensure_ascii=False, indent=2)

    # latest state snapshot
    if os.path.exists(state_db_path):
        with open(state_db_path, "r", encoding="utf-8") as f:
            db = json.load(f)
        latest = db.get(project_id)
        if latest:
            with open(os.path.join(tmp_dir, "latest_state.json"), "w", encoding="utf-8") as f2:
                json.dump(latest, f2, ensure_ascii=False, indent=2)

    # attachments
    if attachments:
        for name, path in attachments.items():
            if path and os.path.exists(path):
                dest = os.path.join(tmp_dir, name)
                with open(path, "rb") as src:
                    data = src.read()
                with open(dest, "wb") as dst:
                    dst.write(data)
                bundle_manifest["attachments"].append(name)

    # rewrite manifest with attachment list
    with open(man_path, "w", encoding="utf-8") as f:
        json.dump(bundle_manifest, f, ensure_ascii=False, indent=2)

    with zipfile.ZipFile(out_zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for fn in os.listdir(tmp_dir):
            z.write(os.path.join(tmp_dir, fn), arcname=fn)

    for fn in os.listdir(tmp_dir):
        os.remove(os.path.join(tmp_dir, fn))
    os.rmdir(tmp_dir)

    return bundle_manifest
