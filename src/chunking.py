from __future__ import annotations

from dataclasses import dataclass

from .config import CHUNK_OVERLAP_CHARS, CHUNK_SIZE_CHARS
from .ingest import SourceDocument, load_documents


@dataclass(frozen=True)
class Chunk:
    id: str
    text: str
    source_name: str
    source_url: str
    title: str
    chunk_index: int


def _paragraphs(text: str) -> list[str]:
    return [p.strip() for p in text.split("\n\n") if p.strip()]


def _overlap_tail(text: str, overlap: int) -> str:
    if overlap <= 0:
        return ""

    paragraphs = _paragraphs(text)
    tail = ""
    for paragraph in reversed(paragraphs):
        candidate = paragraph if not tail else f"{paragraph}\n\n{tail}"
        if tail and len(candidate) > overlap * 2:
            break
        tail = candidate
        if len(tail) >= overlap:
            break
    return tail.strip()


def _split_index(text: str, chunk_size: int) -> int:
    if len(text) <= chunk_size:
        return len(text)

    window = text[:chunk_size]
    for marker in ("\n\n", ". ", "; ", ", "):
        idx = window.rfind(marker)
        if idx >= int(chunk_size * 0.55):
            return idx + len(marker)

    idx = window.rfind(" ")
    if idx >= int(chunk_size * 0.55):
        return idx + 1
    return chunk_size


def chunk_document(
    doc: SourceDocument,
    chunk_size: int = CHUNK_SIZE_CHARS,
    overlap: int = CHUNK_OVERLAP_CHARS,
) -> list[Chunk]:
    chunks: list[Chunk] = []
    current = ""

    for paragraph in _paragraphs(doc.text):
        candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
        if len(candidate) <= chunk_size:
            current = candidate
            continue

        if current:
            chunks.append(
                Chunk(
                    id=f"{doc.source_name}:{len(chunks)}",
                    text=current,
                    source_name=doc.source_name,
                    source_url=doc.source_url,
                    title=doc.title,
                    chunk_index=len(chunks),
                )
            )
            tail = _overlap_tail(current, overlap)
            current = f"{tail}\n\n{paragraph}".strip() if tail else paragraph

        while len(current) > chunk_size:
            split_at = _split_index(current, chunk_size)
            piece = current[:split_at].strip()
            chunks.append(
                Chunk(
                    id=f"{doc.source_name}:{len(chunks)}",
                    text=piece,
                    source_name=doc.source_name,
                    source_url=doc.source_url,
                    title=doc.title,
                    chunk_index=len(chunks),
                )
            )
            current = current[split_at:].strip()

    if current:
        chunks.append(
            Chunk(
                id=f"{doc.source_name}:{len(chunks)}",
                text=current,
                source_name=doc.source_name,
                source_url=doc.source_url,
                title=doc.title,
                chunk_index=len(chunks),
            )
        )

    return chunks


def chunk_documents(documents: list[SourceDocument]) -> list[Chunk]:
    chunks: list[Chunk] = []
    for doc in documents:
        chunks.extend(chunk_document(doc))
    return chunks


if __name__ == "__main__":
    docs = load_documents()
    chunks = chunk_documents(docs)
    print(f"Created {len(chunks)} chunks")
    for chunk in chunks[:5]:
        print("\n---")
        print(f"{chunk.id} | {chunk.title}")
        print(chunk.text[:700])
