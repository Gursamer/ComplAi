from __future__ import annotations

from app.schemas import Clause, GDPRMatch, RiskResult


HIGH_RISK_TERMS = ("sell", "share with any third party", "unlimited", "without notice")
LOW_CONF_TERMS = ("reasonable", "best effort", "as needed", "commercially reasonable")


def score_risks(clauses: list[Clause], matches: list[GDPRMatch]) -> list[RiskResult]:
    match_map: dict[str, list[GDPRMatch]] = {}
    for m in matches:
        match_map.setdefault(m.clause_id, []).append(m)

    results: list[RiskResult] = []
    for clause in clauses:
        text = clause.text.lower()
        score = 20
        issues: list[str] = []

        if "breach" in text and "72" not in text:
            score += 25
            issues.append("Breach clause does not mention 72-hour notification window (GDPR Art. 33).")

        if "security" in text and "encryption" not in text and "access control" not in text:
            score += 20
            issues.append("Security obligations may be too vague for GDPR Art. 32.")

        if any(term in text for term in HIGH_RISK_TERMS):
            score += 20
            issues.append("Overly broad data use/sharing language detected.")

        if any(term in text for term in LOW_CONF_TERMS):
            score += 10
            issues.append("Ambiguous wording may reduce enforceability.")

        top_match = sorted(match_map.get(clause.clause_id, []), key=lambda x: x.similarity_score, reverse=True)
        if not top_match or top_match[0].similarity_score < 0.25:
            score += 15
            issues.append("Weak GDPR alignment based on semantic match.")

        score = max(0, min(100, score))
        severity = "low"
        if score >= 70:
            severity = "high"
        elif score >= 40:
            severity = "medium"

        if not issues:
            issues.append("No significant GDPR risks detected by MVP rule set.")

        results.append(RiskResult(clause_id=clause.clause_id, risk_score=score, issues=issues, severity=severity))

    return results
