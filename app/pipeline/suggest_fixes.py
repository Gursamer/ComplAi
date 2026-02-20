from __future__ import annotations

from app.schemas import Clause, GDPRMatch, RiskResult, SuggestedFix


ARTICLE_GUIDANCE = {
    "Article 28": "processing under documented controller instructions and equivalent subprocessor obligations",
    "Article 32": "appropriate technical and organizational security measures (for example encryption and access controls)",
    "Article 33": "breach notification without undue delay and, where required, within 72 hours",
    "Article 5": "purpose limitation, data minimization, and storage limitation principles",
    "Article 6": "clear lawful basis for processing operations",
}


def _article_line(article: str) -> str:
    guidance = ARTICLE_GUIDANCE.get(article, "explicit GDPR-aligned controls tied to the clause scope")
    return f"{article}: add language on {guidance}."


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
        article_lines = " ".join(_article_line(article) for article in articles)

        base_text = clause.text.strip()
        proposed = (
            f"Replace clause with GDPR-grounded language. {article_lines} "
            "Use measurable obligations, explicit timelines, and controller-approval controls for subprocessors."
        )
        if len(base_text) > 0 and len(base_text) < 350:
            proposed = f"{proposed} Existing clause context: {base_text[:120]}."

        suggestions.append(
            SuggestedFix(
                clause_id=risk.clause_id,
                rationale="Grounded in top RAG-matched GDPR articles for this clause.",
                referenced_articles=articles,
                suggested_text=proposed,
            )
        )

    return suggestions
