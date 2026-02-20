from __future__ import annotations

import argparse

from app.config import settings
from app.pipeline.extract_clauses import extract_clauses
from app.pipeline.rag_match import match_clauses_to_gdpr
from app.pipeline.report import create_report, save_report
from app.pipeline.risk_score import score_risks
from app.pipeline.suggest_fixes import suggest_fixes
from app.utils.hashing import sha256_text
from app.utils.pdf_text import extract_pdf_text


def run(file_path: str) -> str:
    raw_text = extract_pdf_text(file_path)
    doc_hash = sha256_text(raw_text)[:16]

    clauses = extract_clauses(raw_text)
    matches = match_clauses_to_gdpr(clauses)
    risks = score_risks(clauses, matches)
    fixes = suggest_fixes(clauses, matches, risks)

    report = create_report(
        source_file=file_path,
        document_hash=doc_hash,
        clauses=clauses,
        matches=matches,
        risks=risks,
        fixes=fixes,
    )
    path = save_report(report, settings.report_path)
    return str(path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run ComplyAI Week 1 pipeline")
    parser.add_argument("--file", required=True, help="Path to PDF file")
    args = parser.parse_args()

    output_path = run(args.file)
    print(f"Report generated: {output_path}")


if __name__ == "__main__":
    main()
