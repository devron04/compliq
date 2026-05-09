"""
CompliQ - tests/test_retriever.py

Unit tests for the Retriever (BM25 tokenizer and RRF logic)
that can run WITHOUT loading any external model or index.
"""

import sys

def test_tokenize_bm25_preserves_is_numbers():
    """Ensure BM25 tokenizer keeps IS numbers intact."""
    sys.path.insert(0, ".")
    from src.retriever import tokenize_bm25

    tokens = tokenize_bm25("I need IS 269 cement for my building project.")
    assert "is" in tokens
    assert "269" in tokens
    assert "cement" in tokens
    assert "project" in tokens
    print("✅ BM25 tokenizer preserves IS number tokens.")


def test_tokenize_bm25_removes_punctuation():
    """Ensure BM25 tokenizer strips punctuation from tokens."""
    sys.path.insert(0, ".")
    from src.retriever import tokenize_bm25

    tokens = tokenize_bm25("(IS 1786: high-strength deformed steel bars).")
    for token in tokens:
        assert "(" not in token and ")" not in token and "." not in token
    print("✅ BM25 tokenizer strips punctuation correctly.")


if __name__ == "__main__":
    test_tokenize_bm25_preserves_is_numbers()
    test_tokenize_bm25_removes_punctuation()
    print("\n🎉 All retriever tests passed!")
