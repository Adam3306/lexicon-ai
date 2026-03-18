from __future__ import annotations

import os
from dataclasses import dataclass

from openai import OpenAI


@dataclass(frozen=True)
class EmbeddingConfig:
    model: str


def get_embedding_config() -> EmbeddingConfig:
    model = os.environ.get("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    return EmbeddingConfig(model=model)


def embed_texts(texts: list[str], *, model: str) -> list[list[float]]:
    """
    Returns one embedding per input text in the same order.
    """
    client = OpenAI()
    resp = client.embeddings.create(model=model, input=texts)
    return [d.embedding for d in resp.data]

