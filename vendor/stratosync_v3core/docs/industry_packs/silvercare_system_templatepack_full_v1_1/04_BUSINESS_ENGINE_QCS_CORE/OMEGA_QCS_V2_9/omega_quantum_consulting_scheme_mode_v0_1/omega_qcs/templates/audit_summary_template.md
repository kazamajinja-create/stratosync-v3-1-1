# 監査・会計専門家向けサマリー（Snapshot）
- 分析日時: {{analysis_datetime}}
- 対象期間: {{period}}
- 入力根拠: {{source}}
- 役割定義: 本サマリーは会計処理・税務判断・監査意見を行うものではなく、意思決定前提の整理のための構造抽出である。

## 1. 入力（概要）
- 通貨: {{currency}}
- PL: 売上 {{pl_revenue}}, 売上原価 {{pl_cogs}}, 販管費 {{pl_sga}}, 当期純利益 {{pl_net_income}}
- BS: 総資産 {{bs_assets}}, 総負債 {{bs_liabilities}}, 純資産 {{bs_net_assets}}
- CF: 営業CF {{cf_op}}, 投資CF {{cf_inv}}, 財務CF {{cf_fin}}

## 2. 抽出された構造ラベル（評価なし）
- 構造集中指数: {{idx_structure_concentration}}
- コスト硬直指数: {{idx_cost_rigidity}}
- 資金流動指数: {{idx_cashflow}}
- 変動性指数: {{idx_volatility}}

## 3. 不確定性（明示）
- 未入力/不明項目: {{unknown_fields}}
- 外部要因依存: {{external_dependencies}}

## 4. 変更管理（再現性）
- エンジンVersion: {{engine_version}}
- 入力ハッシュ: {{input_hash}}
