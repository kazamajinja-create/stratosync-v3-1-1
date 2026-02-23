from __future__ import annotations

from typing import Any, Dict, Optional


def get_by_path(obj: Any, path: str) -> Any:
    """Read nested values using dotted paths.

    Example: "outputs.rcl.branch_explosion.bei_score"
    Returns None if the path can't be resolved.
    """
    if obj is None:
        return None
    if not path:
        return None

    cur: Any = obj
    for part in path.split("."):
        if part == "":
            continue
        if isinstance(cur, dict):
            if part not in cur:
                return None
            cur = cur.get(part)
        else:
            # allow attribute access as a fallback
            if not hasattr(cur, part):
                return None
            cur = getattr(cur, part)
    return cur


def format_value(value: Any, fmt: str | None = None, default: str = "-") -> str:
    """Format report values in a template-driven way.

    Supported fmt:
      - "str" (default)
      - "int"
      - "float1" / "float2" / "float3"
      - "percent0" / "percent1"
      - "bool"
    """
    if value is None:
        return default

    if fmt is None or fmt == "str":
        return str(value)

    try:
        if fmt == "int":
            return str(int(round(float(value))))
        if fmt.startswith("float"):
            d = int(fmt.replace("float", "") or "2")
            return f"{float(value):.{d}f}"
        if fmt.startswith("percent"):
            d = int(fmt.replace("percent", "") or "0")
            return f"{float(value) * 100:.{d}f}%"
        if fmt == "bool":
            return "YES" if bool(value) else "NO"
    except Exception:
        return str(value)

    return str(value)


def compile_report_fields(record: Dict[str, Any], layout: Dict[str, Any]) -> Dict[str, Any]:
    """Resolve a layout into concrete strings.

    Layout schema (minimal):
      {
        "title": "...",
        "sections": [
          {
            "heading": "...",
            "items": [
              {"label": "...", "path": "outputs....", "fmt": "float2", "default": "-"}
            ]
          }
        ]
      }
    """
    out: Dict[str, Any] = {"title": layout.get("title") or "Report", "sections": []}
    for sec in (layout.get("sections") or []):
        heading = sec.get("heading") or ""
        items_out = []
        for it in (sec.get("items") or []):
            label = it.get("label") or ""
            path = it.get("path") or ""
            fmt = it.get("fmt")
            default = it.get("default") or "-"
            val = get_by_path(record, path)
            items_out.append({
                "label": label,
                "value": format_value(val, fmt=fmt, default=default),
            })
        out["sections"].append({"heading": heading, "items": items_out})
    return out


def merge_layout(base: Dict[str, Any], overlay: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Shallow merge for layout overrides.

    - overlay.title overrides base.title
    - overlay.sections replaces base.sections when provided
    """
    if not overlay:
        return dict(base)
    merged = dict(base)
    if overlay.get("title"):
        merged["title"] = overlay.get("title")
    if overlay.get("sections"):
        merged["sections"] = overlay.get("sections")
    return merged
