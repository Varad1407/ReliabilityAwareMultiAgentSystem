from src.nl_to_sql import ONLINE_RETAIL_DATABASE_SCHEMA
import sqlite3
from pathlib import Path

from src.agents import semantic_validation_agent_v2 as validator


# Database path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "online_retail.db"

# Isolate deterministic validator behaviour
validator.generate_response = lambda prompt: "VALID"


def execute_query(sql):
    connection = sqlite3.connect(
        f"file:{DB_PATH}?mode=ro",
        uri=True
    )

    try:
        cursor = connection.execute(sql)
        return cursor.fetchall()
    finally:
        connection.close()

def validate_query(question, sql, results):
    return validator.semantic_validation_agent_v2(
        user_question=question,
        sql_query=sql,
        query_results=results,
        database_schema=ONLINE_RETAIL_DATABASE_SCHEMA
    )


print("DAY 35 — FALSE ACCEPTANCE TESTING")
print("=" * 60)
print("Database:", DB_PATH)
print("Database exists:", DB_PATH.exists())
print("LLM response mocked as VALID")

print("\nTEST 1 — WRONG AGGREGATION")
print("=" * 60)

question = "How many distinct invoices are present?"

incorrect_sql = """
SELECT COUNT(*)
FROM online_retail
"""

results = execute_query(incorrect_sql)

decision = validate_query(
    question,
    incorrect_sql,
    results
)

print("Question:", question)
print("Incorrect SQL result:", results)
print("Validator decision:", decision)
print("Expected decision: REJECT (is_valid = False)")

print("\nTEST 2 — WRONG DATE FILTER")
print("=" * 60)

question = "How many records are present in November 2011?"

incorrect_sql = """
SELECT COUNT(*)
FROM online_retail
WHERE InvoiceDate >= '2011-10-01'
AND InvoiceDate < '2011-11-01'
"""

results = execute_query(incorrect_sql)

decision = validate_query(
    question,
    incorrect_sql,
    results
)

print("Question:", question)
print("Incorrect SQL result:", results)
print("Validator decision:", decision)
print("Expected decision: REJECT (is_valid = False)")

print("\nTEST 3 — WRONG TRANSACTION FILTER")
print("=" * 60)

question = "How many records have negative quantities, excluding cancelled invoices?"

incorrect_sql = """
SELECT COUNT(*)
FROM online_retail
WHERE Quantity < 0
"""

results = execute_query(incorrect_sql)

decision = validate_query(
    question,
    incorrect_sql,
    results
)

print("Question:", question)
print("Incorrect SQL result:", results)
print("Validator decision:", decision)
print("Expected decision: REJECT (is_valid = False)")

print("\nTEST 4 — WRONG SORTING")
print("=" * 60)

question = "What are the top 5 countries by number of records?"

incorrect_sql = """
SELECT Country, COUNT(*) AS total
FROM online_retail
GROUP BY Country
ORDER BY total ASC
LIMIT 5
"""

results = execute_query(incorrect_sql)

decision = validate_query(
    question,
    incorrect_sql,
    results
)

print("Question:", question)
print("Incorrect SQL result:", results)
print("Validator decision:", decision)
print("Expected decision: REJECT (is_valid = False)")