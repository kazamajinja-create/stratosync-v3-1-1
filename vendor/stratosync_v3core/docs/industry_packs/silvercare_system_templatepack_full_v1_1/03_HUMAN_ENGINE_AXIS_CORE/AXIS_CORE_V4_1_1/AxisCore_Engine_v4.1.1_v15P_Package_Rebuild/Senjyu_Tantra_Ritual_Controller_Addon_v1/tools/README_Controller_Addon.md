# Senjyu Tantra Ritual Controller Addon (差分モジュール)
このアドオンは、司令塔（FastAPI）からタントラ儀式モジュールを**モード発火**できるようにする差分パックです。

## 同梱ファイル
- `render/routers/rituals.py` … /rituals/plan エンドポイントで Lite/Explicit を切替
- `tools/auto_integrate_controller.py` … ルーター配置＆ main.py への include 自動パッチ
- `tests/curl_examples.txt` … 動作確認コマンド例

## 導入手順（Render/ローカル共通）
1. 本ディレクトリを **プロジェクトルート**に置く（`.app` と同じ階層）
2. 依存モジュールが `.app/core/extend/Senjyu_Tantra_SexRitual_Extend_v1/` に存在することを確認
3. 実行:
   ```bash
   python tools/auto_integrate_controller.py
   ```
4. 成功すると以下が実施されます：
   - `routers/rituals.py` が `.app/(render/)routers/` にコピー
   - `.app/(render/)main.py` に include を自動追記

## 環境変数
- `EXPLICIT_RITUALS_ENABLED=true` を設定すると、成人＋同意確認済みかつ `mode="explicit"` リクエストで Explicit が有効化。
  - 未設定（false）の場合は Lite に矯正されます。

## 動作確認
- `tests/curl_examples.txt` を参照してください。
