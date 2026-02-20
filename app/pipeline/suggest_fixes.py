from __future__ import annotations

from app.schemas import Clause, GDPRMatch, RiskResult, SuggestedFix


def suggest_fixes(
    clauses: list[Clause],
    matches: list[GDPRMatch],
    risks: list[RiskResult],
) -> list[SuggestedFix]:
    clause_map = {c.clause_id: c for c in clauses}
    match_map: dict[str, list[GDPRMatch]] = {}
    for m in matches:
        match_map.setdefault(m.clause_id, []).append(m)

    suggestions: list[SuggestedFix] = []
    for risk in risks:
        if risk.risk_score < 40:
            continue

        clause = clause_map[risk.clause_id]
        linked = sorted(match_map.get(risk.clause_id, []), key=lambda x: x.similarity_score, reverse=True)[:3]
        articles = sorted({m.article for m in linked}) or ["Article 32", "Article 33"]

        base_text = clause.text.strip()
        proposed = (
            "The parties shall implement appropriate technical and organizational measures, "
            "including encryption and access controls, to ensure a level of security appropriate "
            "to risk. Personal data breaches will be notified without undue delay and, where required, "
            "within 72 hours. Processing is limited to documented instructions and GDPR-compliant purposes."
        )
        if len(base_text) > 0 and len(base_text) < 350:
            proposed = f"{proposed} Existing clause context: {base_text[:120]}."

        suggestions.append(
            SuggestedFix(
                clause_id=risk.clause_id,
                rationale="Addresses flagged risk issues with clearer GDPR-aligned obligations.",
                referenced_articles=articles,
                suggested_text=proposed,
            )
        )

    return suggestions
