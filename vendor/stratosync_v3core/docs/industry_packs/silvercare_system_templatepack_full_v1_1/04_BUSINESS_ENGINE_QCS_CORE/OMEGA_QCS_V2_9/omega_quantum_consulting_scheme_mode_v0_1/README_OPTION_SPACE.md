# Option Space Expansion (v0.8)
本機能は、分析結果（構造・指数・不確定性）から、これまで意識に上がっていなかった「選択肢そのもの」を可視化します。

## 重要
- 推奨・順位付け・決定は行いません（非決定ツール）
- 量子的・多観測的 = 複数の観測点（CEO/Finance/Ops/Customer/Reputation）で同一事実を再読解します

## 概念フロー
1) 入力（ヒアリング/事実/決算書等）
2) 分析（構造スナップショット、指数、不確定性）
3) 傾向モデル算出（tendency_model）
4) 選択肢空間の展開（option_space.expand_option_space）
5) 出力（Option Spaceレポート + Ωポイント）

## 使い方（概念）
- option_space.expand_option_space(structure, indices, uncertainty, constraints, known_options)
- templates/option_space_template.md を用いてレポートに組み込みます
