import json
import sys
import os
import time
from src.pipeline import BISPipeline

def normalize_std(std_string):
    """Normalizes the standard name by removing spaces and converting to lowercase for fair matching."""
    return str(std_string).replace(" ", "").lower()

def evaluate_pipeline(test_set_path):
    # 1. Load the pipeline
    print(f"Initializing CompliQ Engine...", file=sys.stderr)
    try:
        pipeline = BISPipeline()
    except Exception as e:
        print(f"Error initializing pipeline: {e}")
        return

    # 2. Load the test set
    try:
        with open(test_set_path, "r", encoding="utf-8") as f:
            test_data = json.load(f)
    except Exception as e:
        print(f"Error reading test set: {e}")
        return

    total_queries = len(test_data)
    if total_queries == 0:
        print("No queries found in the test set.")
        return

    print(f"Evaluating {total_queries} queries from {test_set_path}...", file=sys.stderr)
    
    hits_at_3 = 0
    mrr_sum_at_5 = 0.0
    total_latency = 0.0

    for idx, item in enumerate(test_data):
        query = item.get("query", "")
        expected = set(normalize_std(std) for std in item.get("expected_standards", []))
        
        start_time = time.time()
        results = pipeline.predict(query, top_k=5)
        latency = time.time() - start_time
        
        total_latency += latency
        retrieved = [normalize_std(res["standard_id"]) for res in results]

        # 1. Calculate Hit Rate @3
        if any(std in expected for std in retrieved[:3]):
            hits_at_3 += 1

        # 2. Calculate MRR @5
        mrr = 0.0
        for rank, std in enumerate(retrieved[:5], start=1):
            if std in expected:
                mrr = 1.0 / rank
                break
        mrr_sum_at_5 += mrr
        
        if (idx + 1) % 10 == 0:
            print(f"Processed {idx+1}/{total_queries} queries...", file=sys.stderr)

    # 3. Print Final Metrics
    hit_rate_3 = (hits_at_3 / total_queries) * 100
    mrr_5 = mrr_sum_at_5 / total_queries
    avg_latency = total_latency / total_queries

    print("\n" + "=" * 45)
    print("      🏛️  COMPLIQ EVALUATION RESULTS")
    print("=" * 45)
    print(f"Total Queries Evaluated : {total_queries}")
    print(f"Hit Rate @ 3            : {hit_rate_3:.2f}%")
    print(f"MRR @ 5                 : {mrr_5:.4f}")
    print(f"Avg Latency per Query   : {avg_latency:.4f} seconds")
    print("=" * 45)
    print("Reproduction Successful. ✅")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python eval_script.py <path_to_test_set.json>")
        sys.exit(1)
    
    evaluate_pipeline(sys.argv[1])
