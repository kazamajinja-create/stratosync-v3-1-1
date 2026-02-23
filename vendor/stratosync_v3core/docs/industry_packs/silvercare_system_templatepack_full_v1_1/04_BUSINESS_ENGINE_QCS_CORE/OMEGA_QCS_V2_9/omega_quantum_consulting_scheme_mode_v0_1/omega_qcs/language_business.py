from __future__ import annotations
import re
from typing import Iterable

FORBIDDEN = [
    "必ず", "確実に", "100%", "絶対", "保証", "断言", "成功する", "失敗する",
    "〜になる。", "おすすめ", "推奨", "こうすべき"
]

def business_tone(text: str) -> str:
    """
    Convert to business-oriented, non-assertive Japanese.
    Keeps the policy: no prediction, no recommendation, no decision delegation.
    """
    if not text:
        return text

    t = text

    # soften strong modal verbs
    t = t.replace("〜になりやすい。", "〜となる傾向があります。")
    t = t.replace("注意:", "留意点: ")
    t = t.replace("注意：", "留意点: ")
    t = t.replace("慎重に意思決定を進める", "意思決定プロセス上、慎重さが求められる可能性があります")
    t = t.replace("期日・準備の前倒しを検討", "期日・準備の前倒しを論点として整理できます")
    t = t.replace("小さな実験から環境を変える", "小さな検証から環境条件を調整する選択肢があります")
    t = t.replace("今期は加速判断も可", "条件が整う場合は意思決定を前倒しする余地があります")

    # remove explicit recommendation words
    t = t.replace("recommendations", "considerations")
    t = t.replace("おすすめ", "検討観点")
    t = t.replace("推奨", "検討観点")

    # soften sentence ending
    t = re.sub(r"です。$", "です。", t)  # noop but placeholder

    return t

def business_lines(lines: Iterable[str]) -> list[str]:
    return [business_tone(x) for x in lines]
