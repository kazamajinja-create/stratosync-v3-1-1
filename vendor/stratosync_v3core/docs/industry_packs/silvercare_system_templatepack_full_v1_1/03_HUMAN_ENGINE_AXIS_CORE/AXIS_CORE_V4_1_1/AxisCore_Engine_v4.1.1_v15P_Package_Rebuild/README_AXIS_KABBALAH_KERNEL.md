# AXIS: Kabbalah module (independent)

本パッケージには、カバラ（生命の樹）ロジックを安全ゲートとして実装した独立モジュールが同梱されています。
場所: `modules/kabbalah_tree_kernel/`

起動（HTTP）:
```bash
python -m kabbalah_tree_kernel.server
```

判定:
```bash
curl -X POST http://localhost:8801/guard -H 'Content-Type: application/json' -d '{"text":"..."}'
```
