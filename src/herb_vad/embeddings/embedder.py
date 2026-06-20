"""Embedder abstraction + lazy-importing sentence-transformers wrapper.

The ``Embedder`` Protocol is the only contract downstream code depends
on. Production uses ``LMEmbedder`` (lazy ``import sentence_transformers``
so the codebase imports cleanly without the [ml] extra installed); tests
use ``MockEmbedder``.

If you see ``ImportError: sentence_transformers not installed`` at
runtime, install ``[ml]`` extras:
``pip install -e ".[ml]"``.
"""

from __future__ import annotations

import hashlib
from typing import Protocol, Sequence

import numpy as np


class Embedder(Protocol):
    """Embed a batch of strings into row-stacked float vectors."""

    name: str

    @property
    def dim(self) -> int: ...

    def encode(self, texts: Sequence[str]) -> np.ndarray: ...


class MockEmbedder:
    """Deterministic hash-based pseudo-embedder for unit tests.

    Produces unit-norm vectors of fixed dimension. Two identical inputs
    give identical outputs; two different inputs give different outputs
    with probability ~ 1.
    """

    def __init__(self, dim: int = 8, name: str = "mock") -> None:
        self.dim = dim
        self.name = name

    def encode(self, texts: Sequence[str]) -> np.ndarray:
        out = np.zeros((len(texts), self.dim), dtype=np.float32)
        for i, t in enumerate(texts):
            digest = hashlib.sha256(t.encode("utf-8")).digest()
            # Take dim bytes, map to [-1, +1]
            vec = np.frombuffer(digest[: self.dim], dtype=np.uint8).astype(np.float32)
            vec = (vec / 127.5) - 1.0
            norm = np.linalg.norm(vec) or 1.0
            out[i] = vec / norm
        return out


class LMEmbedder:
    """Sentence-Transformers wrapper with lazy import.

    Constructing this object does NOT import sentence-transformers; the
    import happens on the first ``encode`` call. This lets the rest of
    the codebase import ``LMEmbedder`` without the [ml] extra.
    """

    def __init__(
        self,
        model_name: str = "BAAI/bge-m3",
        *,
        device: str | None = None,
        normalize: bool = True,
    ) -> None:
        self.name = model_name
        self.device = device
        self.normalize = normalize
        self._model: object | None = None  # SentenceTransformer at runtime
        self._dim: int | None = None

    @property
    def dim(self) -> int:
        if self._dim is None:
            self._lazy_load()
        assert self._dim is not None
        return self._dim

    def _lazy_load(self) -> None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as e:
            raise ImportError(
                "sentence_transformers is not installed. Install the [ml] "
                'extra: pip install -e ".[ml]"'
            ) from e
        self._model = SentenceTransformer(self.name, device=self.device)
        self._dim = int(self._model.get_sentence_embedding_dimension())  # type: ignore[union-attr]

    def encode(self, texts: Sequence[str]) -> np.ndarray:
        if self._model is None:
            self._lazy_load()
        assert self._model is not None
        vecs = self._model.encode(  # type: ignore[attr-defined]
            list(texts),
            batch_size=32,
            normalize_embeddings=self.normalize,
            show_progress_bar=False,
        )
        return np.asarray(vecs, dtype=np.float32)
