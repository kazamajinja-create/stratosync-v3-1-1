\
#!/usr/bin/env python3
# agastia_resonant_formatter_core.py
# 「泉珠コア接続版」：本番接続できるIFを備え、未接続環境でも自己完結で動くフェイルセーフ実装。

import os, json, glob, argparse, random, re, importlib, hashlib
from datetime import datetime, timedelta

# ========= Determinism Patch =========
# 同一出生情報での揺れ（random）を抑えるための局所RNG。
# 入口から seed を渡せない場合でも、環境変数 SENJYU_FIXED_SEED を設定すれば固定できます。
def _seed_int(seed_str: str) -> int:
    h = hashlib.sha256(seed_str.encode("utf-8")).hexdigest()
    return int(h[:16], 16)

def _rng(seed_hint: str, *, salt: str) -> random.Random:
    env_seed = os.getenv("SENJYU_FIXED_SEED")
    base = env_seed if env_seed else seed_hint
    return random.Random(_seed_int(f"{salt}|{base}"))

# ========= Utilities =========
def read_json(fp):
    with open(fp, "r", encoding="utf-8") as f:
        return json.load(f)

def load_chapters_from_dir(dir_path):
    files = sorted(glob.glob(os.path.join(dir_path, "agastya_part*_filled.json")))
    chapters = []
    for fp in files:
        data = read_json(fp)
        chapters.extend(data.get("chapters", []))
    return chapters

def load_chapters_from_file(json_path):
    return read_json(json_path).get("chapters", [])

# ========= ① 精密ヴェーダ：泉珠コアIF =========
def try_import(path, name):
    try:
        return importlib.import_module(name)
    except Exception:
        return None

def make_vedic_annotation(birth_dt=None, lat=None, lon=None, depth="maha_antara_pratyantara"):
    """
    接続先優先順：
      1) zent_core.vedic.engine (想定) の get_dashas(), get_transits()
      2) 簡易ローカル実装（ダミーだが分運まで段組み）
    戻り値スキーマは固定：{range, dasha:[...], transits:[...]}
    """
    # --- 1) external (if available) ---
    ext = try_import(".", "zent_core_vedic_engine")
    if ext and hasattr(ext, "get_dashas"):
        try:
            dashas = ext.get_dashas(birth_dt=birth_dt, depth=depth)
            trans = ext.get_transits(birth_dt=birth_dt)
            return {"range": dashas.get("range",""), "dasha": dashas.get("dasha",[]), "transits": trans}
        except Exception as e:
            pass  # フォールバックへ

    # --- 2) fallback dummy (deterministic-ish) ---
    base_year = 2026
    if birth_dt:
        base_year = birth_dt.year + (birth_dt.month % 3)
    start = f"{base_year}-05-17"
    end   = f"{base_year+2}-11-20"

    seq = ["Jupiter","Saturn","Mercury","Ketu","Venus","Sun","Moon","Mars","Rahu"]
    seed_hint = (birth_dt.isoformat() if birth_dt else str(base_year))
    r = _rng(seed_hint, salt="vedic")
    # 擬似的にレベルを積層（deterministic）
    maha = {"level":"maha","lord":r.choice(seq),"from":start,"to":f"{base_year+1}-06-30","themes":["基盤","拡張","変容"]}
    antara = {"level":"antara","lord":r.choice(seq),"from":start,"to":f"{base_year}-12-02","themes":["縁","移動","心"]}
    praty = {"level":"pratyantara","lord":r.choice(seq),"from":f"{base_year}-09-01","to":f"{base_year}-11-15","themes":["転機","合意","再会"]}

    out = {"range": f"{start}〜{end}", "dasha":[maha, antara], "transits":[
        {"event":"Saturn square Natal Sun","date":f"{base_year+1}-03-11","note":"責務の刷新"},
        {"event":"Jupiter trine MC","date":f"{base_year+1}-10-08","note":"肩書と支援"}
    ]}
    if depth == "maha_antara_pratyantara":
        out["dasha"].append(praty)
    return out

# ========= ② 泉珠量子MDOQ：観測霊視IF =========
def make_quantum(observer="seer:default", detail="chapter_section", collapse_threshold=0.65):
    """
    接続先優先順：
      1) izumidama.mdoq.core の observe()：{p, phase, dims, poetic}
      2) フォールバック：確率p・位相deltaの擬似生成
    """
    ext = try_import(".", "izumidama_mdoq_core")
    if ext and hasattr(ext, "observe"):
        try:
            r = ext.observe(observer=observer)
            p = float(r.get("p", 0.77))
            section = {
                "observer_state": observer,
                "collapse_p": round(p,2),
                "phase_delta": round(float(r.get("phase",0.07)), 2),
                "dimension_sync": r.get("dims", ["意識層3"]),
                "poetic": r.get("poetic","静寂に在れば道は一条となる。")
            }
            section["note"] = "収束域" if p >= collapse_threshold else "分岐域"
            return section if detail!="one_line" else {"poetic": section["poetic"]}
        except Exception:
            pass

    # fallback
    r = _rng(str(observer), salt="quantum")
    p = round(r.uniform(0.62, 0.91), 2)
    section = {
        "observer_state": observer,
        "collapse_p": p,
        "phase_delta": round(r.uniform(0.03,0.12), 2),
        "dimension_sync": ["意識層3","カルマ層5"] if p>0.75 else ["意識層2"],
        "poetic": "静寂に在れば道は一条となる。恐れあれば波は二つに割れる。",
        "note": "収束域" if p >= collapse_threshold else "分岐域"
    }
    return section if detail!="one_line" else {"poetic": section["poetic"]}

# ========= ③ 第4層ストーリー：改善版 =========
def synth_story(chapter, rules_path="story_rules_v2.json"):
    rules = read_json(rules_path) if os.path.exists(rules_path) else {
        "length":{"min":500,"max":900},
        "lexicon":{"softeners":["兆しが見える"],"actions":["深呼吸を3回する"]},
        "weaving":{"intro":"","bridge":"","insight":"","action":""}
    }
    min_len = rules["length"]["min"]; max_len = rules["length"]["max"]
    softs = rules["lexicon"]["softeners"]; acts = rules["lexicon"]["actions"]

    a = chapter.get("agastia_text","")
    v = chapter.get("vedic_annotation",{})
    q = chapter.get("izumidama_quantum",{})

    # 抽出
    a_key = re.split("[。\\n]", a)[0] if a else "この章の核は静かな決意。"
    v_blk = ""
    if isinstance(v, dict) and v.get("dasha"):
        lst = []
        for d in v["dasha"][:2]:
            lst.append(f"{d.get('from','')}〜{d.get('to','')}の{d.get('lord','')}期")
        v_blk = "、".join(lst)
    q_line = q.get("poetic") if isinstance(q, dict) else ""
    p = q.get("collapse_p", None) if isinstance(q, dict) else None

    seed_hint = (chapter.get("id") or chapter.get("title") or a_key or "story")
    r = _rng(str(seed_hint), salt="story")
    soften = r.choice(softs)
    act = r.choice(acts)

    text = (
        f"{a_key}。"
        f"{v_blk}を背景に、出来事の流れは形を取り始めます。"
        f"{q_line} この現れは選び方で強弱が変わり、{soften}局面です。"
        f"今日はまず「{act}」。それだけで道の輪郭が一段くっきりするでしょう。"
    )
    if len(text) > max_len:
        text = text[:max_len-1] + "…"
    return text

# ========= Plan handling =========
def clamp_for_lite(chapters, limit=50): return chapters[:limit]

def main():
    ap = argparse.ArgumentParser(description="Agastia Resonant Formatter (Core-connected)")
    ap.add_argument("--dir", help="agastya_100_filed ディレクトリ")
    ap.add_argument("--json", help="単一JSON（{'chapters':[...]}）")
    ap.add_argument("--plan", default="premium", choices=["lite","standard","premium"])
    ap.add_argument("--out", default="agastia_4layers_output.json")
    ap.add_argument("--birth", help="出生 'YYYY-MM-DDTHH:MM'", default=None)
    ap.add_argument("--latlon", help="緯度,経度 例 '35.68,139.76'", default=None)
    args = ap.parse_args()

    if args.dir:
        chapters = load_chapters_from_dir(args.dir)
    elif args.json:
        chapters = load_chapters_from_file(args.json)
    else:
        raise SystemExit("ERROR: --dir か --json を指定してください。")
    if not chapters:
        raise SystemExit("No chapters found.")

    if args.plan == "lite":
        chapters = clamp_for_lite(chapters, 50)

    birth_dt = None; lat=None; lon=None
    if args.birth:
        birth_dt = datetime.fromisoformat(args.birth)
    if args.latlon and "," in args.latlon:
        lat, lon = [float(x.strip()) for x in args.latlon.split(",")]

    out = {"plan": args.plan, "chapters":[]}

    for idx, ch in enumerate(chapters, 1):
        node = {
            "chapter_id": idx,
            "title": ch.get("title", f"第{idx}章"),
            "agastia_text": ch.get("content") or ch.get("agastia_text") or "（本文未設定）"
        }

        depth = "major_timeline" if args.plan=="lite" else "maha_antara" if args.plan=="standard" else "maha_antara_pratyantara"
        node["vedic_annotation"] = make_vedic_annotation(birth_dt=birth_dt, lat=lat, lon=lon, depth=depth)

        detail = "one_line" if args.plan=="lite" else "chapter_tail" if args.plan=="standard" else "chapter_section"
        node["izumidama_quantum"] = make_quantum(observer="seer:default", detail=detail, collapse_threshold=0.65)

        if args.plan == "premium":
            node["story"] = synth_story(node, rules_path=os.path.join(os.path.dirname(__file__), "story_rules_v2.json"))
        elif args.plan == "standard" and idx % 10 == 0:
            node["story"] = synth_story(node, rules_path=os.path.join(os.path.dirname(__file__), "story_rules_v2.json"))

        out["chapters"].append(node)

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"[OK] 4-layer JSON generated → {args.out} (plan={args.plan}, chapters={len(out['chapters'])})")

if __name__ == "__main__":
    main()
