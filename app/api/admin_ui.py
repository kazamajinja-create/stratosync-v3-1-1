from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, File, UploadFile, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.config import settings
from app.auto_bootstrap.template_installer import install_template_archives
from app.auto_bootstrap.registry import build_runtime_registry, discover_industry_packs

router = APIRouter(prefix="/admin", tags=["admin-ui"])

INBOX_DIR = "industry_packs_inbox"
RUNTIME_DIR = "industry_packs_runtime"
ARCHIVE_DIR = "industry_packs_archive"

def _require_key(request: Request) -> None:
    """Simple browser-friendly gate.

    If API_KEY is set, require query param ?k=<API_KEY>.
    (Browser forms can't easily set custom headers.)
    """
    if not settings.API_KEY:
        return
    k = request.query_params.get("k")
    if k != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")

def _html_page(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <style>
    body{{font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Noto Sans JP", sans-serif; margin: 24px;}}
    header{{display:flex; gap:16px; align-items:baseline; margin-bottom:16px;}}
    a{{color:#0b57d0; text-decoration:none;}}
    a:hover{{text-decoration:underline;}}
    .card{{border:1px solid #ddd; border-radius:10px; padding:16px; margin: 12px 0;}}
    table{{border-collapse:collapse; width:100%;}}
    th, td{{border-bottom:1px solid #eee; padding:8px; text-align:left; vertical-align:top;}}
    code{{background:#f6f8fa; padding:2px 6px; border-radius:6px;}}
    .muted{{color:#666;}}
    .ok{{color:#0a7f2e; font-weight:600;}}
    .err{{color:#b00020; font-weight:600;}}
    .btn{{display:inline-block; padding:8px 12px; border:1px solid #0b57d0; border-radius:8px;}}
  </style>
</head>
<body>
<header>
  <h2 style="margin:0;">STRATOSYNC Admin</h2>
  <nav class="muted">
    <a href="/admin/packs{_k_suffix(request=None)}">Templates</a>
    &nbsp;|&nbsp;
    <a href="/admin/upload{_k_suffix(request=None)}">Upload</a>
    &nbsp;|&nbsp;
    <a href="/docs">API Docs</a>
  </nav>
</header>
{body}
</body>
</html>"""


def _k_suffix(request: Optional[Request]) -> str:
    if not settings.API_KEY:
        return ""
    k = None
    if request is not None:
        k = request.query_params.get("k")
    # For link rendering, keep whatever was provided; if missing, just show empty.
    if not k:
        return ""
    return f"?k={k}"


@router.get("", include_in_schema=False)
def admin_root(request: Request):
    _require_key(request)
    return RedirectResponse(url="/admin/packs" + _k_suffix(request))


@router.get("/upload", response_class=HTMLResponse, include_in_schema=False)
def upload_form(request: Request):
    _require_key(request)
    suffix = _k_suffix(request)
    body = f"""
<div class="card">
  <h3>テンプレZIPをアップロード</h3>
  <p class="muted">ZIP内に <code>manifest.json</code> を含む業態パックがあれば、自動でインストールされます。</p>
  <form action="/admin/upload{suffix}" method="post" enctype="multipart/form-data">
    <input type="file" name="template_zip" accept=".zip" required />
    <button class="btn" type="submit">Upload</button>
  </form>
  <p class="muted" style="margin-top:10px;">インストール先: <code>{RUNTIME_DIR}/&lt;pack_id&gt;/</code></p>
</div>
"""
    return HTMLResponse(_wrap(request, "Upload Template", body))


@router.post("/upload", response_class=HTMLResponse, include_in_schema=False)
async def upload_template(request: Request, template_zip: UploadFile = File(...)):
    _require_key(request)
    if not template_zip.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip is supported")
    os.makedirs(INBOX_DIR, exist_ok=True)
    target = os.path.join(INBOX_DIR, template_zip.filename)
    # Save uploaded file
    data = await template_zip.read()
    with open(target, "wb") as f:
        f.write(data)

    # Install immediately (no need to wait for restart)
    installed = install_template_archives(
        inbox=INBOX_DIR,
        runtime=RUNTIME_DIR,
        archive=ARCHIVE_DIR,
    )
    build_runtime_registry(base_dir=RUNTIME_DIR, out_path=os.path.join(RUNTIME_DIR, "registry.json"))

    suffix = _k_suffix(request)
    if installed:
        items = "".join([f"<li><code>{p.pack_id}</code> → <span class='muted'>{p.installed_path}</span></li>" for p in installed])
        msg = f"<p class='ok'>Installed {len(installed)} pack(s).</p><ul>{items}</ul>"
    else:
        msg = "<p class='err'>No valid pack (manifest.json) found in the uploaded ZIP. The archive was moved to archive as rejected/error.</p>"

    body = f"""
<div class="card">
  <h3>アップロード結果</h3>
  {msg}
  <p><a class="btn" href="/admin/packs{suffix}">Go to Templates</a></p>
</div>
"""
    return HTMLResponse(_wrap(request, "Upload Result", body))


@router.get("/packs", response_class=HTMLResponse, include_in_schema=False)
def list_packs(request: Request):
    _require_key(request)
    packs = discover_industry_packs(base_dir=RUNTIME_DIR)
    suffix = _k_suffix(request)
    rows = ""
    for p in packs:
        tags = ", ".join(p.get("tags") or [])
        rows += f"""
<tr>
  <td><code>{p.get('industry_id')}</code></td>
  <td>{p.get('title') or ''}</td>
  <td>{p.get('version') or ''}</td>
  <td>{p.get('category') or ''}</td>
  <td class="muted">{tags}</td>
</tr>
"""
    body = f"""
<div class="card">
  <h3>インストール済みテンプレ一覧</h3>
  <p class="muted">現在: <strong>{len(packs)}</strong> pack(s)</p>
  <p><a class="btn" href="/admin/upload{suffix}">Upload a Template ZIP</a></p>
  <table>
    <thead>
      <tr><th>ID</th><th>Title</th><th>Version</th><th>Category</th><th>Tags</th></tr>
    </thead>
    <tbody>
      {rows if rows else '<tr><td colspan="5" class="muted">No packs installed yet.</td></tr>'}
    </tbody>
  </table>
  <p class="muted" style="margin-top:10px;">Tip: Billingを有効化する前でも、テンプレ運用は可能です。</p>
</div>
"""
    return HTMLResponse(_wrap(request, "Templates", body))


def _wrap(request: Request, title: str, body: str) -> str:
    # navigation links keep ?k=...
    suffix = _k_suffix(request)
    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <style>
    body{{font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Noto Sans JP", sans-serif; margin: 24px;}}
    header{{display:flex; gap:16px; align-items:baseline; margin-bottom:16px;}}
    a{{color:#0b57d0; text-decoration:none;}}
    a:hover{{text-decoration:underline;}}
    .card{{border:1px solid #ddd; border-radius:10px; padding:16px; margin: 12px 0;}}
    table{{border-collapse:collapse; width:100%;}}
    th, td{{border-bottom:1px solid #eee; padding:8px; text-align:left; vertical-align:top;}}
    code{{background:#f6f8fa; padding:2px 6px; border-radius:6px;}}
    .muted{{color:#666;}}
    .ok{{color:#0a7f2e; font-weight:600;}}
    .err{{color:#b00020; font-weight:600;}}
    .btn{{display:inline-block; padding:8px 12px; border:1px solid #0b57d0; border-radius:8px;}}
  </style>
</head>
<body>
<header>
  <h2 style="margin:0;">STRATOSYNC Admin</h2>
  <nav class="muted">
    <a href="/admin/packs{suffix}">Templates</a>
    &nbsp;|&nbsp;
    <a href="/admin/upload{suffix}">Upload</a>
    &nbsp;|&nbsp;
    <a href="/docs">API Docs</a>
  </nav>
</header>
{body}
</body>
</html>"""
