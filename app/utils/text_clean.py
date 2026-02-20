from __future__ import annotations

import re


def normalize_text(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[\t ]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    cleaned_lines: list[str] = []
    for line in text.split("\n"):
        s = line.strip()
        if not s:
            cleaned_lines.append("")
            continue
        if re.match(r"^\d{1,2}/\d{1,2}/\d{2,4},\s+\d{1,2}:\d{2}\s+[AP]M\b", s):
            continue
        if re.match(r"^https?://\S+$", s):
            continue
        if re.match(r"^\d+/\d+\s*$", s):
            continue
        if s in {"TRY GROK", "TRY GROK ON", "Web", "iOS", "Android"}:
            continue
        cleaned_lines.append(line)
    text = "\n".join(cleaned_lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _is_heading_line(line: str) -> bool:
    s = line.strip()
    if not s:
        return False

    if re.match(r"^\d{1,2}(?:\.\d+)?[.)]\s+\S", s):
        return True

    if re.match(r"^[A-Z][A-Za-z0-9,&/'()\- ]{2,70}:?$", s):
        words = s.replace(":", "").split()
        # "Title Case" section headers are common in legal docs and web exports.
        if 1 <= len(words) <= 10 and all(w[:1].isupper() or w.isupper() for w in words if w):
            return True

    if re.match(r"^\d{1,2}/\d{1,2}/\d{2,4},\s+\d{1,2}:\d{2}\s+[AP]M\b", s):
        return True

    if re.match(r"^https?://\S+$", s):
        return True

    if s in {"TRY GROK", "PRODUCTS", "COMPANY", "RESOURCES"}:
        return True

    return False


def _merge_small_blocks(blocks: list[str], min_chars: int) -> list[str]:
    if not blocks:
        return blocks
    merged: list[str] = []
    for block in blocks:
        if merged and len(block) < min_chars:
            merged[-1] = (merged[-1].rstrip() + "\n" + block.lstrip()).strip()
        else:
            merged.append(block)
    return merged


def split_into_clause_like_blocks(text: str, min_chars: int = 60) -> list[str]:
    # First pass: split by heading-like lines (numbered sections, title lines, page markers).
    lines = text.splitlines()
    starts = []
    pos = 0
    for line in lines:
        if _is_heading_line(line):
            starts.append(pos)
        pos += len(line) + 1

    starts = sorted(set(starts))
    if starts:
        spans = starts + [len(text)]
        blocks = []
        for i in range(len(starts)):
            chunk = text[spans[i] : spans[i + 1]].strip()
            if len(chunk) >= min_chars:
                blocks.append(chunk)
        blocks = _merge_small_blocks(blocks, min_chars)
        if blocks:
            return blocks

    # Fallback: paragraph blocks with soft merge.
    para_split = [p.strip() for p in text.split("\n\n") if len(p.strip()) >= min_chars]
    para_split = _merge_small_blocks(para_split, min_chars)
    return para_split
