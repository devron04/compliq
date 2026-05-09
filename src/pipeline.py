"""
CompliQ - From product to standard, instantly.
src/pipeline.py

End-to-End RAG Orchestration.
Loads pre-built indexes, retrieves context via Hybrid Search, and calls LLM (Groq)
with a strict anti-hallucination prompt.

Latency strategy:
  - Indexes and embedding model are loaded ONCE on BISPipeline.__init__().
  - Groq client is pre-warmed with a tiny dummy call on startup so the first
    real query does not pay the cold-start tax.
  - Every Groq call runs inside a concurrent.futures thread with a hard
    LLM_TIMEOUT_SECONDS deadline. If the LLM is too slow, we transparently
    fall back to the top-ranked retrieval results — guaranteeing sub-5s
    responses even under API congestion.
"""

import os
import sys
import json
import concurrent.futures
# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from typing import List
from dotenv import load_dotenv
load_dotenv()
from src.retriever import Retriever

try:
    from groq import Groq
except ImportError:
    print("groq is required. Install via: pip install groq", file=sys.stderr)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
LLM_TIMEOUT_SECONDS = 3.5   # Hard ceiling: fall back to retrieval if exceeded
MAX_OUTPUT_TOKENS   = 256   # Enough for 5 compact recommendations
LLM_TEMPERATURE     = 0.0   # Deterministic — removes sampling overhead

# Compact system prompt — fewer tokens → faster TTFT (time-to-first-token)
SYSTEM_PROMPT = (
    "You are a BIS expert. From the CONTEXT, choose 3-5 standards that best match "
    "the PRODUCT. Respond ONLY with valid JSON. "
    'Format: {"recommendations": [{"standard_id": "...", "rationale": "..."}]} '
    "Use ONLY standard_ids that appear verbatim in the CONTEXT. "
    "Keep each rationale under 10 words."
)


def _build_user_prompt(query: str, context_str: str) -> str:
    return f"PRODUCT: {query}\n\nCONTEXT:\n{context_str}"


class BISPipeline:
    def __init__(self, data_dir: str = "data"):
        """
        Initialize pipeline:
          1. Load pre-built FAISS + BM25 indexes (once).
          2. Connect to Groq and pre-warm the connection.
        """
        # 1. Retriever (loads embedding singleton + indexes from disk)
        self.retriever = Retriever(data_dir=data_dir)
        try:
            self.retriever.load_indexes()
        except FileNotFoundError as e:
            print(
                f"Index load error: {e}. "
                "Please run 'python src/retriever.py' to build indexes.",
                file=sys.stderr,
            )
            sys.exit(1)

        # 2. Groq client
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            print(
                "Warning: GROQ_API_KEY not set. LLM generation will fall back to raw retrieval.",
                file=sys.stderr,
            )
            self.client = None
        else:
            self.client = Groq(api_key=api_key)
            self._prewarm_groq()

        self.model = "llama-3.1-8b-instant"

        # Thread pool reused across calls (avoids per-query thread creation overhead)
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _prewarm_groq(self):
        """
        Fire a minimal Groq request at startup to establish the connection
        and pull any cold-start penalty away from the first real query.
        Failures are silently ignored — this is best-effort.
        """
        try:
            print("Pre-warming Groq connection...", file=sys.stderr)
            self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=1,
                temperature=0.0,
            )
            print("Groq connection warm.", file=sys.stderr)
        except Exception as e:
            print(f"Groq pre-warm failed (non-fatal): {e}", file=sys.stderr)

    def _call_groq(self, user_prompt: str) -> str:
        """Blocking Groq call — always run via the thread pool with a timeout."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            max_tokens=MAX_OUTPUT_TOKENS,
            temperature=LLM_TEMPERATURE,
        )
        return response.choices[0].message.content

    def _retrieval_fallback(self, top_chunks, return_full: bool):
        """Return retrieval-only results when LLM is unavailable or too slow.
        
        Deduplicates by standard_id so the same IS number never appears twice
        (multiple chunks can share the same standard_id).
        """
        seen      = set()
        ids       = []
        full_recs = []

        for chunk, _ in top_chunks:
            sid = chunk["standard_id"]
            if sid not in seen:
                seen.add(sid)
                ids.append(sid)
                full_recs.append(
                    {
                        "standard_id": sid,
                        "title":       chunk["title"],
                        "rationale":   "Direct retrieval match (LLM fallback)",
                    }
                )

        return full_recs if return_full else ids

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def query(self, product_description: str, return_full: bool = False) -> List:
        """
        Run the full RAG pipeline for a given product description.

        Args:
            product_description: Natural language product text.
            return_full: If True, returns list of dicts with standard_id, title,
                         rationale (used by the UI). If False, returns a plain
                         list of IS number strings (used by inference.py).

        Returns:
            List of standard IDs (str) or list of recommendation dicts.
        """
        if not product_description or not product_description.strip():
            return []

        # ── Step 1: Hybrid Retrieval ──────────────────────────────────
        top_chunks = self.retriever.hybrid_search(product_description, top_k=5)
        if not top_chunks:
            return []

        # Build context string and set of valid IS numbers for anti-hallucination
        context_parts    = []
        valid_is_numbers = set()
        id_to_title      = {}

        for chunk, _ in top_chunks:
            sid = chunk["standard_id"]
            valid_is_numbers.add(sid)
            id_to_title[sid] = chunk["title"]
            context_parts.append(
                f"Standard ID: {sid}\n"
                f"Title: {chunk['title']}\n"
                f"Category: {chunk['category']}\n"
                f"Scope: {chunk['scope']}"
            )

        context_str = "\n\n---\n\n".join(context_parts)

        # ── Step 2: LLM Generation (with timeout + fallback) ──────────
        if not self.client:
            return self._retrieval_fallback(top_chunks, return_full)

        user_prompt = _build_user_prompt(product_description, context_str)

        try:
            future = self._executor.submit(self._call_groq, user_prompt)
            content = future.result(timeout=LLM_TIMEOUT_SECONDS)
        except concurrent.futures.TimeoutError:
            print(
                f"LLM timeout after {LLM_TIMEOUT_SECONDS}s — using retrieval fallback.",
                file=sys.stderr,
            )
            return self._retrieval_fallback(top_chunks, return_full)
        except Exception as e:
            print(f"LLM Error: {e}", file=sys.stderr)
            return self._retrieval_fallback(top_chunks, return_full)

        # ── Step 3: Parse & Anti-Hallucination Filter ─────────────────
        try:
            data            = json.loads(content)
            recommendations = data.get("recommendations", [])
        except (json.JSONDecodeError, AttributeError):
            return self._retrieval_fallback(top_chunks, return_full)

        final_ids      = []
        final_full     = []
        seen           = set()

        for rec in recommendations:
            std_id = rec.get("standard_id", "").strip()
            # Hard filter: only allow IDs that were in the retrieved context
            if std_id in valid_is_numbers and std_id not in seen:
                seen.add(std_id)
                final_ids.append(std_id)
                rec["title"] = id_to_title.get(std_id, "Standard Document")
                final_full.append(rec)

        # Edge case: LLM returned nothing valid → fall back
        if not final_ids:
            return self._retrieval_fallback(top_chunks, return_full)

        return final_full if return_full else final_ids


if __name__ == "__main__":
    pipeline = BISPipeline()
    res = pipeline.query(
        "Looking for cement used in marine construction that resists sulfates",
        return_full=True,
    )
    print(json.dumps(res, indent=2))
