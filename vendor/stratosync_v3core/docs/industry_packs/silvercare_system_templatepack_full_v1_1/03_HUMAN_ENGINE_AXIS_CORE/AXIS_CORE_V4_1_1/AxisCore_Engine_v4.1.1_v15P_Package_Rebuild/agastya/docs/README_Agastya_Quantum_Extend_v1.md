# Agastya Quantum Extend Pack v1

## 目的
アガスティア単体版に、言語層（Gamma）・因果層（Epsilon）・統合層（Helios）と量子確率レイヤを導入し、
泉珠エコシステムに近い多層連動解析を実現します。

## エンドポイント
`POST /api/agastya/quantum`
```json
{
  "seed": "client_123",
  "chapter": 37,
  "text": "（霊視文）"
}
```

## 応答例（抜粋）
```json
{
  "ok": true,
  "quantum": {"confidence": 0.82, "amplitude": 0.634, "angle_deg": 128.6},
  "gamma": {"theme": "転機", "polarity": "caution", "tense": "future"},
  "result": {"summary":"...", "recommendations":["..."]}
}
```

## 組み込み
- NoCode構成：`app_wrapper_autoinclude` がある場合は `render/routes/agastya_quantum_routes.py` を自動include
- AutoPatch構成：`main.py` に以下を追加
```python
from render.routes.agastya_quantum_routes import router as agastya_router
app.include_router(agastya_router)
```

## テスト
```bash
BASE_URL="https://<your-app>" SEED="client42" CH_START=1 CH_END=5 python tools/agastya_test_cycle.py
```
