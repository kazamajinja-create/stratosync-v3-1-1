from __future__ import annotations

def top3_actions(si_axes: dict, omega_index: float, daf: float) -> list[str]:
    # Deterministic top-3: choose lowest surface axes + org connectivity + decision factor
    items = []
    # Surface axis suggestions
    axis_map = {
        "CT":"顧客接点（頻度・深度・多様性）の再設計",
        "AL":"業務ツール/API連携の自動化・接続強化",
        "PN":"提携ネットワークの増設と継続協業化",
        "BE":"ブランド露出の一貫性と指名導線の強化",
        "DC":"データ取得→可視化→意思決定の定着"
    }
    sorted_axes = sorted([(k, float(v)) for k,v in si_axes.items() if k in axis_map], key=lambda x: x[1])
    for k,_ in sorted_axes[:2]:
        items.append(axis_map[k])

    if omega_index < 60:
        items.append("部門間の接続（連携）を増やしサイロを解消")
    elif daf > 1.2:
        items.append("意思決定条件の言語化とレビュー手順の導入")
    else:
        items.append("KPI運用の定例化と改善ループの高速化")

    # Ensure exactly 3
    return items[:3]
