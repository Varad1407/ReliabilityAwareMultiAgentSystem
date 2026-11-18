
import json
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(PROJECT_DIR / "src"))
sys.path.insert(0, str(PROJECT_DIR / "experiments"))

from sql_executor import execute_sql
from evaluation_utils import rows_match, ordering_matches
from benchmark_questions import benchmark_questions


RESULTS_PATH = PROJECT_DIR / "results" / "multi_agent_system_c.json"


def evaluate_system_c():

    with open(RESULTS_PATH, "r", encoding="utf-8") as file:
        experiment_data = json.load(file)

    experiment_results = experiment_data.get("results", [])

    results_by_id = {
        result["question_id"]: result
        for result in experiment_results
    }

    execution_successes = 0
    correct_answers = 0

    print("\nMULTI-AGENT SYSTEM C EVALUATION")
    print("=" * 55)

    for question in benchmark_questions:

        question_id = question["id"]
        result = results_by_id.get(question_id)

        print(f"\nQuestion {question_id}: ", end="")

        if result is None:
            print("FAIL — Missing experiment result")
            continue

        execution_status = result["execution_success"]

        if execution_status:
            execution_successes += 1

        # Obtain ground-truth database results
        expected_result = execute_sql(question["expected_sql"])

        if not expected_result["success"]:
            print("GROUND-TRUTH ERROR")
            print(expected_result["error"])
            continue

        expected_rows = expected_result["rows"]
        generated_rows = result.get("rows", [])

        # Compare actual and expected database results
        values_correct = rows_match(
            generated_rows,
            expected_rows
        )

        ordering_correct = ordering_matches(
            generated_rows,
            question.get("ordering", [])
        )

        is_correct = (
            execution_status
            and values_correct
            and ordering_correct
        )

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
    print("SYSTEM C EVALUATION SUMMARY")
    print("=" * 55)

    print("Total benchmark questions:", total_questions)
    print("Successful SQL executions:", execution_successes)
    print("Correct database answers:", correct_answers)

    print(
        "Execution success rate:",
        f"{execution_successes / total_questions * 100:.2f}%"
    )

    print(
        "Database answer correctness rate:",
        f"{correct_answers / total_questions * 100:.2f}%"
    )


if __name__ == "__main__":
    evaluate_system_c()
