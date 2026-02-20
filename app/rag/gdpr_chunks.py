from __future__ import annotations

import json
from pathlib import Path

from app.utils.text_clean import normalize_text


def build_gdpr_chunks(
    source_dir: str | Path = "data/regulations/gdpr/source",
    out_path: str | Path = "data/regulations/gdpr/chunks.jsonl",
    chunk_size: int = 700,
    overlap: int = 120,
) -> int:
    src = Path(source_dir)
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    files = sorted(src.glob("*.txt"))
    if not files:
        raise FileNotFoundError(f"No GDPR source files found in {src}")

    lines: list[str] = []
    for file in files:
        article = file.stem.replace("gdpr_", "").replace("_", " ").title()
        text = normalize_text(file.read_text(encoding="utf-8"))

        start = 0
        chunk_idx = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk_text = text[start:end].strip()
            if chunk_text:
                obj = {
                    "id": f"{file.stem}_{chunk_idx}",
                    "text": chunk_text,
                    "article": article,
                    "topic": file.stem.replace("gdpr_", "").replace("_", "-"),
                    "source": str(file),
                }
                lines.append(json.dumps(obj, ensure_ascii=True))
                chunk_idx += 1
            if end == len(text):
                break
            start = max(0, end - overlap)

    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(lines)
