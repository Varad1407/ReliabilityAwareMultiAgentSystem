
import json
import re
from pathlib import Path


# Locate the project directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load System C experiment results
RESULTS_FILE = PROJECT_ROOT / "results" / "multi_agent_system_c.json"


def convert_value(value):
    """
    Convert numeric strings into numbers.
    Keep text values as strings.
    """

    if isinstance(value, str):
        try:
            return float(value) if "." in value else int(value)
        except ValueError:
            return value.strip()

    return value


def extract_rows(final_answer, columns, actual_rows):
    """
    Extract records from the formatted final answer.
    Supports:
    1. Numbered single-column lists.
    2. Numbered multi-column records.
    3. Single numerical answers.
    """

    lines = [
        line.strip()
        for line in final_answer.splitlines()
        if line.strip()
    ]

    extracted_rows = []

    # Single-column answers
    if len(columns) == 1 and len(actual_rows) > 1:

        for line in lines:
            match = re.match(r"^\d+\.\s*(.+)$", line)

            if match:
                extracted_rows.append(
                    [convert_value(match.group(1))]
                )

        return extracted_rows

    # Multiple-column answers
    if len(columns) > 1:

        for line in lines:
            match = re.match(r"^\d+\.\s*(.+)$", line)

            if not match:
                continue

            fields = match.group(1).split("|")

            if len(fields) != len(columns):
                continue

            row = []
            valid = True

            for field, column in zip(fields, columns):

                if ":" not in field:
                    valid = False
                    break

                key, value = field.split(":", 1)

                if key.strip() != column:
                    valid = False
                    break

                row.append(convert_value(value.strip()))

            if valid:
                extracted_rows.append(row)

        return extracted_rows

    # Single numerical answer
    if len(actual_rows) == 1 and len(actual_rows[0]) == 1:

        expected_value = actual_rows[0][0]

        if isinstance(expected_value, (int, float)):
            numbers = re.findall(
                r"(?<![A-Za-z])[-+]?\d+(?:\.\d+)?",
                final_answer
            )

            for number in numbers:
                extracted_rows.append([convert_value(number)])

        return extracted_rows

    return extracted_rows


def values_match(actual, expected):
    """
    Compare values, allowing a small tolerance for decimals.
    """

    if isinstance(actual, (int, float)) and isinstance(
        expected, (int, float)
    ):
        return abs(actual - expected) < 0.000001

    return str(actual).strip() == str(expected).strip()


def rows_match(first_rows, second_rows):
    """
    Compare two collections of rows, including duplicates.
    """

    if len(first_rows) != len(second_rows):
        return False

    unmatched = list(second_rows)

    for first_row in first_rows:

        found_index = None

        for index, second_row in enumerate(unmatched):

            if len(first_row) != len(second_row):
                continue

            if all(
                values_match(a, b)
                for a, b in zip(first_row, second_row)
            ):
                found_index = index
                break

        if found_index is None:
            return False

        unmatched.pop(found_index)

    return True


def evaluate_question(question_result):
    """
    Evaluate one question using four criteria.
    """

    columns = question_result["columns"]
    actual_rows = question_result["rows"]
    final_answer = question_result["final_answer"]

    extracted_rows = extract_rows(
        final_answer,
        columns,
        actual_rows
    )

    # Criterion 1: Factual accuracy
    factual_accuracy = (
        len(extracted_rows) > 0
        and all(
            any(
                len(extracted_row) == len(actual_row)
                and all(
                    values_match(a, b)
                    for a, b in zip(extracted_row, actual_row)
                )
                for actual_row in actual_rows
            )
            for extracted_row in extracted_rows
        )
    )

    # Criterion 2: Completeness
    completeness = rows_match(
        extracted_rows,
        actual_rows
    )

    # Criterion 3: Ordering
    ordering = extracted_rows == actual_rows

    # Criterion 4: Clarity
    lines = [
        line.strip()
        for line in final_answer.splitlines()
        if line.strip()
    ]

    if len(columns) == 1 and len(actual_rows) == 1:
        clarity = len(lines) > 0

    else:
        clarity = (
            len(lines) > 0
            and all(
                re.match(r"^\d+\.\s*.+$", line)
                for line in lines
            )
            and [
                int(re.match(r"^(\d+)\.", line).group(1))
                for line in lines
            ] == list(range(1, len(lines) + 1))
        )

    return {
        "question_id": question_result["question_id"],
        "factual_accuracy": factual_accuracy,
        "completeness": completeness,
        "ordering": ordering,
        "clarity": clarity,
        "expected_records": len(actual_rows),
        "extracted_records": len(extracted_rows)
    }


def main():

    with open(RESULTS_FILE, "r") as file:
        experiment_data = json.load(file)

    results = experiment_data["results"]

    total_score = 0
    maximum_score = 0

    print("\nNATURAL-LANGUAGE ANSWER EVALUATION")
    print("=" * 55)

    for question_result in results:

        evaluation = evaluate_question(question_result)

        scores = [
            evaluation["factual_accuracy"],
            evaluation["completeness"],
            evaluation["ordering"],
            evaluation["clarity"]
        ]

        question_score = sum(scores)

        total_score += question_score
        maximum_score += 4

        print(
            f"\nQuestion {evaluation['question_id']}: "
            f"{question_score}/4"
        )

        print(
            "Expected records:",
            evaluation["expected_records"]
        )

        print(
            "Extracted records:",
            evaluation["extracted_records"]
        )

        print(
            "Factual accuracy:",
            int(evaluation["factual_accuracy"])
        )

        print(
            "Completeness:",
            int(evaluation["completeness"])
        )

        print(
            "Ordering:",
            int(evaluation["ordering"])
        )

        print(
            "Clarity:",
            int(evaluation["clarity"])
        )

    print("\n" + "=" * 55)
    print("FINAL EVALUATION")
    print("=" * 55)

    print(f"Total score: {total_score}/{maximum_score}")

    percentage = (
        total_score / maximum_score * 100
        if maximum_score else 0
    )

    print(f"Overall score: {percentage:.2f}%")


if __name__ == "__main__":
    main()
