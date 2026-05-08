"""
CompliQ - From product to standard, instantly.
inference.py

This is the main evaluation script run by the judges.
Loads the pre-built indexes ONCE, processes a batch of queries,
measures per-query latency, and outputs results in a strict JSON format.
"""

import argparse
import json
import time
import sys
from pathlib import Path
# Add src to path so we can import modules directly
sys.path.append(str(Path(__file__).parent / "src"))
from pipeline import BISPipeline

def main():
    parser = argparse.ArgumentParser(description="CompliQ Inference Script")
    parser.add_argument("--input", required=True, type=str, help="Path to input JSON file")
    parser.add_argument("--output", required=True, type=str, help="Path to output JSON file")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file {args.input} not found.", file=sys.stderr)
        sys.exit(1)

    print("Loading BIS RAG pipeline...", file=sys.stderr)
    try:
        pipeline = BISPipeline()
    except Exception as e:
        print(f"Failed to load pipeline: {e}", file=sys.stderr)
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8") as f:
        queries = json.load(f)

    if not isinstance(queries, list):
        print("Error: Input JSON must be a list of query objects.", file=sys.stderr)
        sys.exit(1)

    results = []
    total_queries = len(queries)
    
    for i, item in enumerate(queries):
        query_id = item.get("id")
        query_text = item.get("query", "")
        
        print(f"Processing {i+1}/{total_queries}: {query_id}", file=sys.stderr)
        
        start = time.perf_counter()
        try:
            standards = pipeline.query(query_text, return_full=False)
        except Exception as e:
            print(f"Error on query {query_id}: {e}", file=sys.stderr)
            standards = []
        latency = time.perf_counter() - start

        result_item = {
            "id": query_id,
            "query": query_text,
            "retrieved_standards": standards,
            "latency_seconds": round(latency, 3)
        }
        # Pass through expected_standards if present in input (required by eval_script.py)
        if "expected_standards" in item:
            result_item["expected_standards"] = item["expected_standards"]

        results.append(result_item)

    # Atomic write to ensure output is not partially written if interrupted
    out_path = Path(args.output)
    tmp_path = Path(str(out_path) + ".tmp")
    
    # Ensure parent directory exists
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        tmp_path.rename(out_path)
    except Exception as e:
        print(f"Failed to write output: {e}", file=sys.stderr)
        if tmp_path.exists():
            tmp_path.unlink()
        sys.exit(1)
        
    print(f"Done. Results written to {args.output}", file=sys.stderr)

if __name__ == "__main__":
    main()
