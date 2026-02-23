from __future__ import annotations
from dataclasses import dataclass
from typing import List, Literal, Dict
import re

Status = Literal["OK", "WARN", "BLOCK"]

# High-risk phrases for business consulting (JP) that can imply certainty, guarantee, or decision delegation
BLOCK_PATTERNS = [
    r"必ず", r"確実", r"100%|１００％", r"絶対", r"保証", r"断言",
    r"成功する", r"失敗する", r"儲かる", r"勝てる",
    r"あなたは(.*)すべき", r"やるべき", r"正しいのは", r"唯一の答え",
]
WARN_PATTERNS = [
    r"おすすめ", r"推奨", r"結論として", r"最適解", r"間違いない",
    r"こうすれば", r"これで", r"この通りに",
]

@dataclass
class Finding:
    level: Literal["WARN","BLOCK"]
    pattern: str
    snippet: str

@dataclass
class QualityResult:
    status: Status
    findings: List[Finding]

def _scan(text: str, patterns: List[str], level: Literal["WARN","BLOCK"]) -> List[Finding]:
    findings: List[Finding] = []
    for pat in patterns:
        for m in re.finditer(pat, text):
            start = max(0, m.start() - 24)
            end = min(len(text), m.end() + 24)
            snippet = text[start:end].replace("\n"," ")
            findings.append(Finding(level=level, pattern=pat, snippet=snippet))
    return findings

def evaluate(text: str) -> QualityResult:
    """
    Guardrail:
    - BLOCK: guarantee / prediction / decision delegation
    - WARN: recommendation wording that may need rephrasing into 'considerations'
    """
    if not text:
        return QualityResult(status="OK", findings=[])
    findings = []
    findings += _scan(text, BLOCK_PATTERNS, "BLOCK")
    findings += _scan(text, WARN_PATTERNS, "WARN")
    status: Status = "OK"
    if any(f.level=="BLOCK" for f in findings):
        status = "BLOCK"
    elif any(f.level=="WARN" for f in findings):
        status = "WARN"
    return QualityResult(status=status, findings=findings)

def findings_to_text(q: QualityResult) -> str:
    if q.status == "OK":
        return "品質チェック: OK（断定/推奨の高リスク表現は検出されませんでした）"
    lines = [f"品質チェック: {q.status}（検出件数: {len(q.findings)}）"]
    for f in q.findings[:20]:
        lines.append(f"- [{f.level}] pattern='{f.pattern}' / snippet='{f.snippet}'")
    if len(q.findings) > 20:
        lines.append(f"...（他 {len(q.findings)-20} 件）")
    return "\n".join(lines)
