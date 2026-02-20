from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class Clause:
    clause_id: str
    title: str
    category: str
    text: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class GDPRMatch:
    clause_id: str
    article: str
    topic: str
    snippet: str
    similarity_score: float

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RiskResult:
    clause_id: str
    risk_score: int
    issues: list[str]
    severity: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SuggestedFix:
    clause_id: str
    rationale: str
    referenced_articles: list[str]
    suggested_text: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ExecutiveSummary:
    overall_risk_score: int
    total_clauses: int
    high_risk_clauses: int
    key_findings: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class PipelineReport:
    source_file: str
    document_hash: str
    clauses: list[Clause]
    gdpr_matches: list[GDPRMatch]
    risk_scores: list[RiskResult]
    suggested_fixes: list[SuggestedFix]
    executive_summary: ExecutiveSummary

    def to_dict(self) -> dict:
        return {
            "source_file": self.source_file,
            "document_hash": self.document_hash,
            "clauses": [c.to_dict() for c in self.clauses],
            "gdpr_matches": [m.to_dict() for m in self.gdpr_matches],
            "risk_scores": [r.to_dict() for r in self.risk_scores],
            "suggested_fixes": [s.to_dict() for s in self.suggested_fixes],
            "executive_summary": self.executive_summary.to_dict(),
        }
