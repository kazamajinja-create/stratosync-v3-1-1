from __future__ import annotations
from typing import Dict

def scope_text() -> str:
    return """【別紙：業務内容（Ω量子コンサルティング）】
本業務は、Ωシステムによる量子ロジック解析レポートを起点として、
意思決定・構造選択のための情報整理、構造の可視化、視点・問いの提示を行う。
なお、未来予測や結果断定、意思決定の代行は行わない。"""

def disclaimer_text() -> str:
    return """【免責】
本コンサルティングは意思決定を支援するためのものであり、
特定の成果・利益・成功を保証するものではない。
最終的な判断およびその結果に関する責任は、すべてクライアントに帰属する。"""

def not_do_text() -> str:
    return """【行わないこと】
・決断の代行
・成果/利益/成功の保証
・精神的依存を生む関与
・判断責任の肩代わり"""

def build_contract_pack() -> Dict[str, str]:
    return {
        "scope": scope_text(),
        "disclaimer": disclaimer_text(),
        "not_do": not_do_text(),
    }
