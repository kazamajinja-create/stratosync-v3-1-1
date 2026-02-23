from __future__ import annotations
from typing import Dict, Any
from .collision_model import band_collision
from .config import DEFAULT_THRESHOLDS

def generate_strategic_priorities(ci: float, thresholds=DEFAULT_THRESHOLDS) -> Dict[str, Any]:
    band = band_collision(ci, thresholds=thresholds)
    # no recommendations; just "collision points"
    guidance = {
        "衝突優先度レベル1": ["衝突点を分解し、90日で可逆な実験に落とし込む", "説明責任（外部/内部）の論点化を優先する"],
        "衝突優先度レベル2": ["集中点/固定費/競争圧のどこが増幅しているかを可視化する", "KPIを絞って監視する"],
        "衝突優先度レベル3": ["現状維持の前提条件を明確化し、変化検知のトリガーを設定する"],
    }
    return {
        "band": band,
        "collision_points": guidance.get(band, []),
        "notes": ["推奨ではありません。選択肢空間の整理のための論点提示です。"],
    }
