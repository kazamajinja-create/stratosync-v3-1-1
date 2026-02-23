from __future__ import annotations
import argparse, json
from .kernel import guard_text, load_policy

def main():
    ap = argparse.ArgumentParser(description="Kabbalah Tree Kernel (AXIS) - CLI")
    ap.add_argument("--text", required=True, help="Input text (intent / post / request)")
    ap.add_argument("--policy", default=None, help="Optional policy.json path")
    args = ap.parse_args()

    policy = load_policy(args.policy)
    res = guard_text(args.text, policy)
    out = {
        "ok": res.ok,
        "level": res.level,
        "flags": [{"name": f.name, "score": f.score, "evidence": f.evidence} for f in res.flags],
        "next_step": res.next_step,
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
