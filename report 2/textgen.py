from __future__ import annotations

def executive_one_liner(surface_power: float, resilience: float, adjusted_risk: float, omega_index: float, se: float) -> str:
    # Simple deterministic narrative template
    parts = []
    if surface_power >= 70:
        parts.append("境界面優位性は高い")
    elif surface_power >= 40:
        parts.append("境界面優位性は標準域")
    else:
        parts.append("境界面優位性は弱い")

    if omega_index < 40:
        parts.append("組織接続が不足しサイロ化の兆候")
    elif omega_index < 70:
        parts.append("組織接続は改善余地あり")
    else:
        parts.append("組織接続は良好")

    if adjusted_risk >= 70:
        parts.append("実効リスクが高い")
    elif adjusted_risk >= 40:
        parts.append("実効リスクは中程度")
    else:
        parts.append("実効リスクは低い")

    if resilience >= 70:
        parts.append("耐性は強い")
    elif resilience >= 40:
        parts.append("耐性は標準")
    else:
        parts.append("耐性は脆弱")

    return " / ".join(parts) + "。"
