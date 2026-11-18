
from agents import semantic_validation_agent_v2 as validator
from nl_to_sql import ONLINE_RETAIL_DATABASE_SCHEMA, DATABASE_SCHEMA

# Mock LLM response to isolate deterministic validation
validator.generate_response = lambda prompt: "VALID"


TEST_CASES = [

    # ALTERNATIVE DATE EXPRESSIONS

    {
        "name": "November date filter using DATE and BETWEEN",
        "question": "How many records were recorded in November 2011?",
        "sql": """
            SELECT COUNT(*) FROM online_retail
            WHERE DATE(InvoiceDate)
            BETWEEN '2011-11-01' AND '2011-11-30'
        """,
        "expected": True
    },

    {
        "name": "November date filter using STRFTIME",
        "question": "How many records were recorded in November 2011?",
        "sql": """
            SELECT COUNT(*) FROM online_retail
            WHERE STRFTIME('%Y-%m', InvoiceDate) = '2011-11'
        """,
        "expected": True
    },

    # ALTERNATIVE CANCELLATION EXPRESSIONS

    {
        "name": "Cancellation exclusion using NOT GLOB",
        "question": "Count negative quantity records excluding cancellations.",
        "sql": """
            SELECT COUNT(*) FROM online_retail
            WHERE Quantity < 0
            AND InvoiceNo NOT GLOB 'C*'
        """,
        "expected": True
    },

    {
        "name": "Cancellation exclusion using LEFT",
        "question": "Count negative quantity records excluding cancellations.",
        "sql": """
            SELECT COUNT(*) FROM online_retail
            WHERE Quantity < 0
            AND LEFT(InvoiceNo, 1) <> 'C'
        """,
        "expected": False
    },

    # ALTERNATIVE SORTING EXPRESSIONS

    {
        "name": "Top five countries using aggregate expression in ORDER BY",
        "question": "Show the top 5 countries by number of records.",
        "sql": """
            SELECT Country, COUNT(*) AS total
            FROM online_retail
            GROUP BY Country
            ORDER BY COUNT(*) DESC
            LIMIT 5
        """,
        "expected": True
    },

    {
        "name": "Incorrect lowest five countries using descending order",
        "question": "Show the lowest 5 countries by number of records.",
        "sql": """
            SELECT Country, COUNT(*) AS total
            FROM online_retail
            GROUP BY Country
            ORDER BY COUNT(*) DESC
            LIMIT 5
        """,
        "expected": False
    },

    # DISTINCT CUSTOMER COUNT

    {
        "name": "Correct distinct customer count",
        "question": "How many distinct customers are in the database?",
        "sql": """
            SELECT COUNT(DISTINCT CustomerID)
            FROM online_retail
        """,
        "expected": True
    },

    {
        "name": "Incorrect distinct customer count",
        "question": "How many distinct customers are in the database?",
        "sql": """
            SELECT COUNT(*)
            FROM online_retail
        """,
        "expected": False
    }

]


def run_tests():

    passed = 0
    failed = 0

    print("\nDAY 32 - UNSEEN SQL FORMULATION TEST")
    print("=" * 65)

    for index, test in enumerate(TEST_CASES, start=1):

        schema = (
            DATABASE_SCHEMA
            if "paise" in test["sql"].lower()
            else ONLINE_RETAIL_DATABASE_SCHEMA
        )

        result = validator.semantic_validation_agent_v2(
            user_question=test["question"],
            sql_query=test["sql"],
            query_results=[],
            database_schema=schema
        )

        actual = result["is_valid"]
        expected = test["expected"]

        if actual == expected:
            passed += 1
            status = "PASS"
        else:
            failed += 1
            status = "FAIL"

        print(f"\nTest {index}: {test['name']}")
        print(f"Expected: {expected}")
        print(f"Actual:   {actual}")
        print(f"Status:   {status}")

        if result["feedback"]:
            print(f"Feedback: {result['feedback']}")

    print("\n" + "=" * 65)
    print("FINAL RESULTS")
    print("=" * 65)
    print(f"Total tests: {len(TEST_CASES)}")
    print(f"Passed:      {passed}")
    print(f"Failed:      {failed}")
    print(f"Test agreement: {passed / len(TEST_CASES) * 100:.2f}%")
    print("\nTest execution completed.")


if __name__ == "__main__":
    run_tests()
