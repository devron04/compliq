"""
CompliQ - From product to standard, instantly.
src/embeddings.py

Wrapper for embedding generation using sentence-transformers.
Uses BAAI/bge-small-en-v1.5 as per requirements for low latency and high accuracy on CPU.
"""

import sys
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("sentence_transformers is required. Install via: pip install sentence-transformers")
    sys.exit(1)

class EmbeddingModel:
    """Singleton-like wrapper for the SentenceTransformer model."""
    
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        # The BGE model requires "Represent this sentence for searching relevant passages: "
        # for queries, but for documents we just embed the raw text.
        # We will handle the prompt logic in the pipeline or here.
        print(f"Loading embedding model: {model_name}", file=sys.stderr)
        self.model = SentenceTransformer(model_name)
        
    def encode_documents(self, texts: list[str]) -> np.ndarray:
        """Encode a list of document strings into embeddings."""
        if not texts:
            return np.array([])
        # normalize_embeddings=True is required for bge models and cosine similarity (IndexFlatIP)
        embeddings = self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return embeddings

    def encode_query(self, query: str) -> np.ndarray:
        """Encode a single query string into an embedding.
        BGE models expect a specific prefix for queries.
        """
        prompt = f"Represent this sentence for searching relevant passages: {query}"
        embedding = self.model.encode([prompt], normalize_embeddings=True, show_progress_bar=False)
        return embedding[0]
