
import argparse, csv, os, random, json, pathlib

BASE = pathlib.Path(__file__).resolve().parents[2]

def load_tsv(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for r in reader:
            rows.append(r)
    return rows

def pick(words, tag=None, default=""):
    if tag:
        pool = [w["語形"] for w in words if w.get("タグ")==tag]
        if pool:
            return random.choice(pool)
    # fallback
    if words:
        return random.choice([w["語形"] for w in words])
    return default

def assemble(intent="宣言", place="富士", heav="火", earth="水", god_hint=None):
    miyashita = load_tsv(BASE/"data/miyashita_lexicon.tsv")
    kz = load_tsv(BASE/"data/kuzuryu_kotodama_dict.tsv")

    god1 = god_hint or pick(miyashita, "GOD", "天御中主大神")
    god2 = pick(miyashita, "GOD", god1)
    heav1 = heav
    earth1 = earth

    # Simple 5-7 cadence helper (very naive; for demo only)
    def line5(text):
        return text
    def line7(text):
        return text

    if intent in ("鎮魂","浄化"):
        t = [
            f"{line7('天津'+heav1+' かがやき出でて')}／{line7('国津'+earth1+' むすび清む')}",
            f"{line7(god1+' にまします 御稜威')}／{line7('ここに '+place+' を 鎮め定む')}",
            f"{line7('祓へ給ひ 清め給へ')}／{line7('現はれ出づる 光なり')}"
        ]
    else:  # 宣言・創造系
        t = [
            f"{line7('天津'+heav1+' かがやき出でて')}／{line7('国津'+earth1+' むすび清む')}",
            f"{line7(god1+' にまします 御稜威（みいづ）')}／{line7('ここに '+place+' を 鎮め定む')}",
            f"{line7('祓へ給ひ 清め給へ')}／{line7('現はれ出づる 光なり')}"
        ]

    return "\n".join(t)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--intent", default="宣言")
    ap.add_argument("--place", default="富士")
    ap.add_argument("--heav", default="火")
    ap.add_argument("--earth", default="水")
    ap.add_argument("--god_hint", default=None)
    args = ap.parse_args()
    chant = assemble(args.intent, args.place, args.heav, args.earth, args.god_hint)
    print(chant)

if __name__ == "__main__":
    main()
