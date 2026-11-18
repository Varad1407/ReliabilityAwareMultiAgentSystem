import sys
import json
import time
from pathlib import Path
from datetime import datetime, timezone

# Locate project folders
project_dir = Path(__file__).resolve().parent.parent
src_dir = project_dir / "src"
experiments_dir = project_dir / "experiments"

sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(experiments_dir))

from nl_to_sql import generate_sql
from sql_executor import execute_sql
from benchmark_questions import benchmark_questions


results = []

print("=" * 60)
print("SINGLE-AGENT BASELINE EXPERIMENT")
print("=" * 60)

for item in benchmark_questions:

    question_id = item["id"]
    question = item["question"]

    print(f"\nQuestion {question_id}: {question}")

    # Measure total generation and execution time
    start_time = time.perf_counter()

    try:
        # Generate SQL using Qwen
        generated_sql = generate_sql(question)

        # Execute generated SQL
        execution_result = execute_sql(generated_sql)

        elapsed_time = time.perf_counter() - start_time

        record = {
            "question_id": question_id,
            "question": question,
            "generated_sql": generated_sql,
            "execution_success": execution_result["success"],
            "execution_error_type": execution_result.get("error_type"),
            "execution_error": execution_result.get("error"),
            "columns": execution_result.get("columns"),
            "rows": [
                list(row) for row in execution_result.get("rows", [])
            ],
            "truncated": execution_result.get("truncated", False),
            "elapsed_seconds": round(elapsed_time, 3)
        }

    except Exception as error:

        elapsed_time = time.perf_counter() - start_time

        record = {
            "question_id": question_id,
            "question": question,
            "generated_sql": None,
            "execution_success": False,
            "execution_error_type": "GENERATION_ERROR",
            "execution_error": str(error),
            "columns": None,
            "rows": [],
            "truncated": False,
            "elapsed_seconds": round(elapsed_time, 3)
        }

    results.append(record)

    print("Generated SQL:")
    print(record["generated_sql"])

    print("Execution successful:", record["execution_success"])
    print("Elapsed time:", record["elapsed_seconds"], "seconds")

    if not record["execution_success"]:
        print("Error:", record["execution_error"])

# Save experiment results
output_path = project_dir / "results" / "single_agent_baseline.json"

experiment_data = {
    "experiment": "Single-Agent Baseline",
    "model": "qwen2.5:7b",
    "temperature": 0.0,
    "seed": 42,
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "results": results
}

with open(output_path, "w", encoding="utf-8") as file:
    json.dump(experiment_data, file, indent=4, ensure_ascii=False)

successful = sum(
    1 for result in results if result["execution_success"]
)

print("\n" + "=" * 60)
print("BASELINE SUMMARY")
print("=" * 60)
print("Total questions:", len(results))
print("SQL execution successes:", successful)
print("SQL execution failures:", len(results) - successful)
print("Results saved to:", output_path)