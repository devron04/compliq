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
from dotenv import load_dotenv
load_dotenv()
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

        # Concise prompt for both speed and accuracy
        system_prompt = """You are a BIS expert. Recommend 3-5 standards from the CONTEXT that match the PRODUCT.
Return JSON format: {"recommendations": [{"standard_id": "...", "rationale": "..."}]}
ONLY use standard_ids from the context. Keep rationales under 10 words."""
        
        user_prompt = f"PRODUCT: {product_description}\n\nCONTEXT:\n{context_str}"

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=300,
                temperature=0.0
            )
            
            content = response.choices[0].message.content
            data = json.loads(content)
            recommendations = data.get("recommendations", [])
            
            # Map IDs to Titles from the original search results
            id_to_title = {chunk["standard_id"]: chunk["title"] for chunk, _ in top_chunks}
            
            final_standards = []
            final_full_data = []
            
            for rec in recommendations:
                std_id = rec.get("standard_id", "").strip()
                if std_id in valid_is_numbers:
                    if std_id not in final_standards:
                        final_standards.append(std_id)
                        # Add the real title to the recommendation
                        rec["title"] = id_to_title.get(std_id, "Standard Document")
                        final_full_data.append(rec)
            
            if return_full:
                return final_full_data
            return final_standards
            
        except Exception as e:
            print(f"LLM Error: {e}", file=sys.stderr)
            # Fallback to search results if LLM fails
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
