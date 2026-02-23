
# Kuzuryu_Kotodama_AllInOne_v2

**九頭龍神的言霊モジュール v2（宮下文書辞書バンドル＋生成API）**

## 構成
- `data/` : 宮下文書辞書（抜粋）・九頭龍言霊辞書
- `config/` : 呼吸パターン
- `src/kuzuryu_kotodama/` : 生成器・API・融合ロジック
- `templates/` : 詩テンプレ
- `docs/` : 使い方
- `meta/` : 免責

## クイックスタート（ローカル）
```bash
python -m kuzuryu_kotodama.generator --intent 宣言 --place 高千穂 --heav 火 --earth 水
# API
python -m kuzuryu_kotodama.api
# 別端末で:
# curl -X POST http://127.0.0.1:8000/generate -H "Content-Type: application/json" -d '{"intent":"宣言","place":"高千穂"}'
```
