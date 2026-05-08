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
            # Fallback if no LLM configured: just return retrieved IDs
            if return_full:
                return [
                    {
                        "standard_id": chunk["standard_id"],
                        "title": chunk["title"],
                        "rationale": "Retrieved via Hybrid Search (LLM disabled)"
                    } for chunk, _ in top_chunks
                ]
            return list(valid_is_numbers)

        prompt = PROMPT_TEMPLATE.format(
            retrieved_chunks=context_str,
            query=product_description
        )

        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.0, # Zero temperature for deterministic adherence to context
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            output_text = response.choices[0].message.content
            parsed_output = json.loads(output_text)
            
            recommendations = parsed_output.get("recommendations", [])
            
            # Anti-hallucination filter: strictly filter out any generated ID not in valid_is_numbers
            safe_recs = []
            for rec in recommendations:
                # Basic string cleanup
                rec_id = rec.get("standard_id", "").strip()
                if rec_id in valid_is_numbers:
                    safe_recs.append(rec)
            
            if return_full:
                return safe_recs
                
            return [rec["standard_id"] for rec in safe_recs]
            
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
