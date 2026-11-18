
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR / "src"))

from agents.semantic_validation_agent import semantic_validation_agent
from nl_to_sql import regenerate_sql_semantic


question = "How many customers are in the database?"


# TEST 1: Correct SQL query
correct_sql = "SELECT COUNT(*) FROM customers"
correct_results = [(30,)]

print("\nTEST 1: CORRECT SQL")
print("=" * 40)

result_1 = semantic_validation_agent(
    question,
    correct_sql,
    correct_results
)

print("Validation result:", result_1)


# TEST 2: Incorrect but executable SQL query
incorrect_sql = "SELECT COUNT(*) FROM products"
incorrect_results = [(20,)]

print("\nTEST 2: INCORRECT SQL")
print("=" * 40)

result_2 = semantic_validation_agent(
    question,
    incorrect_sql,
    incorrect_results
)

print("Validation result:", result_2)


# TEST 3: Semantic SQL correction
print("\nTEST 3: SEMANTIC SQL CORRECTION")
print("=" * 40)

semantic_feedback = (
    "The SQL query should use the customers table, "
    "not the products table."
)

corrected_sql = regenerate_sql_semantic(
    question,
    incorrect_sql,
    semantic_feedback
)

print("Original SQL:", incorrect_sql)
print("Corrected SQL:", corrected_sql)

# TEST 4: Incorrect aggregation (SUM instead of AVG)

aggregation_question = (
    "Show the average current price of products "
    "in each category, in rupees."
)

incorrect_aggregation_sql = """
SELECT category,
       SUM(current_price_paise) / 100.0 AS average_price_rupees
FROM products
GROUP BY category
ORDER BY category
"""

aggregation_results = [
    ("Accessories", 4900.0),
    ("Appliances", 19200.0),
    ("Electronics", 105200.0),
    ("Fashion", 10700.0),
    ("Furniture", 26500.0),
    ("Stationery", 370.0)
]

print("\nTEST 4: INCORRECT AGGREGATION")
print("=" * 40)

result_4 = semantic_validation_agent(
    aggregation_question,
    incorrect_aggregation_sql,
    aggregation_results
)

print("Validation result:", result_4)

# TEST 5: INCORRECT UNIT CONVERSION

print("\nTEST 5: INCORRECT UNIT CONVERSION")
print("=" * 40)

unit_question = (
    "Show the average current price of products "
    "in each category, in rupees."
)

incorrect_unit_sql = """
SELECT category,
       AVG(current_price_paise) AS average_price_rupees
FROM products
GROUP BY category
ORDER BY category
"""

result_5 = semantic_validation_agent(
    unit_question,
    incorrect_unit_sql,
    []
)

print("Validation result:", result_5)
