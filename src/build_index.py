from __future__ import annotations

import chromadb

from .chunking import chunk_documents
from .config import CHROMA_DIR, COLLECTION_NAME
from .embeddings import load_embedding_backend
from .ingest import load_documents


def rebuild_index() -> int:
    documents = load_documents()
    chunks = chunk_documents(documents)
    if not chunks:
        raise SystemExit("No chunks found. Add .txt source documents to documents/ first.")

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    backend = load_embedding_backend()
    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine", "embedding_backend": backend.name},
    )
    embeddings = backend.encode([chunk.text for chunk in chunks])

    collection.add(
        ids=[chunk.id for chunk in chunks],
        documents=[chunk.text for chunk in chunks],
        metadatas=[
            {
                "source_name": chunk.source_name,
                "source_url": chunk.source_url,
                "title": chunk.title,
                "chunk_index": chunk.chunk_index,
            }
            for chunk in chunks
        ],
        embeddings=embeddings,
    )
    return len(chunks)


if __name__ == "__main__":
    count = rebuild_index()
    print(f"Indexed {count} chunks into {CHROMA_DIR}")
