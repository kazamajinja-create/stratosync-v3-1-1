from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Optional
import datetime

from .industry_risk_dictionary_extended import INDUSTRY_RISK_DICTIONARY_EXTENDED

@dataclass
class TemplateGenResult:
    industry: str
    template_path: str
    created_utc: str

def _industry_title(industry: str) -> str:
    mapping = {
        "manufacturing": "製造業",
        "healthcare": "医療・ヘルスケア",
        "finance": "金融",
        "community_management": "コミュニティ運営",
        "consulting": "コンサルティング",
        "agriculture": "農業",
        "saas": "SaaS",
        "education": "教育",
    }
    return mapping.get(industry, industry)

def generate_industry_template(industry: str, out_dir: str | Path = "outputs/templates", extra_notes: Optional[str] = None) -> TemplateGenResult:
    industry = (industry or "").strip().lower()
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    risk_map = INDUSTRY_RISK_DICTIONARY_EXTENDED.get(industry, {})
    title = _industry_title(industry)
    dt = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    risk_lines = []
    for k, v in sorted(risk_map.items(), key=lambda kv: kv[1], reverse=True):
        risk_lines.append(f"- {k}: weight={v}")

    body = f"""# 業界別テンプレ（{title}）— Non-Decision / Non-Advisory
- created_utc: {dt}
- industry_key: {industry}

## 1. 目的
本テンプレは、当該業界における外部圧力・競争・規制等を『論点』として整理するためのものです。
推奨・決定・成果保証は行いません。

## 2. 事前入力（最小）
- 事業概要（1段落）
- 顧客セグメント（誰に/何を/どう提供）
- 地域（国/都道府県など）
- 主要KPI（最大3つ）
- 直近決算レンジ（売上/粗利/固定費などのレンジで可）

## 3. Market Context（外部環境）
- MVI（マクロ変動性）: [非常に低い/低い/中程度/高い/非常に高い]
- IGM（業界成長モメンタム）: [収縮/横ばい/緩成長/急成長]
- CPI（競争圧力）: [低圧/中圧/高圧]
- RFI（規制摩擦）: [低摩擦/中摩擦/高摩擦]

## 4. 業界特有リスク辞書（重み付き）
{chr(10).join(risk_lines) if risk_lines else "- (未定義) : 必要に応じて辞書を拡張してください"}

## 5. 衝突マップ（Collision Map）
- 内部構造（HSSI/12変数）と外部環境の『衝突点』を列挙
- 上位衝突点は「90日で可逆な実験」に落とす（推奨ではなく論点提示）

## 6. 90日モニタリング（候補）
- 主要KPI: [ ]
- 停止条件: [ ]
- ピボットトリガー: [ ]

## 7. 注意
- 本テンプレは投資助言・会計判断・税務判断・監査意見・法的助言を構成しません。
"""
    if extra_notes:
        body += f"\n\n## 追加メモ\n{extra_notes.strip()}\n"

    out_path = out_dir / f"industry_template_{industry}.md"
    out_path.write_text(body, encoding="utf-8")
    return TemplateGenResult(industry=industry, template_path=str(out_path), created_utc=dt)
