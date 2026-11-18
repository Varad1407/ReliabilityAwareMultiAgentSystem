
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.agents import semantic_validation_agent_v2 as validator
from src.nl_to_sql import ONLINE_RETAIL_DATABASE_SCHEMA


DB_PATH = PROJECT_ROOT / "data" / "online_retail.db"

# Isolate deterministic validation rules.
validator.generate_response = lambda prompt: "VALID"


TEST_CASES = [
    {
        "name": "Valid date filter using YEAR and MONTH extraction",
        "question": "How many records were created in November 2011?",
        "sql": """
            SELECT COUNT(*)
            FROM online_retail
            WHERE CAST(STRFTIME('%Y', InvoiceDate) AS INTEGER) = 2011
              AND CAST(STRFTIME('%m', InvoiceDate) AS INTEGER) = 11
        """,
        "expected_valid": True,
    },
    {
        "name": "Invalid date filter using December instead of November",
        "question": "How many records were created in November 2011?",
        "sql": """
            SELECT COUNT(*)
            FROM online_retail
            WHERE InvoiceDate >= '2011-12-01'
              AND InvoiceDate < '2012-01-01'
        """,
        "expected_valid": False,
    },
    {
        "name": "Valid cancellation exclusion using GLOB",
        "question": "How many negative quantity records exclude cancelled invoices?",
        "sql": """
            SELECT COUNT(*)
            FROM online_retail
            WHERE Quantity < 0
              AND InvoiceNo NOT GLOB 'C*'
        """,
        "expected_valid": True,
    },
    {
        "name": "Invalid cancellation handling using no exclusion",
        "question": "How many negative quantity records exclude cancelled invoices?",
        "sql": """
            SELECT COUNT(*)
            FROM online_retail
            WHERE Quantity < 0
        """,
        "expected_valid": False,
    },
    {
        "name": "Valid distinct invoice count using a CTE",
        "question": "How many unique invoices are in the dataset?",
        "sql": """
            WITH unique_invoices AS (
                SELECT DISTINCT InvoiceNo
                FROM online_retail
            )
            SELECT COUNT(*)
            FROM unique_invoices
        """,
        "expected_valid": True,
    },
    {
        "name": "Invalid invoice count using ordinary COUNT",
        "question": "How many unique invoices are in the dataset?",
        "sql": """
            SELECT COUNT(*)
            FROM online_retail
        """,
        "expected_valid": False,
    },
    {
        "name": "Valid distinct customer count using GROUP BY",
        "question": "How many unique customers are recorded?",
        "sql": """
            SELECT COUNT(*)
            FROM (
                SELECT CustomerID
                FROM online_retail
                WHERE CustomerID IS NOT NULL
                GROUP BY CustomerID
            )
        """,
        "expected_valid": True,
    },
    {
        "name": "Invalid customer count including duplicate records",
        "question": "How many unique customers are recorded?",
        "sql": """
            SELECT COUNT(CustomerID)
            FROM online_retail
        """,
        "expected_valid": False,
    },
]


def execute_query(sql):
    connection = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    try:
        cursor = connection.cursor()
        cursor.execute(sql)
        return cursor.fetchall()
    finally:
        connection.close()


def main():
    passed = 0
    failed = 0
    execution_failures = 0
    false_acceptances = 0
    false_rejections = 0

    print("\nDAY 37 — UNSEEN SQL PATTERN TESTING")
    print("=" * 65)

    for index, test in enumerate(TEST_CASES, start=1):
        print(f"\nTest {index}: {test['name']}")

        try:
            result = execute_query(test["sql"])
            print("SQL execution: SUCCESS")
            print("Query result:", result)

        except Exception as error:
            execution_failures += 1
            result = None
            print("SQL execution: FAILED")
            print("Error:", error)

        try:
            validation = validator.semantic_validation_agent_v2(
                user_question=test["question"],
                sql_query=test["sql"],
                query_results=result,
                database_schema=ONLINE_RETAIL_DATABASE_SCHEMA,
            )

            actual_valid = validation.get("is_valid", False)
            feedback = validation.get("feedback", "")

            print("Expected validator decision:", test["expected_valid"])
            print("Actual validator decision:", actual_valid)
            print("Feedback:", feedback)

            if actual_valid == test["expected_valid"]:
                passed += 1
                print("TEST RESULT: PASS")
            else:
                failed += 1
                print("TEST RESULT: FAIL")

                if actual_valid and not test["expected_valid"]:
                    false_acceptances += 1

                if not actual_valid and test["expected_valid"]:
                    false_rejections += 1

        except Exception as error:
            failed += 1
            print("VALIDATOR ERROR:", error)
            print("TEST RESULT: FAIL")

    total = len(TEST_CASES)

    print("\n" + "=" * 65)
    print("DAY 37 SUMMARY")
    print("=" * 65)
    print(f"Total tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"SQL execution failures: {execution_failures}")
    print(f"False acceptances: {false_acceptances}")
    print(f"False rejections: {false_rejections}")
    print(f"Validator test agreement: {(passed / total) * 100:.2f}%")


if __name__ == "__main__":
    main()
