
from agents import semantic_validation_agent_v2 as validator
from nl_to_sql import (
    ONLINE_RETAIL_DATABASE_SCHEMA,
    DATABASE_SCHEMA
)


# ==================================================
# DAY 30: VALIDATOR ROBUSTNESS TEST
# ==================================================

# We mock the LLM response so that this first test
# focuses on the deterministic validation rules.
# The LLM will not make external API calls.

validator.generate_response = lambda prompt: "VALID"


TEST_CASES = [

    {
        "name": "Valid November date filter",
        "question": "How many records were recorded in November 2011?",
        "sql": """
            SELECT COUNT(*)
            FROM online_retail
            WHERE InvoiceDate >= '2011-11-01'
            AND InvoiceDate < '2011-12-01'
        """,
        "expected": True
    },

    {
        "name": "Incorrect November date filter",
        "question": "How many records were recorded in November 2011?",
        "sql": """
            SELECT COUNT(*)
            FROM online_retail
            WHERE InvoiceDate >= '2011-11-01'
            AND InvoiceDate < '2012-01-01'
        """,
        "expected": False
    },

    {
        "name": "Date boundaries present but reversed",
        "question": "How many records were recorded in November 2011?",
        "sql": """
            SELECT COUNT(*)
            FROM online_retail
            WHERE InvoiceDate < '2011-11-01'
            AND InvoiceDate >= '2011-12-01'
        """,
        "expected": False
    },

    {
        "name": "Missing cancellation exclusion",
        "question": "Count negative quantity records excluding cancellations.",
        "sql": """
            SELECT COUNT(*)
            FROM online_retail
            WHERE Quantity < 0
        """,
        "expected": False
    },

    {
        "name": "Standard cancellation exclusion",
        "question": "Count negative quantity records excluding cancellations.",
        "sql": """
            SELECT COUNT(*)
            FROM online_retail
            WHERE Quantity < 0
            AND InvoiceNo NOT LIKE 'C%'
        """,
        "expected": True
    },

    {
        "name": "Equivalent cancellation exclusion",
        "question": "Count negative quantity records excluding cancellations.",
        "sql": """
            SELECT COUNT(*)
            FROM online_retail
            WHERE Quantity < 0
            AND SUBSTR(InvoiceNo, 1, 1) <> 'C'
        """,
        "expected": True
    },

    {
        "name": "Incorrect sorting direction",
        "question": "Show the top 5 countries by number of records.",
        "sql": """
            SELECT Country, COUNT(*) AS total
            FROM online_retail
            GROUP BY Country
            ORDER BY total ASC
            LIMIT 5
        """,
        "expected": False
    },

    {
        "name": "Correct sorting direction",
        "question": "Show the top 5 countries by number of records.",
        "sql": """
            SELECT Country, COUNT(*) AS total
            FROM online_retail
            GROUP BY Country
            ORDER BY total DESC
            LIMIT 5
        """,
        "expected": True
    },

    {
        "name": "Incorrect SUM instead of AVG",
        "question": "What is the average UnitPrice?",
        "sql": """
        SELECT SUM(UnitPrice)
        FROM online_retail
    """,
        "expected": False
    },

    {
        "name": "Incorrect AVG instead of SUM",
        "question": "What is the total quantity?",
        "sql": """
        SELECT AVG(Quantity)
        FROM online_retail
    """,
        "expected": False
    },
    {
        "name": "Missing paise-to-rupees conversion",
        "question": "What is the average product price in rupees?",
        "sql": """
        SELECT AVG(current_price_paise)
        FROM products
    """,
        "expected": False
    },

    {
        "name": "Correct paise-to-rupees conversion",
        "question": "What is the average product price in rupees?",
        "sql": """
        SELECT AVG(current_price_paise) / 100.0
        FROM products
    """,
        "expected": True
    }

]


# ==================================================
# RUN TESTS
# ==================================================

def run_tests():

    passed = 0
    failed = 0

    print("\nDAY 30 - VALIDATOR ROBUSTNESS TEST")
    print("=" * 60)

    for index, test in enumerate(TEST_CASES, start=1):

        result = validator.semantic_validation_agent_v2(
            user_question=test["question"],
            sql_query=test["sql"],
            query_results=[],
            database_schema=(
                DATABASE_SCHEMA
                if "paise" in test["sql"].lower()
                else ONLINE_RETAIL_DATABASE_SCHEMA
            )
        )

        actual = result["is_valid"]
        expected = test["expected"]

        success = actual == expected

        if success:
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

    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)

    print(f"Total tests: {len(TEST_CASES)}")
    print(f"Passed:      {passed}")
    print(f"Failed:      {failed}")

    accuracy = (passed / len(TEST_CASES)) * 100

    print(f"Test agreement: {accuracy:.2f}%")

    print("\nTest execution completed.")


if __name__ == "__main__":
    run_tests()
