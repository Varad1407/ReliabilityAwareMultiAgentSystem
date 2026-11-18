
import sqlite3
import time
from pathlib import Path

from src.agents import semantic_validation_agent_v2 as validator
from src.nl_to_sql import ONLINE_RETAIL_DATABASE_SCHEMA


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "online_retail.db"

# Isolate deterministic validator checks from real LLM judgement.
validator.generate_response = lambda prompt: "VALID"


TEST_CASES = [
    {
        "name": "Valid date filtering using STRFTIME",
        "question": "How many records were created in November 2011?",
        "sql": """
            SELECT COUNT(*)
            FROM online_retail
            WHERE STRFTIME('%Y-%m', InvoiceDate) = '2011-11'
        """,
        "expected_valid": True,
        "expected_result": [(84711,)]
    },
    {
        "name": "Incorrect distinct invoice aggregation using subquery",
        "question": "How many distinct invoices are present?",
        "sql": """
            SELECT COUNT(*)
            FROM (
                SELECT InvoiceNo
                FROM online_retail
            )
        """,
        "expected_valid": False,
        "expected_result": [(541909,)]
    },
    {
        "name": "Valid cancellation exclusion using NOT EXISTS",
        "question": "How many records have negative quantities, excluding cancelled invoices?",
        "sql": """
            SELECT COUNT(*)
            FROM online_retail o
            WHERE o.Quantity < 0
            AND NOT EXISTS (
                SELECT 1
                FROM online_retail c
                WHERE c.InvoiceNo = o.InvoiceNo
                AND c.InvoiceNo GLOB 'C*'
            )
        """,
        "expected_valid": True,
        "expected_result": [(1336,)]
    },
    {
        "name": "Incorrect cancellation filtering",
        "question": "How many records have negative quantities, excluding cancelled invoices?",
        "sql": """
            SELECT COUNT(*)
            FROM online_retail
            WHERE Quantity < 0
        """,
        "expected_valid": False,
        "expected_result": [(10624,)]
    },
    {
        "name": "Valid top five countries using CTE",
        "question": "What are the top 5 countries by number of records?",
        "sql": """
            WITH country_counts AS (
                SELECT Country, COUNT(*) AS total
                FROM online_retail
                GROUP BY Country
            )
            SELECT Country, total
            FROM country_counts
            ORDER BY total DESC
            LIMIT 5
        """,
        "expected_valid": True,
        "expected_result": [
            ("United Kingdom", 495478),
            ("Germany", 9495),
            ("France", 8557),
            ("EIRE", 8196),
            ("Spain", 2533)
        ]
    },
    {
        "name": "Incorrect top five countries sorted ascending",
        "question": "What are the top 5 countries by number of records?",
        "sql": """
            WITH country_counts AS (
                SELECT Country, COUNT(*) AS total
                FROM online_retail
                GROUP BY Country
            )
            SELECT Country, total
            FROM country_counts
            ORDER BY total ASC
            LIMIT 5
        """,
        "expected_valid": False,
        "expected_result": None
    },
    {
        "name": "Valid distinct customer count using CTE",
        "question": "How many distinct customers are present?",
        "sql": """
            WITH distinct_customers AS (
                SELECT DISTINCT CustomerID
                FROM online_retail
                WHERE CustomerID IS NOT NULL
            )
            SELECT COUNT(*)
            FROM distinct_customers
        """,
        "expected_valid": True,
        "expected_result": [(4372,)]
    },
    {
        "name": "Incorrect distinct customer count using whole-table COUNT",
        "question": "How many distinct customers are present?",
        "sql": """
            SELECT COUNT(*)
            FROM online_retail
        """,
        "expected_valid": False,
        "expected_result": [(541909,)]
    }
]


def main():
    print("\nDAY 36 — BROADER SQL ROBUSTNESS TESTING")
    print("=" * 75)
    print(f"Database: {DB_PATH}")
    print(f"Database exists: {DB_PATH.exists()}")
    print(f"Total test cases: {len(TEST_CASES)}")
    print("LLM response: Mocked as VALID")
    print("Purpose: Isolate deterministic semantic validation")

    if not DB_PATH.exists():
        print("ERROR: Database file not found.")
        return

    connection = sqlite3.connect(
        f"file:{DB_PATH.as_posix()}?mode=ro",
        uri=True
    )

    passed = 0
    failed = 0
    execution_failures = 0
    validation_results = []

    try:
        for index, test in enumerate(TEST_CASES, start=1):
            print("\n" + "=" * 75)
            print(f"TEST {index}: {test['name']}")
            print("-" * 75)

            query_results = None
            execution_success = False

            # Execute SQL and measure execution time.
            start = time.perf_counter()

            try:
                cursor = connection.cursor()
                cursor.execute(test["sql"])
                query_results = cursor.fetchall()

                execution_time = time.perf_counter() - start
                execution_success = True

                print(f"SQL result: {query_results}")
                print(f"Execution time: {execution_time:.4f} seconds")

                if test["expected_result"] is not None:
                    print(
                        "Matches expected result:",
                        query_results == test["expected_result"]
                    )

            except Exception as error:
                execution_time = time.perf_counter() - start
                execution_failures += 1
                print(f"SQL execution failed: {error}")

            if not execution_success:
                print("Semantic validation skipped.")
                failed += 1
                continue

            # Run System C V2 semantic validator.
            try:
                validation = validator.semantic_validation_agent_v2(
                    user_question=test["question"],
                    sql_query=test["sql"],
                    query_results=query_results,
                    database_schema=ONLINE_RETAIL_DATABASE_SCHEMA
                )

                actual_valid = validation["is_valid"]
                expected_valid = test["expected_valid"]

                test_passed = actual_valid == expected_valid

                print(f"Expected validator decision: {expected_valid}")
                print(f"Actual validator decision: {actual_valid}")
                print(f"Validator feedback: {validation.get('feedback')}")

                print(
                    "TEST RESULT:",
                    "PASS" if test_passed else "FAIL"
                )

                if test_passed:
                    passed += 1
                else:
                    failed += 1

                validation_results.append({
                    "name": test["name"],
                    "expected": expected_valid,
                    "actual": actual_valid,
                    "passed": test_passed
                })

            except Exception as error:
                print(f"Validator error: {error}")
                failed += 1

    finally:
        connection.close()

    print("\n\nDAY 36 — FINAL SUMMARY")
    print("=" * 75)
    print(f"Total tests: {len(TEST_CASES)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"SQL execution failures: {execution_failures}")

    if passed + failed > 0:
        print(
            "Validator test agreement:",
            f"{(passed / (passed + failed)) * 100:.2f}%"
        )

    print("\nVALIDATION RESULTS")
    print("-" * 75)

    for result in validation_results:
        print(
            f"{result['name']}: "
            f"Expected={result['expected']}, "
            f"Actual={result['actual']}, "
            f"Passed={result['passed']}"
        )

    print("\nLLM was mocked as VALID.")
    print("These results measure deterministic validator behaviour.")
    print("They do not measure real LLM semantic judgement.")


if __name__ == "__main__":
    main()
