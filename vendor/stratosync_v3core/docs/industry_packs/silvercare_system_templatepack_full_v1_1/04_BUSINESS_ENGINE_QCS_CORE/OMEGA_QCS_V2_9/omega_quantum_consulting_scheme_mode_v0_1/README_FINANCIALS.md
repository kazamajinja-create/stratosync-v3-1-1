# Financial Snapshot (v0.7)
本機能は、過去の決算書等の財務情報を「評価せずに」構造抽出し、傾向モデル算出の前提データとして利用します。

## 入力スキーマ
- omega_qcs/schemas/financials_input_schema.json

## 最小入力例（JSON）
```json
{
  "period": "FY2024",
  "currency": "JPY",
  "source": "決算書（監査対象）",
  "pl": {"revenue": 100000000, "cogs": 20000000, "sg_and_a": 50000000, "net_income": 8000000},
  "bs": {"total_assets": 60000000, "total_liabilities": 30000000, "net_assets": 30000000},
  "cf": {"operating_cf": 12000000, "investing_cf": -6000000, "financing_cf": -2000000}
}
```

## 処理フロー（概念）
1) normalize_financials.normalize(financials)
2) financial_snapshot.build_snapshot(derived)
3) structure_indices.extract_indices(snapshot)
4) tendency_model.build_tendency_model(indices)

> 注意: 本機能は会計処理・税務判断・監査意見を行いません。
