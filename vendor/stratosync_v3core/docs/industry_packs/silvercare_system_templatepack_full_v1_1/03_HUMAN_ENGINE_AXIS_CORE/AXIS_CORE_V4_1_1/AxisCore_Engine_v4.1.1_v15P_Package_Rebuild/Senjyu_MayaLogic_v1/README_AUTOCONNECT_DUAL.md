
# Senjyu Maya AutoConnect (Dual Strategy)

**目的**: 既存の `app.main:app` を一切編集せず、起動時に自動で `/api/maya/*` ルータを登録します。

## 同梱ファイル
- `.app/sitecustomize.py` … Python起動時に自動実行。即時登録を試み、失敗時はフォールバックを起動。
- `senjyu_app/Senjyu_AddOn_Modules_v3_2/auto/auto_patch_loader.py` … appロードを監視し、準備でき次第で自動登録。

## 設置
このZIPを既存リポジトリに展開し、**上記2ファイルをそのまま配置**するだけ。  
Procfile や `app/main.py` の変更は不要です。

## 仕組み
1) Gunicorn/uvicorn が Python を起動 → `.app/sitecustomize.py` が自動import  
2) 可能なら即時に `app.main:app` を取得して `/api/maya/*` を登録  
3) まだ未初期化なら `auto_patch_loader` がバックグラウンドで数十秒だけ監視して登録

## テスト
- 情報: `GET  /api/maya/dict/info`
- 取得: `POST /api/maya/dict/get`  `{"tone": 11, "seal": "Ahau"}`
- 詩文: `POST /api/maya/story`    `{"tone": 11, "seal": "Ahau", "lang": "ja"}`

## 注意
- この方式は **完全非侵襲** です（既存コード無改変）。
- ログに `[AutoConnect]` / `[AutoPatch]` が出力されれば接続成功のサイン。
