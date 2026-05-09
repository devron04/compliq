import json
import argparse
import sys

def normalize_std(std_string):
    """Normalizes the standard name by removing spaces and converting to lowercase."""
    return str(std_string).replace(" ", "").lower()

def evaluate_results(results_file):
    try:
        with open(results_file, "r") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading results file: {e}")
        sys.exit(1)

    total_queries = len(data)
    if total_queries == 0:
        print("No queries found in the result file.")
        return

    hits_at_3 = 0
    mrr_sum_at_5 = 0.0
    total_latency = 0.0

    for item in data:
        expected = set(normalize_std(std) for std in item.get("expected_standards", []))
        retrieved = [normalize_std(std) for std in item.get("retrieved_standards", [])]
        latency = item.get("latency_seconds", 0.0)
        total_latency += latency

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

    # Calculate Final Metrics
    hit_rate_3 = (hits_at_3 / total_queries) * 100
    mrr_5 = mrr_sum_at_5 / total_queries
    avg_latency = total_latency / total_queries

    print("\n" + "=" * 45)
    print("      🏛️  COMPLIQ EVALUATION RESULTS")
    print("=" * 45)
    print(f"Total Queries Evaluated : {total_queries}")
    print(f"Hit Rate @ 3            : {hit_rate_3:.2f}%")
    print(f"MRR @ 5                 : {mrr_5:.4f}")
    print(f"Avg Latency             : {avg_latency:.4f} seconds")
    print("=" * 45)
    print("Evaluation Complete. ✅")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate RAG Pipeline Results")
    parser.add_argument("results", help="Path to the results JSON file (e.g., data/sample_output.json)")
    args = parser.parse_args()
    evaluate_results(args.results)
