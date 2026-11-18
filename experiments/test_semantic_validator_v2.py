
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))

from agents.semantic_validation_agent_v2 import (
    semantic_validation_agent_v2
)
from nl_to_sql import (
    DATABASE_SCHEMA,
    ONLINE_RETAIL_DATABASE_SCHEMA
)


tests = [

    {
        "name": "Wrong aggregation",
        "question": "What is the average price of products in rupees?",
        "sql": """
            SELECT SUM(current_price_paise) / 100.0
            FROM products
        """,
        "schema": DATABASE_SCHEMA,
        "expected": False
    },

    {
        "name": "Missing currency conversion",
        "question": "What is the average price of products in rupees?",
        "sql": """
            SELECT AVG(current_price_paise)
            FROM products
        """,
        "schema": DATABASE_SCHEMA,
        "expected": False
    },

    {
        "name": "Wrong sorting",
        "question": "Show the five countries with the highest number of records, sorted from highest to lowest record count.",
        "sql": """
            SELECT Country, COUNT(*) AS record_count
            FROM online_retail
            GROUP BY Country
            ORDER BY record_count ASC, Country ASC
            LIMIT 5
        """,
        "schema": ONLINE_RETAIL_DATABASE_SCHEMA,
        "expected": False
    },

    {
        "name": "Correct November date filter",
        "question": "How many records were recorded in November 2011?",
        "sql": """
            SELECT COUNT(*)
            FROM online_retail
            WHERE InvoiceDate >= '2011-11-01'
            AND InvoiceDate < '2011-12-01'
        """,
        "schema": ONLINE_RETAIL_DATABASE_SCHEMA,
        "expected": True
    },

    {
        "name": "Correct cancellation exclusion",
        "question": "How many non-cancellation records have a negative quantity?",
        "sql": """
            SELECT COUNT(*)
            FROM online_retail
            WHERE InvoiceNo NOT LIKE 'C%'
            AND Quantity < 0
        """,
        "schema": ONLINE_RETAIL_DATABASE_SCHEMA,
        "expected": True
    }
]


print("\nSYSTEM C V2 — VALIDATION TESTS")
print("=" * 60)

for test in tests:

    result = semantic_validation_agent_v2(
        test["question"],
        test["sql"],
        [],
        test["schema"]
    )

    passed = result["is_valid"] == test["expected"]

    print("\nTest:", test["name"])
    print("Expected valid:", test["expected"])
    print("Actual valid:", result["is_valid"])
    print("Test passed:", passed)
    print("Feedback:", result["feedback"])

print("\nAll tests completed.")
