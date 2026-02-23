# Ω量子コンサルティングスキームモード v0.5（ZIPバインド版 / ローカル実行）

このZIPは「クラウド前」の **ローカル実行 + 将来クラウド移行前提** の最小実装です。
目的は、Ω量子コンサルティングの実務フロー（解析→レポ→セッション→納品）を
**モジュール群**として固定し、運用ブレを減らすことです。

## 収録モジュール
- `omega_intake`：事前ヒアリング（質問セット/入力正規化）
- `omega_case_registry`：案件管理（状態遷移）
- `omega_quantum_analyzer`：Ω量子ロジック解析（断定禁止ルール内蔵）
- `omega_report_builder`：解析レポート生成（Markdown + PDF）
- `omega_session_orchestrator`：90分セッション状態機械 + ログ + 要約
- `omega_meditation_micro`：3〜5分の補助ワーク（主目的化禁止）
- `omega_deliverables_pack`：納品物3点セット生成 + ZIP
- `omega_contract_pack`：別紙業務内容/免責テンプレ生成
- `omega_bridge_suite`：JWT/課金などは後で接続するためのプレースホルダ

## すぐ試す（Python 3.10+）
1) 依存導入
```bash
pip install -r requirements.txt
```

2) 起動
```bash
uvicorn app:app --reload
```

3) ブラウザ
- OpenAPI: http://127.0.0.1:8000/docs

## 典型フロー（API）
1. Case作成: `POST /omega/case/create`
2. Intake入力: `POST /omega/intake/submit`
3. 解析: `POST /omega/analyze/{case_id}`
4. レポ生成: `POST /omega/report/{case_id}/build`
5. セッション開始: `POST /omega/session/{case_id}/start`
6. セッションメモ: `POST /omega/session/{case_id}/note`
7. セッション確定: `POST /omega/session/{case_id}/finalize`
8. 納品ZIP: `POST /omega/deliver/{case_id}` → `GET /omega/deliver/{case_id}/zip`

## 重要ポリシー（固定）
- 未来予測・結果断定をしない（レポートには「結論」「おすすめ」を書かない）
- 決断はクライアントが行う（本実装は「判断材料の構造化」に限定）
- 瞑想ワークは補助であり主目的化しない（宿題化もしない）

## 将来の接続
- FastAPI_Controller_Bridge_Suite への router mount は `app.py` に集約
- Render/n8n/Bubble/Stripe/JWT は `omega_bridge_suite` を差し替えて接続


## v0.5 追加（品質/外部視点/KPI/自立指標）
- Quality Guard（断定/推奨の検出）
- 外部視点シミュレーター（誤解/批判/説明責任論点）
- AXIS育成KPIプロファイル（推奨KPI/除外KPI）
- AXIS自立指標（READY/BORDER/NOT_READY）
