
import json
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(PROJECT_DIR / "src"))
sys.path.insert(0, str(PROJECT_DIR / "experiments"))

from sql_executor import execute_sql
from evaluation_utils import rows_match, ordering_matches
from benchmark_questions import benchmark_questions

RESULTS_PATH = PROJECT_DIR / "results" / "single_agent_baseline.json"


def get_result_field(result, possible_names, default=None):
    """Retrieve a field using supported alternative names."""
    for name in possible_names:
        if name in result:
            return result[name]
    return default


def evaluate_baseline():
    with open(RESULTS_PATH, "r", encoding="utf-8") as file:
        baseline_data = json.load(file)

    baseline_results = baseline_data.get("results", [])

    results_by_id = {}

    for result in baseline_results:
        question_id = get_result_field(
            result,
            ["question_id", "id"]
        )

        if question_id is not None:
            results_by_id[question_id] = result

    execution_successes = 0
    correct_answers = 0
    evaluated_questions = 0

    print("\nSINGLE-AGENT BASELINE EVALUATION")
    print("=" * 55)

    for question in benchmark_questions:
        question_id = question["id"]
        result = results_by_id.get(question_id)

        print(f"\nQuestion {question_id}: ", end="")

        if result is None:
            print("FAIL — Missing experiment result")
            continue

        # Read execution status.
        execution_status = get_result_field(
            result,
            ["success", "execution_success"],
            None
        )

        if execution_status is None and isinstance(
            result.get("execution"), dict
        ):
            execution_status = result["execution"].get("success")

        # Read generated rows.
        generated_rows = get_result_field(
            result,
            ["rows", "result_rows", "generated_rows"],
            []
        )

        # Handle nested execution results if present.
        if isinstance(result.get("execution"), dict):
            execution_data = result["execution"]
            generated_rows = get_result_field(
                execution_data,
                ["rows", "result_rows"],
                generated_rows
            )

        if execution_status is None:
            print("FAIL — Could not identify execution status")
            print("Available fields:", list(result.keys()))
            continue

        if execution_status:
            execution_successes += 1

        # Execute the benchmark's expected SQL to obtain ground truth.
        expected_result = execute_sql(question["expected_sql"])

        if not expected_result.get("success", False):
            print("GROUND-TRUTH ERROR")
            print("Expected SQL could not be executed.")
            print(expected_result.get("error_message", "Unknown error"))
            continue

        expected_rows = expected_result.get("rows", [])

        values_correct = rows_match(
            generated_rows,
            expected_rows
        )

        ordering_correct = ordering_matches(
            generated_rows,
            question.get("ordering", [])
        )

        is_correct = (
            bool(execution_status)
            and values_correct
            and ordering_correct
        )

        evaluated_questions += 1

        if is_correct:
            correct_answers += 1
            print("PASS")
        else:
            print("FAIL")

            if not execution_status:
                print("  SQL execution failed.")

            if not values_correct:
                print("  Result values do not match expected results.")

            if not ordering_correct:
                print("  Result ordering is incorrect.")

    total_questions = len(benchmark_questions)

    print("\n" + "=" * 55)
    print("EVALUATION SUMMARY")
    print("=" * 55)

    print(f"Total benchmark questions: {total_questions}")
    print(f"Successful SQL executions: {execution_successes}")
    print(f"Correct final answers: {correct_answers}")

    if total_questions:
        print(
            f"Execution success rate: "
            f"{execution_successes / total_questions * 100:.2f}%"
        )

    if evaluated_questions:
        print(
            f"Answer correctness rate: "
            f"{correct_answers / evaluated_questions * 100:.2f}%"
        )


if __name__ == "__main__":
    evaluate_baseline()
