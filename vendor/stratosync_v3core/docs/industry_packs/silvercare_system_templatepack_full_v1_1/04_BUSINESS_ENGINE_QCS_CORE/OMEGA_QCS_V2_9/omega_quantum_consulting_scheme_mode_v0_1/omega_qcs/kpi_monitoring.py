from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class KPIMonitoringPlan:
    horizon_days: int
    kpis: List[str]
    check_frequency: str
    stop_conditions: List[str]
    pivot_triggers: List[str]
    notes: List[str]

def design_kpi_monitoring(structure: Dict[str, str], indices: Dict[str, str], option_space: Optional[Dict] = None) -> KPIMonitoringPlan:
    option_space = option_space or {}
    kpis = [
        "主要KPI（売上/継続/参加/稼働など）を1-3個に限定して追う",
        "変動が大きい場合は週次でトレンドを見る（単発値で判断しない）",
        "外部説明指標（問い合わせ/離脱/不信兆候）を併記できる",
    ]
    stop_conditions = [
        "90日で前提条件が崩れた場合（市場/人/資金/運用）",
        "副作用が想定以上に顕在化した場合（信頼毀損・運用破綻など）",
    ]
    pivot_triggers = [
        "短期傾向が連続して逆向きに出た場合（仮説修正）",
        "集中点がリスク化した場合（分散/分離の検討が必要になる）",
    ]
    notes = [
        "本設計は『測り方の候補』であり、推奨・義務ではありません。",
        "会計/税務上の取り扱いは、社内方針・専門家レビューに従ってください。",
    ]
    return KPIMonitoringPlan(90, kpis, "weekly", stop_conditions, pivot_triggers, notes)
