"""
CompliQ - From product to standard, instantly.
src/pipeline.py

End-to-End RAG Orchestration.
Loads pre-built indexes, retrieves context via Hybrid Search, and calls LLM (Groq)
with a strict anti-hallucination prompt.
"""

import os
import sys
import json
from typing import List
from retriever import Retriever

try:
    from groq import Groq
except ImportError:
    print("groq is required. Install via: pip install groq", file=sys.stderr)
    sys.exit(1)

# Anti-Hallucination Prompt Template
PROMPT_TEMPLATE = """You are a BIS Standards compliance assistant. Your job is to recommend relevant 
Bureau of Indian Standards (BIS) standards based on a product description.

STRICT RULES:
1. You MUST ONLY recommend standards from the CONTEXT provided below.
2. NEVER invent, guess, or recall IS numbers from memory.
3. If a standard is not in the CONTEXT, do not mention it.
4. Return ONLY the IS numbers that appear verbatim in the CONTEXT.

CONTEXT (retrieved BIS standards):
{retrieved_chunks}

PRODUCT DESCRIPTION:
{query}

OUTPUT FORMAT (JSON only, no preamble, no explanation outside JSON):
{{
  "recommendations": [
    {{
      "standard_id": "IS XXXX",
      "title": "exact title from context",
      "rationale": "one sentence explaining relevance to the product"
    }}
  ]
}}

Return 3 to 5 recommendations. Only use standard_ids that appear in the CONTEXT above.
"""

class BISPipeline:
    def __init__(self, data_dir: str = "data"):
        """Initialize pipeline and load pre-built indexes once."""
        self.retriever = Retriever(data_dir=data_dir)
        try:
            self.retriever.load_indexes()
        except FileNotFoundError as e:
            print(f"Index load error: {e}. Please run 'python src/retriever.py' to build indexes.", file=sys.stderr)
            sys.exit(1)

        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            print("Warning: GROQ_API_KEY environment variable not set. LLM generation will fallback to raw retrieval.", file=sys.stderr)
            self.client = None
        else:
            self.client = Groq(api_key=api_key)
            
        self.model = "llama-3.1-8b-instant"

    def query(self, product_description: str, return_full: bool = False) -> List[str]:
        """
        Run the full RAG pipeline for a given product description.
        If return_full is True, returns the parsed JSON from LLM (for UI).
        Otherwise, returns a list of just the IS numbers (for inference.py).
        """
        # Edge case: empty query
        if not product_description or not product_description.strip():
            return [] if not return_full else []

        # 1. Retrieve Context (Top 5)
        top_chunks = self.retriever.hybrid_search(product_description, top_k=5)
        
        # If no chunks found, return empty
        if not top_chunks:
            return [] if not return_full else []

        # Formatting context for LLM
        context_parts = []
        valid_is_numbers = set()
        for chunk, score in top_chunks:
            valid_is_numbers.add(chunk["standard_id"])
            context_parts.append(
                f"Standard ID: {chunk['standard_id']}\n"
                f"Title: {chunk['title']}\n"
                f"Category: {chunk['category']}\n"
                f"Scope: {chunk['scope']}"
            )
        
        context_str = "\n\n---\n\n".join(context_parts)

        # 2. Generate with LLM
        if not self.client:
            return [chunk["standard_id"] for chunk, _ in top_chunks]

        # PERFORMANCE TWEAK: If we only need IDs, ask the LLM to be brief (no rationales)
        # to stay under the 5s latency limit.
        if not return_full:
            system_prompt = "You are a BIS expert. Return a JSON list of the top 3-5 most relevant IS standard IDs from the context. Return ONLY the JSON list."
            user_prompt = f"Product: {product_description}\n\nContext:\n{context_str}"
            max_tokens = 100
        else:
            system_prompt = PROMPT_TEMPLATE
            user_prompt = f"PRODUCT DESCRIPTION: {product_description}\n\nRETRIEVED CONTEXT:\n{context_str}"
            max_tokens = 500

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"} if return_full else None,
                max_tokens=max_tokens,
                temperature=0.0
            )
            
            content = response.choices[0].message.content
            
            if not return_full:
                # LLM should return a list or a JSON with a list
                try:
                    data = json.loads(content)
                    if isinstance(data, list):
                        return data[:5]
                    if isinstance(data, dict):
                        # Find the first list in the dict
                        for val in data.values():
                            if isinstance(val, list):
                                return val[:5]
                    return [content] # Fallback
                except:
                    # If LLM returned raw text, try to find IS numbers
                    import re
                    return re.findall(r"IS\s+\d+(?:\s*\(Part\s*\d+\))?(?:\s*:\s*\d{4})?", content)[:5]

            # Full UI mode with rationales
            data = json.loads(content)
            recommendations = data.get("recommendations", [])
            
            # Anti-hallucination filter
            safe_recs = []
            for rec in recommendations:
                if rec.get("standard_id") in valid_is_numbers:
                    safe_recs.append(rec)
            
            return safe_recs
            
        except Exception as e:
            print(f"LLM Generation Error: {e}", file=sys.stderr)
            # Fallback to direct retrieval on error
            if return_full:
                return [
                    {
                        "standard_id": chunk["standard_id"],
                        "title": chunk["title"],
                        "rationale": "Fallback retrieval due to LLM error"
                    } for chunk, _ in top_chunks
                ]
            return list(valid_is_numbers)

if __name__ == "__main__":
    pipeline = BISPipeline()
    res = pipeline.query("Looking for cement used in marine construction that resists sulfates", return_full=True)
    print(json.dumps(res, indent=2))
