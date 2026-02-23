def render_text(layers: dict, plan: str="C") -> str:
    T = []
    if plan in ("A","B","C"):
        T.append("— 序章（Thoth）—\n"+layers["thoth_text"]+"\n")
    if plan in ("B","C"):
        T.append("— 量子確率（QPL）—")
        for p in layers["qpl"]:
            T.append(f"  Path-{p['path']}: {p['prob']} 条件: {', '.join(p['conditions'])}")
    if plan == "C":
        T.append("— Voynich解読 —")
        v = layers["voynich"]
        T.append(f"  概念: {v['concept']}  信頼度: {v['confidence']}  記号: {', '.join(v['symbols'])}")
        T.append("— Mode-G再構文 —\n"+layers["mode_g_summary"])
    return "\n".join(T)
