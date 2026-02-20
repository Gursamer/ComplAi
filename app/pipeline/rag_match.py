from __future__ import annotations

import json
from pathlib import Path

from app.config import settings
from app.schemas import Clause, GDPRMatch
from app.utils.embeddings import embed_texts


COLLECTION = "gdpr_chunks"
FALLBACK_INDEX = "gdpr_index.json"


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    if na == 0 or nb == 0:
        return 0.0
    return max(0.0, min(1.0, dot / (na * nb)))


def _fallback_match(clauses: list[Clause], top_k: int) -> list[GDPRMatch]:
    path = Path(settings.chroma_path) / FALLBACK_INDEX
    if not path.exists():
        raise FileNotFoundError(
            f"RAG index not found at {path}. Run `python -m app.rag.build_index` first."
        )
    rows = json.loads(path.read_text(encoding="utf-8"))
    clause_embeddings = embed_texts([c.text for c in clauses])
    results: list[GDPRMatch] = []

    for clause, emb in zip(clauses, clause_embeddings):
        ranked = sorted(
            rows,
            key=lambda r: _cosine_similarity(emb, r.get("embedding", [])),
            reverse=True,
        )[:top_k]

        for row in ranked:
            meta = row.get("metadata", {})
            sim = _cosine_similarity(emb, row.get("embedding", []))
            results.append(
                GDPRMatch(
                    clause_id=clause.clause_id,
                    article=str(meta.get("article", "Unknown")),
                    topic=str(meta.get("topic", "unknown")),
                    snippet=str(row.get("document", ""))[:280],
                    similarity_score=round(sim, 4),
                )
            )

    return results


def match_clauses_to_gdpr(clauses: list[Clause], top_k: int | None = None) -> list[GDPRMatch]:
    top_k = top_k or settings.clause_top_k
    try:
        import chromadb

        client = chromadb.PersistentClient(path=str(settings.chroma_path))
        collection = client.get_collection(COLLECTION)

        clause_texts = [c.text for c in clauses]
        clause_embeddings = embed_texts(clause_texts)

        results: list[GDPRMatch] = []
        query = collection.query(
            query_embeddings=clause_embeddings,
            n_results=top_k,
            include=["metadatas", "documents", "distances"],
        )

        for idx, clause in enumerate(clauses):
            docs = query.get("documents", [[]])[idx]
            metas = query.get("metadatas", [[]])[idx]
            distances = query.get("distances", [[]])[idx]

            for doc, meta, dist in zip(docs, metas, distances):
                similarity = max(0.0, min(1.0, 1.0 - float(dist)))
                results.append(
                    GDPRMatch(
                        clause_id=clause.clause_id,
                        article=str(meta.get("article", "Unknown")),
                        topic=str(meta.get("topic", "unknown")),
                        snippet=doc[:280],
                        similarity_score=round(similarity, 4),
                    )
                )

        return results
    except Exception:
        return _fallback_match(clauses, top_k)
