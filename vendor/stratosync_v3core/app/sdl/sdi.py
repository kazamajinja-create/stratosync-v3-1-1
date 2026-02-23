from __future__ import annotations

from dataclasses import dataclass


def _clamp01(x: float) -> float:
    try:
        x = float(x)
    except Exception:
        x = 0.0
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x


def _norm100(x: float, scale: float = 100.0) -> float:
    """Soft-normalize to 0..100.

    `scale` is a tunable constant per industry pack.
    """
    try:
        x = float(x)
    except Exception:
        x = 0.0
    if scale <= 0:
        scale = 100.0
    v = (x / scale) * 100.0
    if v < 0:
        return 0.0
    if v > 100:
        return 100.0
    return v


@dataclass
class SDIParams:
    """Industry-tunable parameters for SDI."""

    scale: float = 100.0
    w_surface: float = 1.0
    w_network: float = 1.0
    w_amp: float = 1.0


def calculate_sdi(
    *,
    channels: float,
    frequency: float,
    quality: float,
    api_count: float,
    partners: float,
    sns_factor: float,
    brand_exposure: float,
    volume_proxy: float | None = None,
    params: SDIParams | None = None,
) -> dict:
    """Surface Dominance Index (SDI).

    Interprets enterprise value as a function of the *boundary surface*:
    customer touchpoints, distribution interfaces, and network effect.

    All inputs are expected to be non-negative. The function is intentionally
    simple and explainable; industry packs can tune weights and scale.
    """

    p = params or SDIParams()

    # Core components
    surface = max(0.0, float(channels)) * max(0.0, float(frequency)) * max(0.0, float(quality))
    network = max(0.0, float(api_count)) + max(0.0, float(partners))
    amplification = max(0.0, float(sns_factor)) * max(0.0, float(brand_exposure))

    raw = p.w_surface * surface + p.w_network * network + p.w_amp * amplification
    surface_index = _norm100(raw, scale=p.scale)

    # Volume/Surface ratio (optional): if client provides a proxy of internal volume.
    vsr = None
    if volume_proxy is not None:
        try:
            vp = max(0.0, float(volume_proxy))
            vsr = round(vp / (raw + 1e-9), 4) if raw > 0 else None
        except Exception:
            vsr = None

    # Expansion potential: heuristics based on underutilized channels & weak amplification.
    # 0..1 where 1 means high headroom.
    # (This is intentionally conservative and easy to explain.)
    headroom = 0.0
    headroom += (1.0 - _clamp01(quality)) * 0.35
    headroom += (1.0 - _clamp01(sns_factor)) * 0.35
    headroom += (1.0 - _clamp01(brand_exposure)) * 0.30
    headroom = _clamp01(headroom)

    return {
        "surface_index": round(surface_index, 2),
        "surface_components": {
            "surface": round(surface, 4),
            "network": round(network, 4),
            "amplification": round(amplification, 4),
            "raw": round(raw, 4),
        },
        "volume_surface_ratio": vsr,
        "surface_expansion_potential": round(headroom, 3),
    }
