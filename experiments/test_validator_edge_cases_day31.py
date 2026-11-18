
from agents import semantic_validation_agent_v2 as validator
from nl_to_sql import ONLINE_RETAIL_DATABASE_SCHEMA, DATABASE_SCHEMA

# Mock LLM response to isolate deterministic validation
validator.generate_response = lambda prompt: "VALID"


TEST_CASES = [

    # DATE FILTERS

    {
        "name": "Valid November date using inclusive last day",
        "question": "How many records were recorded in November 2011?",
        "sql": """
            SELECT COUNT(*) FROM online_retail
            WHERE InvoiceDate >= '2011-11-01'
            AND InvoiceDate <= '2011-11-30'
        """,
        "expected": True
    },

    {
        "name": "Incorrect date filter using exclusive start",
        "question": "How many records were recorded in November 2011?",
        "sql": """
            SELECT COUNT(*) FROM online_retail
            WHERE InvoiceDate > '2011-11-01'
            AND InvoiceDate < '2011-12-01'
        """,
        "expected": False
    },

    # CANCELLATION FILTERS

    {
        "name": "Cancellation exclusion using NOT LIKE",
        "question": "Count negative quantity records excluding cancellations.",
        "sql": """
            SELECT COUNT(*) FROM online_retail
            WHERE Quantity < 0
            AND NOT (InvoiceNo LIKE 'C%')
        """,
        "expected": True
    },

    {
        "name": "Cancellation exclusion using SUBSTR and !=",
        "question": "Count negative quantity records excluding cancellations.",
        "sql": """
            SELECT COUNT(*) FROM online_retail
            WHERE Quantity < 0
            AND SUBSTR(InvoiceNo, 1, 1) != 'C'
        """,
        "expected": True
    },

    {
        "name": "Incorrect cancellation filter",
        "question": "Count negative quantity records excluding cancellations.",
        "sql": """
            SELECT COUNT(*) FROM online_retail
            WHERE Quantity < 0
            AND InvoiceNo LIKE 'C%'
        """,
        "expected": False
    },

    # SORTING AND RANKING

    {
        "name": "Top five countries without LIMIT",
        "question": "Show the top 5 countries by number of records.",
        "sql": """
            SELECT Country, COUNT(*) AS total
            FROM online_retail
            GROUP BY Country
            ORDER BY total DESC
        """,
        "expected": False
    },

    {
        "name": "Lowest five countries with correct sorting",
        "question": "Show the lowest 5 countries by number of records.",
        "sql": """
            SELECT Country, COUNT(*) AS total
            FROM online_retail
            GROUP BY Country
            ORDER BY total ASC
            LIMIT 5
        """,
        "expected": True
    },

    # AGGREGATION

    {
        "name": "Correct average using AVG",
        "question": "What is the average UnitPrice?",
        "sql": """
            SELECT AVG(UnitPrice) FROM online_retail
        """,
        "expected": True
    },

    {
        "name": "Correct total quantity using SUM",
        "question": "What is the total quantity?",
        "sql": """
            SELECT SUM(Quantity) FROM online_retail
        """,
        "expected": True
    },

    {
        "name": "Incorrect distinct invoice count",
        "question": "How many distinct invoices are in the database?",
        "sql": """
            SELECT COUNT(*) FROM online_retail
        """,
        "expected": False
    },

    # CURRENCY CONVERSION

    {
        "name": "Equivalent conversion using multiplication",
        "question": "What is the average product price in rupees?",
        "sql": """
            SELECT AVG(current_price_paise) * 0.01
            FROM products
        """,
        "expected": True
    },

    {
        "name": "Incorrect currency conversion divisor",
        "question": "What is the average product price in rupees?",
        "sql": """
            SELECT AVG(current_price_paise) / 1000.0
            FROM products
        """,
        "expected": False
    }
]


def run_tests():

    passed = 0
    failed = 0

    print("\nDAY 31 - EXTENDED VALIDATOR EDGE CASE TEST")
    print("=" * 60)

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

    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    print(f"Total tests: {len(TEST_CASES)}")
    print(f"Passed:      {passed}")
    print(f"Failed:      {failed}")
    print(f"Test agreement: {passed / len(TEST_CASES) * 100:.2f}%")
    print("\nTest execution completed.")


if __name__ == "__main__":
    run_tests()
