import json
import argparse
import time
import sys
from src.pipeline import BISPipeline

def run_inference(input_path, output_path):
    """
    Mandatory entry-point for judges (Rule 3.3).
    Processes queries and saves results in the required format.
    """
    print(f"Initializing CompliQ Engine...", file=sys.stderr)
    try:
        pipeline = BISPipeline()
    except Exception as e:
        print(f"Error initializing pipeline: {e}")
        sys.exit(1)

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            test_data = json.load(f)
    except Exception as e:
        print(f"Error reading input file: {e}")
        sys.exit(1)

    print(f"Processing {len(test_data)} queries...", file=sys.stderr)
    
    results_to_save = []
    for idx, item in enumerate(test_data):
        query = item.get("query", "")
        query_id = item.get("id", f"Q-{idx}")
        
        start_time = time.time()
        # Retrieve top 5 to satisfy MRR @ 5 requirements (Rule 4.1)
        pipeline_results = pipeline.predict(query, top_k=5)
        latency = time.time() - start_time
        
        retrieved_ids = [res["standard_id"] for res in pipeline_results]
        
        # Build result object (Rule 3.3)
        result_item = {
            "id": query_id,
            "retrieved_standards": retrieved_ids,
            "latency_seconds": round(latency, 4)
        }
        
        # Include expected_standards ONLY if present in input (makes eval_script.py work)
        if "expected_standards" in item:
            result_item["expected_standards"] = item["expected_standards"]
            
        results_to_save.append(result_item)
        
        if (idx + 1) % 10 == 0:
            print(f"Processed {idx+1}/{len(test_data)} queries...", file=sys.stderr)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results_to_save, f, indent=2)
    
    print(f"Inference complete. Results saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CompliQ Mandatory Inference Script")
    parser.add_argument("--input", required=True, help="Path to input JSON file")
    parser.add_argument("--output", required=True, help="Path to save results JSON file")
    
    args = parser.parse_args()
    run_inference(args.input, args.output)
