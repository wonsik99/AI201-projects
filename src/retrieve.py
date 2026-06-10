from __future__ import annotations

from dataclasses import dataclass

import chromadb

from .config import CHROMA_DIR, COLLECTION_NAME, TOP_K
from .embeddings import load_embedding_backend


@dataclass(frozen=True)
class RetrievalResult:
    text: str
    distance: float
    source_name: str
    source_url: str
    title: str
    chunk_index: int


def retrieve(query: str, top_k: int = TOP_K) -> list[RetrievalResult]:
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_collection(COLLECTION_NAME)
    backend = load_embedding_backend()
    query_embedding = backend.encode([query])[0]

    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    rows: list[RetrievalResult] = []
    for text, metadata, distance in zip(
        result["documents"][0],
        result["metadatas"][0],
        result["distances"][0],
    ):
        rows.append(
            RetrievalResult(
                text=text,
                distance=float(distance),
                source_name=str(metadata.get("source_name", "")),
                source_url=str(metadata.get("source_url", "")),
                title=str(metadata.get("title", "")),
                chunk_index=int(metadata.get("chunk_index", 0)),
            )
        )
    return rows


if __name__ == "__main__":
    import sys

    question = " ".join(sys.argv[1:]) or "Which EECS professor gives useful feedback?"
    for item in retrieve(question):
        print("\n---")
        print(f"{item.title} | chunk {item.chunk_index} | distance={item.distance:.3f}")
        print(item.text[:900])
