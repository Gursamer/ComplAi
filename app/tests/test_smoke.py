from __future__ import annotations

import unittest
from pathlib import Path

from app.pipeline.extract_clauses import extract_clauses
from app.pipeline.rag_match import match_clauses_to_gdpr
from app.pipeline.report import create_report
from app.pipeline.risk_score import score_risks
from app.pipeline.suggest_fixes import suggest_fixes
from app.rag.build_index import build_index
from app.utils.hashing import sha256_text
from app.utils.pdf_text import extract_pdf_text


SAMPLE_PDF = Path("data/samples/contracts/sample_vendor_agreement.pdf")


class SmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        build_index()
        raw_text = extract_pdf_text(SAMPLE_PDF)
        cls.clauses = extract_clauses(raw_text)
        cls.matches = match_clauses_to_gdpr(cls.clauses)
        cls.risks = score_risks(cls.clauses, cls.matches)
        cls.fixes = suggest_fixes(cls.clauses, cls.matches, cls.risks)
        cls.doc_hash = sha256_text(raw_text)[:16]

    def test_extract_returns_at_least_five_clauses(self) -> None:
        self.assertGreaterEqual(len(self.clauses), 5)

    def test_rag_returns_match_for_each_clause(self) -> None:
        by_clause = {}
        for match in self.matches:
            by_clause.setdefault(match.clause_id, 0)
            by_clause[match.clause_id] += 1

        for clause in self.clauses:
            self.assertGreaterEqual(by_clause.get(clause.clause_id, 0), 1)

    def test_report_schema_shape(self) -> None:
        report = create_report(
            source_file=str(SAMPLE_PDF),
            document_hash=self.doc_hash,
            clauses=self.clauses,
            matches=self.matches,
            risks=self.risks,
            fixes=self.fixes,
        )
        payload = report.to_dict()
        self.assertIn("clauses", payload)
        self.assertIn("gdpr_matches", payload)
        self.assertIn("risk_scores", payload)
        self.assertIn("suggested_fixes", payload)
        self.assertIn("executive_summary", payload)
        self.assertEqual(payload["document_hash"], self.doc_hash)


if __name__ == "__main__":
    unittest.main()
