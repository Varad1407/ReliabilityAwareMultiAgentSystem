
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

from agents.orchestrator_c import orchestrate_c
from benchmark_questions import benchmark_questions


results = []

print("=" * 60)
print("MULTI-AGENT SYSTEM C EXPERIMENT")
print("=" * 60)

for item in benchmark_questions:

    question_id = item["id"]
    question = item["question"]

    print(f"\nQuestion {question_id}: {question}")

    start_time = time.perf_counter()

    try:
        # Run System C with autonomous error recovery
        system_result = orchestrate_c(question)

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
            "recovery_attempts": system_result.get("recovery_attempts", 0),
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
            "recovery_attempts": 0,
            "elapsed_seconds": round(elapsed_time, 3)
        }

    results.append(record)

    print("Generated SQL:")
    print(record["generated_sql"])

    print("Execution successful:", record["execution_success"])
    print("Recovery attempts:", record["recovery_attempts"])
    print("Elapsed time:", record["elapsed_seconds"], "seconds")

    if record["execution_success"]:
        print("Final answer:", record["final_answer"])
    else:
        print("Error:", record["execution_error"])


# Save experiment results
output_path = project_dir / "results" / "multi_agent_system_c.json"

experiment_data = {
    "experiment": "Multi-Agent System C with Autonomous Recovery",
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

total_recovery_attempts = sum(
    result["recovery_attempts"] for result in results
)

print("\n" + "=" * 60)
print("SYSTEM C SUMMARY")
print("=" * 60)
print("Total questions:", len(results))
print("SQL execution successes:", successful)
print("SQL execution failures:", len(results) - successful)
print("Total recovery attempts:", total_recovery_attempts)
print("Results saved to:", output_path)
