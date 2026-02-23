import os, hashlib
def _hash_prob(seed: str) -> float:
    h = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    return 0.55 + (int(h[:8], 16) / 0xffffffff) * 0.30
def thoth_layer(ctx: dict) -> str:
    name = ctx.get("client_code","あなた")
    return (f"「言葉は形なき光。{name}、汝が問う時、過去と未来は一つとなる。」\n"
            f"汝は記録を担う舟、誓いの印は再び刻まれる。")
def veda_layer(ctx: dict) -> dict:
    dob = ctx.get("dob","")
    score = _hash_prob(dob)
    return {"cycle_hint":"構文展開期","phase_score": round(score,3)}
def qpl_layer(ctx: dict) -> list:
    seed = "|".join([ctx.get("dob",""), ctx.get("tob","") or "", ctx.get("pob","") or ""])
    a = round(_hash_prob(seed+"A"), 2)
    b = round(_hash_prob(seed+"B"), 2)
    c = round(max(0.01, 1.0 - max(a,b)), 2)
    s = a+b+c
    if s>1.0:
        a,b,c = round(a/s,2), round(b/s,2), round(c/s,2)
    return [
        {"path":"A","prob":a,"conditions":["定期的な記述","レビュー導入"]},
        {"path":"B","prob":b,"conditions":["協力者2名以上"]},
        {"path":"C","prob":c,"conditions":["家庭要因優先"]},
    ]
def voynich_layer(ctx: dict) -> dict:
    return {"symbols": ["#84","#12","#33"], "concept":"共同編集", "confidence": 0.93}
def mode_g_layer(ctx: dict, thoth: str, qpl: list) -> str:
    best = max(qpl, key=lambda x: x["prob"])
    return f"Mode-G要約：{best['path']}経路が優勢（p={best['prob']}). 条件: {', '.join(best['conditions'])}."
def run_pipeline(ctx: dict) -> dict:
    thoth = thoth_layer(ctx)
    veda = veda_layer(ctx)
    qpl  = qpl_layer(ctx)
    voy  = voynich_layer(ctx)
    modeg = mode_g_layer(ctx, thoth, qpl)
    return {
        "thoth_text": thoth,
        "veda": veda,
        "qpl": qpl,
        "voynich": voy,
        "mode_g_summary": modeg,
        "meta": {"engine":"senjyu_light_v1.0","modes":["thoth","modeG","voynich","qpl"]}
    }
