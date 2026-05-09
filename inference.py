import json
import argparse
import time
import sys
import os
from src.pipeline import BISPipeline

def run_inference_on_set(input_path, output_path):
    print(f"Initializing CompliQ Engine...", file=sys.stderr)
    try:
        pipeline = BISPipeline()
    except Exception as e:
        print(f"Error initializing pipeline: {e}")
        return

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            test_data = json.load(f)
    except Exception as e:
        print(f"Error reading input set: {e}")
        return

    print(f"Running inference on {len(test_data)} queries...", file=sys.stderr)
    
    results_to_save = []
    for idx, item in enumerate(test_data):
        query = item.get("query", "")
        
        start_time = time.time()
        pipeline_results = pipeline.predict(query, top_k=5)
        latency = time.time() - start_time
        
        retrieved_ids = [res["standard_id"] for res in pipeline_results]
        
        results_to_save.append({
            "id": item.get("id"),
            "query": query,
            "expected_standards": item.get("expected_standards", []),
            "retrieved_standards": retrieved_ids,
            "latency_seconds": round(latency, 4)
        })
        
        if (idx + 1) % 10 == 0:
            print(f"Processed {idx+1}/{len(test_data)} queries...", file=sys.stderr)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results_to_save, f, indent=2)
    
    print(f"Inference complete. Results saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run CompliQ Inference on a Test Set")
    parser.add_argument("input", help="Path to input test set (e.g., data/public_test_set.json)")
    parser.add_argument("output", help="Path to save results (e.g., my_results.json)")
    
    # Also support single query mode if needed
    parser.add_argument("--query", help="Run inference on a single query")
    
    args = parser.parse_args()
    
    if args.query:
        pipeline = BISPipeline()
        res = pipeline.predict(args.query)
        print(json.dumps(res, indent=2))
    else:
        run_inference_on_set(args.input, args.output)
