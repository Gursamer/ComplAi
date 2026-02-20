from __future__ import annotations

import hashlib


def sha256_text(content: str) -> str:
    text = content if isinstance(content, str) else str(content)
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()
