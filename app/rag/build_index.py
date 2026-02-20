from __future__ import annotations

import json
from pathlib import Path

from app.config import settings
from app.rag.gdpr_chunks import build_gdpr_chunks
from app.utils.embeddings import embed_texts


COLLECTION = "gdpr_chunks"
FALLBACK_INDEX = "gdpr_index.json"


def load_chunks(chunks_path: str | Path = "data/regulations/gdpr/chunks.jsonl") -> list[dict]:
    path = Path(chunks_path)
    if not path.exists():
        raise FileNotFoundError(f"Missing chunks file: {path}")
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rows.append(json.loads(line))
    return rows


def build_index() -> int:
    settings.chroma_path.mkdir(parents=True, exist_ok=True)
    build_gdpr_chunks()

    chunks = load_chunks()
    docs = [c["text"] for c in chunks]
    ids = [c["id"] for c in chunks]
    metadatas = [{"article": c["article"], "topic": c["topic"], "source": c["source"]} for c in chunks]
    embeddings = embed_texts(docs)

    try:
        import chromadb

        client = chromadb.PersistentClient(path=str(settings.chroma_path))
        try:
            client.delete_collection(COLLECTION)
        except Exception:
            pass

        collection = client.create_collection(name=COLLECTION)
        collection.add(ids=ids, documents=docs, metadatas=metadatas, embeddings=embeddings)
    except Exception:
        fallback_path = settings.chroma_path / FALLBACK_INDEX
        payload = []
        for idx, doc, meta, emb in zip(ids, docs, metadatas, embeddings):
            payload.append({"id": idx, "document": doc, "metadata": meta, "embedding": emb})
        fallback_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return len(ids)


if __name__ == "__main__":
    count = build_index()
    print(f"Indexed GDPR chunks: {count}")
