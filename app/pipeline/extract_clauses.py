from __future__ import annotations

import re
from typing import Iterable

from app.schemas import Clause
from app.utils.text_clean import normalize_text, split_into_clause_like_blocks


KEYWORDS = {
    "security": "Security",
    "breach": "Breach Notification",
    "processor": "Processor Obligations",
    "subprocessor": "Subprocessor",
    "retention": "Data Retention",
    "transfer": "International Transfer",
    "legal basis": "Legal Basis",
    "consent": "Consent",
    "rights": "Data Subject Rights",
    "audit": "Audit",
}


def _categorize(text: str) -> str:
    lower = text.lower()
    for key, category in KEYWORDS.items():
        if key in lower:
            return category
    return "General"


def _title_for_block(block: str, idx: int) -> str:
    line = block.split("\n", 1)[0].strip()
    line = re.sub(r"^\d+(?:\.\d+)?[.)]\s*", "", line)
    line = line[:80].strip(" :.-")
    return line if len(line) >= 5 else f"Clause {idx}"


def extract_clauses(raw_text: str) -> list[Clause]:
    text = normalize_text(raw_text)
    blocks = split_into_clause_like_blocks(text)

    if not blocks:
        blocks = [text]

    clauses: list[Clause] = []
    for i, block in enumerate(blocks, start=1):
        clause_id = f"C{i:03d}"
        clauses.append(
            Clause(
                clause_id=clause_id,
                title=_title_for_block(block, i),
                category=_categorize(block),
                text=block,
            )
        )
    return clauses


def to_dicts(clauses: Iterable[Clause]) -> list[dict]:
    return [c.to_dict() for c in clauses]
