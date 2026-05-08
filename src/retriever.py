"""
CompliQ - From product to standard, instantly.
src/retriever.py

Implements FAISS dense index, BM25 sparse index, and Reciprocal Rank Fusion (RRF).
Allows building indices from chunks.json and loading them from disk.
"""

import json
import sys
import pickle
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict, Any

try:
    import faiss
except ImportError:
    print("faiss is required. Install via: pip install faiss-cpu")
    sys.exit(1)

try:
    from rank_bm25 import BM25Okapi
except ImportError:
    print("rank_bm25 is required. Install via: pip install rank-bm25")
    sys.exit(1)

from src.embeddings import EmbeddingModel

def tokenize_bm25(text: str) -> List[str]:
    """Domain-aware tokenizer that preserves IS numbers and grade names."""
    # Convert to lower case, split by space, remove basic punctuation from ends
    # This keeps "is 269", "fe 500" relatively intact compared to heavy regex.
    tokens = text.lower().replace("\n", " ").split()
    return [t.strip(".,;:()[]{}") for t in tokens if t.strip(".,;:()[]{}")]

class Retriever:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.faiss_index_path = self.data_dir / "faiss.index"
        self.bm25_index_path = self.data_dir / "bm25.pkl"
        self.chunks_path = self.data_dir / "chunks.json"
        
        self.chunks = []
        self.faiss_index = None
        self.bm25_index = None
        self.embed_model = None

    def build_indexes(self):
        """Build FAISS and BM25 indexes from chunks.json and save to disk."""
        if not self.chunks_path.exists():
            raise FileNotFoundError(f"{self.chunks_path} not found. Run ingest.py first.")

        print(f"Loading chunks from {self.chunks_path}...", file=sys.stderr)
        with open(self.chunks_path, "r", encoding="utf-8") as f:
            self.chunks = json.load(f)

        if not self.chunks:
            raise ValueError("Chunks file is empty.")

        texts = [c["full_text"] for c in self.chunks]
        
        # 1. Build FAISS Index
        print("Building FAISS index...", file=sys.stderr)
        self.embed_model = EmbeddingModel()
        embeddings = self.embed_model.encode_documents(texts)
        
        # Using IndexFlatIP for Inner Product (Cosine Similarity on normalized vectors)
        d = embeddings.shape[1]
        self.faiss_index = faiss.IndexFlatIP(d)
        self.faiss_index.add(embeddings)
        
        faiss.write_index(self.faiss_index, str(self.faiss_index_path))
        
        # 2. Build BM25 Index
        print("Building BM25 index...", file=sys.stderr)
        tokenized_corpus = [tokenize_bm25(text) for text in texts]
        self.bm25_index = BM25Okapi(tokenized_corpus)
        
        with open(self.bm25_index_path, "wb") as f:
            pickle.dump(self.bm25_index, f)
            
        print("Indexes built and saved to disk.", file=sys.stderr)

    def load_indexes(self):
        """Load pre-built indexes from disk for O(1) amortized setup."""
        if not self.faiss_index_path.exists() or not self.bm25_index_path.exists():
            raise FileNotFoundError("Indexes not found. Run build_indexes() first.")
            
        with open(self.chunks_path, "r", encoding="utf-8") as f:
            self.chunks = json.load(f)

        self.faiss_index = faiss.read_index(str(self.faiss_index_path))
        
        with open(self.bm25_index_path, "rb") as f:
            self.bm25_index = pickle.load(f)
            
        self.embed_model = EmbeddingModel()

    def hybrid_search(self, query: str, top_k: int = 5, retrieve_k: int = 10) -> List[Tuple[Dict[Any, Any], float]]:
        """Perform dense + sparse retrieval, fuse with RRF, and return top_k chunks."""
        if not self.faiss_index or not self.bm25_index:
            self.load_indexes()

        # Dense Retrieval (FAISS)
        q_emb = self.embed_model.encode_query(query).reshape(1, -1)
        # return top retrieve_k
        D, I = self.faiss_index.search(q_emb, min(retrieve_k, len(self.chunks)))
        
        dense_results = []
        for rank, idx in enumerate(I[0]):
            if idx != -1: # faiss returns -1 if not enough results
                dense_results.append((int(idx), rank + 1)) # (chunk_id, rank)

        # Sparse Retrieval (BM25)
        tokenized_query = tokenize_bm25(query)
        bm25_scores = self.bm25_index.get_scores(tokenized_query)
        # argsort descending, take top retrieve_k
        top_bm25_indices = np.argsort(bm25_scores)[::-1][:retrieve_k]
        
        sparse_results = []
        for rank, idx in enumerate(top_bm25_indices):
            # Only include if score > 0 to avoid irrelevant tail
            if bm25_scores[idx] > 0:
                sparse_results.append((int(idx), rank + 1))

        # Reciprocal Rank Fusion (RRF)
        # RRF_score(d) = sum(1 / (k + rank(d)))
        k_rrf = 60
        rrf_scores = {}
        
        for chunk_idx, rank in dense_results:
            rrf_scores[chunk_idx] = rrf_scores.get(chunk_idx, 0.0) + 1.0 / (k_rrf + rank)
            
        for chunk_idx, rank in sparse_results:
            rrf_scores[chunk_idx] = rrf_scores.get(chunk_idx, 0.0) + 1.0 / (k_rrf + rank)

        # Sort by RRF score descending
        sorted_indices = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)
        
        # Return top_k
        results = []
        for idx in sorted_indices[:top_k]:
            results.append((self.chunks[idx], rrf_scores[idx]))
            
        return results

if __name__ == "__main__":
    # If run standalone, build indices
    r = Retriever()
    r.build_indexes()
