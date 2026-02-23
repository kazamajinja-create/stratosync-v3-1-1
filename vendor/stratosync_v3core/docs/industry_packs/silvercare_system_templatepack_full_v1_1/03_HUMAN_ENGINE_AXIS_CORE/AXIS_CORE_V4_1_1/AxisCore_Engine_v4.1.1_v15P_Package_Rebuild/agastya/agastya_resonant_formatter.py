\
#!/usr/bin/env python3
import os, json, glob, argparse, random, re
from datetime import datetime

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

def make_vedic_annotation(seed_idx, depth="maha_antara"):
    base_year = 2026 + (seed_idx % 3)
    start = f"{base_year}-05-17"
    end   = f"{base_year+1}-12-23"
    maha = {"level":"maha","lord":"Jupiter","from":start,"to":end,"themes":["拡張","学び","庇護"]}
    antara = {"level":"antara","lord":"Moon","from":start,"to":f"{base_year}-12-02","themes":["縁","移動","心"]}
    transits = [{"event":"Saturn square Natal Sun","date":f"{base_year+1}-03-11","note":"責務の刷新"}]
    out = {"range": f"{start}〜{end}", "dasha":[maha], "transits": transits}
    if depth in ("maha_antara","maha_antara_pratyantara"):
        out["dasha"].append(antara)
    return out

def make_quantum(detail="chapter_section", collapse_threshold=0.65):
    p = round(random.uniform(0.62, 0.88), 2)
    poetic = "静寂に在れば道は一条となる。恐れあれば波は二つに割れる。"
    section = {
        "observer_state":"seer:default",
        "collapse_p": p,
        "phase_delta": round(random.uniform(0.03,0.12), 2),
        "poetic": poetic
    }
    if p >= collapse_threshold:
        section["note"] = "収束域：選択が整いやすい位相"
    else:
        section["note"] = "分岐域：準備と静寂が必要"
    if detail == "one_line":
        return {"poetic": poetic}
    return section

def synth_story(chapter, max_len=700):
    a = chapter.get("agastia_text","")
    v = chapter.get("vedic_annotation",{})
    q = chapter.get("izumidama_quantum",{})
    a_key = re.split("[。\\n]", a)[0] if a else "この章の核は、静かな決意。"
    v_key = ""
    if isinstance(v, dict) and v.get("dasha"):
        d = v["dasha"][0]
        v_key = f"{d.get('from','')}〜{d.get('to','')}の{d.get('lord','')}期"
    q_key = q.get("poetic") if isinstance(q, dict) else ""
    text = f"{a_key}。{v_key}を背景に、この流れは姿を現します。{q_key} いまは一歩、小さな整えから始めましょう。"
    return text[:max_len]

def clamp_chapters_for_lite(chapters, limit=50):
    return chapters[:limit]

def main():
    ap = argparse.ArgumentParser(description="Agastia Resonant Formatter (4 layers, 3 plans)")
    ap.add_argument("--dir", help="agastya_100_filed ディレクトリ")
    ap.add_argument("--json", help="単一JSON（{'chapters':[...]}）")
    ap.add_argument("--plan", default="premium", choices=["lite","standard","premium"])
    ap.add_argument("--out", default="agastia_4layers_output.json")
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
        chapters = clamp_chapters_for_lite(chapters, 50)

    out = {"plan": args.plan, "chapters":[]}

    for idx, ch in enumerate(chapters, 1):
        node = {
            "chapter_id": idx,
            "title": ch.get("title", f"第{idx}章"),
            "agastia_text": ch.get("content") or ch.get("agastia_text") or "（本文未設定）"
        }

        # Vedic layer
        depth = "major_timeline" if args.plan=="lite" else "maha_antara" if args.plan=="standard" else "maha_antara_pratyantara"
        node["vedic_annotation"] = make_vedic_annotation(idx, depth=depth)

        # Quantum layer
        detail = "one_line" if args.plan=="lite" else "chapter_tail" if args.plan=="standard" else "chapter_section"
        node["izumidama_quantum"] = make_quantum(detail=detail, collapse_threshold=0.65)

        # Story layer
        if args.plan == "premium":
            node["story"] = synth_story(node, max_len=700)
        elif args.plan == "standard" and idx % 10 == 0:
            node["story"] = synth_story(node, max_len=550)

        out["chapters"].append(node)

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"[OK] 4-layer JSON generated → {args.out} (plan={args.plan}, chapters={len(out['chapters'])})")

if __name__ == "__main__":
    main()
