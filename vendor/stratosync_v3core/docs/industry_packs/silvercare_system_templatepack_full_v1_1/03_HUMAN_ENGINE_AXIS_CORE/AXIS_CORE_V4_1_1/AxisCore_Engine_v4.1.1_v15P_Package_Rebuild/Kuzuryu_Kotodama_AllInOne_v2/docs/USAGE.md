
# 使い方（要約）
- CLI: `python -m kuzuryu_kotodama.generator --intent 浄化 --place 阿蘇 --heav 火 --earth 水`
- API: `python -m kuzuryu_kotodama.api` 起動後 `/generate` に JSON POST

## JSONボディ例
```json
{"intent":"鎮魂","place":"阿蘇カルデラ","heav":"火","earth":"水","god_hint":"天御中主大神"}
```
