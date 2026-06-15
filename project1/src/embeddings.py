from __future__ import annotations

import os
from dataclasses import dataclass

from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import HashingVectorizer

from .config import EMBEDDING_MODEL


@dataclass
class EmbeddingBackend:
    name: str
    model: object

    def encode(self, texts: list[str]) -> list[list[float]]:
        if isinstance(self.model, SentenceTransformer):
            return self.model.encode(texts, normalize_embeddings=True).tolist()
        vectors = self.model.transform(texts)
        return vectors.toarray().tolist()


def load_embedding_backend() -> EmbeddingBackend:
    try:
        model = SentenceTransformer(EMBEDDING_MODEL, local_files_only=True)
        return EmbeddingBackend(name=EMBEDDING_MODEL, model=model)
    except Exception:
        if os.getenv("ALLOW_MODEL_DOWNLOAD") == "1":
            model = SentenceTransformer(EMBEDDING_MODEL)
            return EmbeddingBackend(name=EMBEDDING_MODEL, model=model)

    fallback = HashingVectorizer(
        n_features=384,
        alternate_sign=False,
        norm="l2",
        ngram_range=(1, 2),
        stop_words="english",
    )
    return EmbeddingBackend(name="local HashingVectorizer fallback", model=fallback)

