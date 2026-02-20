from __future__ import annotations

import re
from pathlib import Path


def extract_pdf_text(pdf_path: str | Path) -> str:
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    try:
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        text_parts = []
        for page in reader.pages:
            text_parts.append(page.extract_text() or "")
        text = "\n".join(text_parts).strip()
        if text:
            return text
    except Exception:
        pass

    # Fallback path for malformed or non-standard PDFs.
    raw = path.read_bytes().decode("latin-1", errors="ignore")
    raw = raw.replace("\r\n", "\n").replace("\r", "\n")
    cleaned = re.sub(r"[ \t]+", " ", raw)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    if not cleaned:
        raise ValueError(f"Could not extract text from {path}")
    return cleaned
