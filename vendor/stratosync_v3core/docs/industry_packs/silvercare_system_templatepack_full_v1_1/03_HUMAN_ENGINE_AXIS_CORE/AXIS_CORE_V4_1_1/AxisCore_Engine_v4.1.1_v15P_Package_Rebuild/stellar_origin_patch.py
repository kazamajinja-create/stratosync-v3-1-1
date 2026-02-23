"""stellar_origin_patch.py

魂解析における「恒星由来（Stellar Origin / Soul Goal）」を
出生情報から **決定的（deterministic）** に確定させるためのパッチ。

狙い
----
同一の出生情報（dob/tob/pob）が固定なのに、実行ごとに恒星由来が入れ替わると、
"魂ゴール"としての信用性が崩れます。

本パッチは、恒星由来を「スコア最大値」ではなく、
出生情報→ハッシュ→恒星（候補リスト）という *一意マッピング* にします。

さらに、同じ出生情報から導出した seed を提供し、
下流の乱数（random）を固定するのにも使えます。

導入（最小改修）
----------------
1) パイプラインの入口で:

    from stellar_origin_patch import apply_fixed_star
    ctx = apply_fixed_star(ctx)

2) レポート/テンプレ分岐は ctx['fixed_star'] を参照

3) 乱数を固定したい場合:
    - random.seed(ctx['seed']) ではなく、できれば rng = seeded_rng(ctx['seed']) を使う

注意
----
このパッチは「恒星由来＝固定ゴール」という運用前提のためのものです。
"現在の共鳴星"（Active Star）も併記したい場合は、別レイヤーで算出し、
ctx['active_star'] として持たせるのが安全です。
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


DEFAULT_STARS: List[str] = [
    # よく使われる「魂起源」ラベル（必要に応じて増減してOK）
    "Arcturus",
    "Vega",
    "Sirius",
    "Capella",
    "Pleiades",
    "Rigel",
    "Polaris",
    "Deneb",
    "Altair",
]


def _norm(s: Optional[str]) -> str:
    if not s:
        return ""
    s = str(s).strip()
    # 余計な空白・全角空白・連続スペースを潰す
    s = s.replace("\u3000", " ")
    s = re.sub(r"\s+", " ", s)
    return s


def birth_fingerprint(dob: str, tob: Optional[str] = None, pob: Optional[str] = None) -> str:
    """出生情報の正規化 fingerprint（決定的）"""
    return "|".join([_norm(dob), _norm(tob), _norm(pob)])


def seed_from_birth(dob: str, tob: Optional[str] = None, pob: Optional[str] = None, salt: str = "SENJYU_FIXED_SEED") -> str:
    fp = birth_fingerprint(dob, tob, pob)
    return hashlib.sha256((salt + "|" + fp).encode("utf-8")).hexdigest()


def resolve_fixed_star(
    dob: str,
    tob: Optional[str] = None,
    pob: Optional[str] = None,
    *,
    stars: Optional[List[str]] = None,
    salt: str = "SENJYU_FIXED_STAR_V1",
) -> str:
    """出生情報から固定恒星（固定ゴール）を決定。

    - stars の順序が変わると割当も変わるため、運用で固定してください。
    - 恒星リストを変更する場合は "version" を上げるのがおすすめ。
    """
    stars = stars or DEFAULT_STARS
    if not stars:
        raise ValueError("stars list is empty")
    fp = birth_fingerprint(dob, tob, pob)
    h = hashlib.sha256((salt + "|" + fp).encode("utf-8")).hexdigest()
    # 先頭8桁→ 0..2^32-1
    n = int(h[:8], 16)
    return stars[n % len(stars)]


def apply_fixed_star(ctx: Dict, *, stars: Optional[List[str]] = None) -> Dict:
    """ctxに fixed_star / seed / star_band を注入して返す（破壊的変更あり）"""

    - fixed_star: 魂ゴールとして扱う"固定恒星"
    - seed:      再現性担保のための出生由来 seed（hex）
    - star_band: 主峰/副峰/帯域幅（僅差帯の可視化）。表示や後段の加重平均に利用可能。
    """
    dob = ctx.get("dob") or ""
    tob = ctx.get("tob")
    pob = ctx.get("pob")

    ctx["fixed_star"] = resolve_fixed_star(dob, tob, pob, stars=stars)
    ctx["seed"] = seed_from_birth(dob, tob, pob)

    # Multi-peak / band information (deterministic)
    try:
        ctx["star_band"] = resolve_star_band(dob, tob, pob, stars=stars)
    except Exception:
        ctx["star_band"] = None

    return ctx

def seeded_rng(seed_hex: str):
    """hex seed → random.Random を返す（グローバル random を汚さない）"""
    import random

    # python の random は int seed が扱いやすい
    n = int(seed_hex[:16], 16)
    return random.Random(n)



# ------------------------------
# Star Band / Multi-Peak support
# ------------------------------

def _hash_to_unit_float(hex_str: str) -> float:
    """sha256 hexdigest -> [0,1) using first 8 hex chars."""
    n = int(hex_str[:8], 16)
    return n / 0xffffffff


def score_stars_from_birth(
    dob: str,
    tob: Optional[str] = None,
    pob: Optional[str] = None,
    *,
    stars: Optional[List[str]] = None,
    salt: str = "SENJYU_STAR_SCORE_V1",
) -> List[Tuple[str, float]]:
    """出生情報から恒星候補の相対スコアを決定的に生成（再現性担保）。

    目的:
      - 「僅差帯（共鳴帯）」の可視化（主峰/副峰/帯域幅）
      - 実行ごとのブレを抑えつつ、"近い星が複数ある" という構造を表現

    注意:
      - ここでの score は"物理的真値"ではなく、内部の相対ランキング用指標。
      - stars の順序を変えても score 自体は変わりません（各星を個別にハッシュ化するため）。
    """
    stars = stars or DEFAULT_STARS
    fp = birth_fingerprint(dob, tob, pob)
    base = hashlib.sha256((salt + "|" + fp).encode("utf-8")).hexdigest()
    out: List[Tuple[str, float]] = []
    for s in stars:
        h = hashlib.sha256((base + "|" + s).encode("utf-8")).hexdigest()
        out.append((s, round(_hash_to_unit_float(h), 6)))
    # high to low
    out.sort(key=lambda x: x[1], reverse=True)
    return out


def resolve_star_band(
    dob: str,
    tob: Optional[str] = None,
    pob: Optional[str] = None,
    *,
    stars: Optional[List[str]] = None,
    close_threshold: float = 0.02,
    band_threshold: float = 0.03,
) -> Dict:
    """主峰（Primary）、副峰（Secondary）、帯域幅（Bandwidth）を返す。

    - close_threshold:
        Top1 と Top2 の差（margin）がこれ未満なら「僅差＝入れ替わり得る」帯域。
    - band_threshold:
        Top1 から band_threshold 以内に入る星を "band members" として列挙。

    戻り値例:
      {
        "primary_peak": "Arcturus",
        "secondary_peak": "Sirius",
        "scores": [("Arcturus",0.84),("Sirius",0.83),...],
        "margin": 0.012,
        "is_close": True,
        "confidence": "LOW",
        "band_members": ["Arcturus","Sirius","Vega"],
        "bandwidth": 3
      }
    """
    scored = score_stars_from_birth(dob, tob, pob, stars=stars)
    if not scored:
        raise ValueError("No stars to score")
    primary, p1 = scored[0]
    secondary, p2 = scored[1] if len(scored) > 1 else (primary, p1)
    margin = round(p1 - p2, 6)

    is_close = margin < close_threshold

    # confidence as display policy
    if margin >= 0.05:
        confidence = "HIGH"
    elif margin >= 0.02:
        confidence = "MEDIUM"
    else:
        confidence = "LOW"

    band_members = [s for (s, sc) in scored if (p1 - sc) <= band_threshold]
    bandwidth = len(band_members)

    return {
        "primary_peak": primary,
        "secondary_peak": secondary,
        "scores": scored,
        "margin": margin,
        "is_close": is_close,
        "confidence": confidence,
        "band_members": band_members,
        "bandwidth": bandwidth,
    }
