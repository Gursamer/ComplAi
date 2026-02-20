from __future__ import annotations

import hashlib
from typing import Iterable

from app.config import settings


_EMBED_DIM = 128


def _hash_embedding(text: str, dim: int = _EMBED_DIM) -> list[float]:
    vec = [0.0] * dim
    for token in text.lower().split():
        h = int(hashlib.sha256(token.encode("utf-8")).hexdigest(), 16)
        idx = h % dim
        sign = -1.0 if (h >> 8) % 2 else 1.0
        vec[idx] += sign
    norm = sum(v * v for v in vec) ** 0.5
    if norm == 0:
        return vec
    return [v / norm for v in vec]


def embed_texts(texts: Iterable[str]) -> list[list[float]]:
    text_list = list(texts)
    if not text_list:
        return []

    if settings.openai_api_key:
        try:
            from openai import OpenAI

            client = OpenAI(api_key=settings.openai_api_key)
            response = client.embeddings.create(model=settings.model_embed, input=text_list)
            return [row.embedding for row in response.data]
        except Exception:
            pass

    return [_hash_embedding(t) for t in text_list]
