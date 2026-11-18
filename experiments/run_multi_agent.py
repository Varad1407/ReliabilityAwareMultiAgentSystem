
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

from agents.orchestrator import orchestrate
from benchmark_questions import benchmark_questions


results = []

print("=" * 60)
print("MULTI-AGENT SYSTEM B EXPERIMENT")
print("=" * 60)

for item in benchmark_questions:

    question_id = item["id"]
    question = item["question"]

    print(f"\nQuestion {question_id}: {question}")

    start_time = time.perf_counter()

    try:
        # Run the complete multi-agent workflow
        system_result = orchestrate(question)

        elapsed_time = time.perf_counter() - start_time

        record = {
            "question_id": question_id,
            "question": question,
            "generated_sql": system_result.get("sql_query"),
            "execution_success": system_result["success"],
            "execution_error_type": system_result.get("error_type"),
            "execution_error": system_result.get("error"),
            "columns": system_result.get("columns"),
            "rows": [
                list(row) for row in system_result.get("rows", [])
            ],
            "truncated": system_result.get("truncated", False),
            "final_answer": system_result.get("answer"),
            "elapsed_seconds": round(elapsed_time, 3)
        }

    except Exception as error:

        elapsed_time = time.perf_counter() - start_time

        record = {
            "question_id": question_id,
            "question": question,
            "generated_sql": None,
            "execution_success": False,
            "execution_error_type": "SYSTEM_ERROR",
            "execution_error": str(error),
            "columns": None,
            "rows": [],
            "truncated": False,
            "final_answer": None,
            "elapsed_seconds": round(elapsed_time, 3)
        }

    results.append(record)

    print("Generated SQL:")
    print(record["generated_sql"])

    print("Execution successful:", record["execution_success"])
    print("Elapsed time:", record["elapsed_seconds"], "seconds")

    if record["execution_success"]:
        print("Final answer:", record["final_answer"])
    else:
        print("Error:", record["execution_error"])


# Save experiment results
output_path = project_dir / "results" / "multi_agent_system_b.json"

experiment_data = {
    "experiment": "Multi-Agent System B",
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
print("SYSTEM B SUMMARY")
print("=" * 60)
print("Total questions:", len(results))
print("SQL execution successes:", successful)
print("SQL execution failures:", len(results) - successful)
print("Results saved to:", output_path)
