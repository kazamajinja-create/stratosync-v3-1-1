from __future__ import annotations
from typing import Dict

def grounding(duration: int = 180) -> Dict:
    return {
        "duration_sec": duration,
        "purpose": "解析結果を歪めずに扱える認知状態を一時的につくる",
        "script": [
            "目を閉じる（可能なら）。背筋だけ伸ばす。",
            "呼吸を数える（吸う1〜4 / 吐く1〜6 を3回）。",
            "身体の接地感（足裏/椅子）に注意を戻す。",
            "今のテーマを一文で心の中で言い、手放す。",
        ],
        "policy": "習慣化・宿題化はしない。必要時のみ使用。"
    }

def reset(duration: int = 240) -> Dict:
    return {
        "duration_sec": duration,
        "purpose": "防衛反応・過緊張を一時的に緩め、論点を戻す",
        "script": [
            "視線を一点に置き、周辺視野を広げる。",
            "肩を上げて3秒キープ→脱力を3回。",
            "『いま判断する必要はない。構造だけ見る』と一度だけ言う。",
        ],
        "policy": "感情浄化やトラウマ掘りを目的にしない。"
    }
