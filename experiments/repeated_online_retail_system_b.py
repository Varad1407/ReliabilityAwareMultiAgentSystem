
import json
import sys
import time
from pathlib import Path
from datetime import datetime

# Locate project directories
project_dir = Path(__file__).resolve().parent.parent
src_dir = project_dir / "src"

sys.path.insert(0, str(project_dir))
sys.path.insert(0, str(src_dir))

from online_retail_benchmark import online_retail_benchmark
from evaluation_utils import rows_match, ordering_matches
from agents.orchestrator import orchestrate
from nl_to_sql import ONLINE_RETAIL_DATABASE_SCHEMA
from database import online_retail_database_path


REPETITIONS = 5


def evaluate_question(benchmark_item):
    question_id = benchmark_item["id"]
    question = benchmark_item["question"]
    expected_rows = benchmark_item["expected_rows"]
    ordering = benchmark_item.get("ordering", [])

    start_time = time.perf_counter()

    try:
        result = orchestrate(
            question,
            db_path=online_retail_database_path,
            database_schema=ONLINE_RETAIL_DATABASE_SCHEMA
        )

        latency = time.perf_counter() - start_time

        actual_rows = result.get("rows", [])
        actual_columns = result.get("columns", [])

        # Question 8 uses a semantic column-value comparison.
        if question_id == 8:
            expected_categories = {
                "PositiveQuantityRecords": 531285,
                "NonCancellationReturns": 1336,
                "CancellationRecords": 9288
            }

            result_matches = False

            if len(actual_rows) == 1 and len(actual_columns) == 3:
                actual_mapping = dict(
                    zip(actual_columns, actual_rows[0])
                )

                result_matches = all(
                    actual_mapping.get(column) == expected_value
                    for column, expected_value in expected_categories.items()
                )
        else:
            result_matches = rows_match(
                actual_rows,
                expected_rows
            )

        order_matches = ordering_matches(
            actual_rows,
            ordering
        )

        correct = (
            result.get("success", False)
            and result_matches
            and order_matches
        )

        return {
            "id": question_id,
            "success": result.get("success", False),
            "correct": correct,
            "latency_seconds": round(latency, 4),
            "sql": result.get("sql_query"),
            "error": result.get("error")
        }

    except Exception as error:
        latency = time.perf_counter() - start_time

        return {
            "id": question_id,
            "success": False,
            "correct": False,
            "latency_seconds": round(latency, 4),
            "sql": None,
            "error": str(error)
        }


def main():
    print("=" * 65)
    print("REPEATED BENCHMARK - SYSTEM B")
    print("=" * 65)

    all_runs = []

    for repetition in range(1, REPETITIONS + 1):
        print(f"\n========== REPETITION {repetition}/{REPETITIONS} ==========")

        run_results = []

        for item in online_retail_benchmark:
            result = evaluate_question(item)
            run_results.append(result)

            print(
                f"Q{result['id']}: "
                f"Success={result['success']} | "
                f"Correct={result['correct']} | "
                f"Latency={result['latency_seconds']}s"
            )

        successful = sum(r["success"] for r in run_results)
        correct = sum(r["correct"] for r in run_results)

        print(f"Successful executions: {successful}/10")
        print(f"Correct answers: {correct}/10")

        all_runs.append({
            "repetition": repetition,
            "successful_executions": successful,
            "correct_answers": correct,
            "results": run_results
        })

    # Aggregate results
    all_results = [
        result
        for run in all_runs
        for result in run["results"]
    ]

    total_evaluations = len(all_results)

    successful_total = sum(
        result["success"] for result in all_results
    )

    correct_total = sum(
        result["correct"] for result in all_results
    )

    latencies = [
        result["latency_seconds"]
        for result in all_results
    ]

    average_latency = (
        sum(latencies) / len(latencies)
        if latencies else 0
    )

    summary = {
        "system": "System B",
        "repetitions": REPETITIONS,
        "questions_per_repetition": len(online_retail_benchmark),
        "total_evaluations": total_evaluations,
        "successful_executions": successful_total,
        "correct_answers": correct_total,
        "execution_success_rate": round(
            successful_total / total_evaluations * 100, 2
        ),
        "answer_accuracy": round(
            correct_total / total_evaluations * 100, 2
        ),
        "average_latency_seconds": round(average_latency, 4),
        "minimum_latency_seconds": round(min(latencies), 4),
        "maximum_latency_seconds": round(max(latencies), 4)
    }

    print("\n" + "=" * 65)
    print("FINAL SYSTEM B SUMMARY")
    print("=" * 65)

    for key, value in summary.items():
        print(f"{key}: {value}")

    # Save each experiment without overwriting previous results.
    results_dir = project_dir / "results"
    results_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    output_file = (
        results_dir /
        f"repeated_online_retail_system_b_{timestamp}.json"
    )

    output_data = {
        "experiment": "Repeated Online Retail Benchmark - System B",
        "summary": summary,
        "runs": all_runs
    }

    with output_file.open("x", encoding="utf-8") as file:
        json.dump(
            output_data,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\nResults saved to:")
    print(output_file)


if __name__ == "__main__":
    main()
