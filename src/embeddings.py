"""
CompliQ - From product to standard, instantly.
src/embeddings.py

Wrapper for embedding generation using sentence-transformers.
Uses BAAI/bge-small-en-v1.5 for low latency and high accuracy on CPU.
The model is loaded as a module-level singleton so it is instantiated only
once per process, regardless of how many times EmbeddingModel() is called.
"""

import sys
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("sentence_transformers is required. Install via: pip install sentence-transformers")
    sys.exit(1)

# --- Module-level singleton ---
_MODEL_NAME = "BAAI/bge-small-en-v1.5"
_singleton_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    """Return the cached SentenceTransformer instance, loading it once."""
    global _singleton_model
    if _singleton_model is None:
        print(f"Loading embedding model: {_MODEL_NAME}", file=sys.stderr)
        _singleton_model = SentenceTransformer(_MODEL_NAME)
    return _singleton_model


class EmbeddingModel:
    """
    Thin wrapper around the module-level singleton SentenceTransformer.
    Constructing multiple EmbeddingModel() instances is cheap — they all
    share the same underlying model weights in memory.
    """

    def __init__(self, model_name: str = _MODEL_NAME):
        # model_name kept for API compatibility; singleton always uses _MODEL_NAME.
        self.model = _get_model()

    def encode_documents(self, texts: list[str]) -> np.ndarray:
        """Encode a list of document strings into L2-normalised embeddings."""
        if not texts:
            return np.array([])
        return self.model.encode(
            texts, normalize_embeddings=True, show_progress_bar=False, batch_size=64
        )

    def encode_query(self, query: str) -> np.ndarray:
        """
        Encode a single query string.
        BGE models require a specific prefix for asymmetric retrieval.
        """
        prompt = f"Represent this sentence for searching relevant passages: {query}"
        embedding = self.model.encode(
            [prompt], normalize_embeddings=True, show_progress_bar=False
        )
        return embedding[0]
