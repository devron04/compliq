"""
CompliQ - tests/test_schema.py

Validates that data/public_test_results.json exactly matches
the required schema for judging (can also be run in CI).
"""

import json
import sys
from pathlib import Path

RESULTS_FILE = Path(__file__).parent.parent / "data" / "public_test_results.json"


def test_output_schema():
    """Verify the output JSON schema is exactly correct for every item."""
    assert RESULTS_FILE.exists(), f"Missing: {RESULTS_FILE}"

    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert isinstance(data, list), "Output must be a JSON array"
    assert len(data) > 0, "Output array must not be empty"

    for i, item in enumerate(data):
        # 1. Required keys
        assert "id" in item, f"Item {i} missing 'id'"
        assert "retrieved_standards" in item, f"Item {i} missing 'retrieved_standards'"
        assert "latency_seconds" in item, f"Item {i} missing 'latency_seconds'"

        # 2. Type checks
        assert isinstance(item["retrieved_standards"], list), \
            f"Item {i}: 'retrieved_standards' must be a list"
        assert isinstance(item["latency_seconds"], (int, float)), \
            f"Item {i}: 'latency_seconds' must be a number"

        # 3. No more than 5 standards
        assert len(item["retrieved_standards"]) <= 5, \
            f"Item {i}: retrieved_standards has {len(item['retrieved_standards'])} items (max 5)"

        # 4. Each standard string must start with "IS "
        for std in item["retrieved_standards"]:
            assert isinstance(std, str), f"Item {i}: standard '{std}' must be a string"
            assert std.startswith("IS "), \
                f"Item {i}: standard '{std}' must start with 'IS '"

    print(f"✅ Schema validation passed for {len(data)} results.")


def test_inference_py_exists():
    """Ensure inference.py exists at root level."""
    inference_path = Path(__file__).parent.parent / "inference.py"
    assert inference_path.exists(), "inference.py is missing from root!"
    print("✅ inference.py found at root level.")


def test_all_required_files_exist():
    """Ensure all required deliverable files are present."""
    root = Path(__file__).parent.parent
    required = [
        "inference.py",
        "eval_script.py",
        "requirements.txt",
        "README.md",
        "src/ingest.py",
        "src/embeddings.py",
        "src/retriever.py",
        "src/pipeline.py",
        "src/app.py",
        "data/public_test_results.json",
    ]
    missing = [f for f in required if not (root / f).exists()]
    assert not missing, f"Missing required files: {missing}"
    print(f"✅ All {len(required)} required files present.")


if __name__ == "__main__":
    test_output_schema()
    test_inference_py_exists()
    test_all_required_files_exist()
    print("\n🎉 All checks passed!")
