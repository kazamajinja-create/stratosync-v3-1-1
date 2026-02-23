# Agastia Resonant Formatter – 泉珠コア接続版
- 3関数を本番接続IFに更新：
  1) make_vedic_annotation(birth_dt, lat, lon, depth)
  2) make_quantum(observer, detail, collapse_threshold)
  3) synth_story(chapter, rules_path)

## 実行例（Premium, 100章, 4層すべて）
python3 agastia_resonant_formatter_core.py --dir "../agastya_100_filed" --plan premium --birth "1967-04-21T11:20" --latlon "37.91,139.04" --out "agastia_full_4layers_premium_core.json"

※ 外部モジュールが見つかれば自動接続（zent_core_vedic_engine / izumidama_mdoq_core）。
  無い場合はフェイルセーフのローカル計算に自動切替。
