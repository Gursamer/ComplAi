from __future__ import annotations

import json
from pathlib import Path

from app.schemas import Clause, ExecutiveSummary, GDPRMatch, PipelineReport, RiskResult, SuggestedFix


def build_executive_summary(risks: list[RiskResult]) -> ExecutiveSummary:
    if not risks:
        return ExecutiveSummary(
            overall_risk_score=0,
            total_clauses=0,
            high_risk_clauses=0,
            key_findings=["No clauses detected."],
        )

    overall = round(sum(r.risk_score for r in risks) / len(risks))
    high = sum(1 for r in risks if r.severity == "high")
    findings = []
    for r in sorted(risks, key=lambda x: x.risk_score, reverse=True)[:3]:
        findings.append(f"{r.clause_id}: score={r.risk_score}, issues={'; '.join(r.issues[:2])}")

    return ExecutiveSummary(
        overall_risk_score=overall,
        total_clauses=len(risks),
        high_risk_clauses=high,
        key_findings=findings,
    )


def create_report(
    source_file: str,
    document_hash: str,
    clauses: list[Clause],
    matches: list[GDPRMatch],
    risks: list[RiskResult],
    fixes: list[SuggestedFix],
) -> PipelineReport:
    return PipelineReport(
        source_file=source_file,
        document_hash=document_hash,
        clauses=clauses,
        gdpr_matches=matches,
        risk_scores=risks,
        suggested_fixes=fixes,
        executive_summary=build_executive_summary(risks),
    )


def save_report(report: PipelineReport, out_dir: str | Path) -> Path:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{report.document_hash}.json"
    path.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
    return path
