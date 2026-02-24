# Industry Packs (Runtime)

このフォルダ配下に業態テンプレを追加すると、STRATOSYNCは **コード改修なし**で帳票（PDF）を生成できます。

## 必須
- manifest.json

## 任意（推奨）
- rcl_params.json
- report_layout.executive.json
- report_layout.agent.json
- report_layout.enterprise.json

## 追加手順
1. `industry_packs_runtime/<industry_id>/` を作成
2. `manifest.json` を配置
3. 必要に応じて layout / params を配置
4. 帳票生成: `?industry=<industry_id>&kind=executive|agent|enterprise`
