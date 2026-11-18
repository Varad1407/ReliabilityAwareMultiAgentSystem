
import re

from llm_client import generate_response
from nl_to_sql import DATABASE_SCHEMA


def semantic_validation_agent(
    user_question,
    sql_query,
    query_results,
    database_schema=DATABASE_SCHEMA
):

    question_lower = user_question.lower()
    sql_upper = sql_query.upper()

    # Normalize SQL by removing whitespace.
    sql_normalized = "".join(sql_upper.split())

    # ==================================================
    # 1. DETERMINISTIC CHECK: AVERAGE VS SUM
    # ==================================================

    uses_sum = bool(re.search(r"\bSUM\s*\(", sql_upper))
    uses_avg = bool(re.search(r"\bAVG\s*\(", sql_upper))

    if (
        "average" in question_lower
        and uses_sum
        and not uses_avg
    ):
        return {
            "is_valid": False,
            "feedback": (
                "The question asks for an average, "
                "but the SQL uses SUM instead of AVG."
            )
        }

    # ==================================================
    # 2. DATABASE-SPECIFIC PRICE VALIDATION
    # ==================================================

    schema_upper = database_schema.upper()

    # Check whether this database stores prices in paise.
    stores_prices_in_paise = (
        "CURRENT_PRICE_PAISE" in schema_upper
        or "UNIT_PRICE_PAISE" in schema_upper
    )

    if stores_prices_in_paise:

        uses_paise_column = (
            "CURRENT_PRICE_PAISE" in sql_normalized
            or "UNIT_PRICE_PAISE" in sql_normalized
        )

        has_paise_conversion = "/100" in sql_normalized

        if (
            "rupees" in question_lower
            and uses_paise_column
            and not has_paise_conversion
        ):
            return {
                "is_valid": False,
                "feedback": (
                    "The question asks for prices in rupees, "
                    "but the SQL does not convert paise to rupees. "
                    "Divide the price by 100.0."
                )
            }

    # ==================================================
    # 3. DATABASE-AWARE LLM VALIDATION
    # ==================================================

    prompt = f"""
You are a strict semantic SQL validation assistant.

Your task is to determine whether the SQL query correctly
answers the user's original question.

DATABASE SCHEMA:
{database_schema}

USER QUESTION:
{user_question}

GENERATED SQL QUERY:
{sql_query}

DATABASE RESULTS:
{query_results}

VALIDATION RULES:

1. QUESTION UNDERSTANDING:
Understand exactly what information the user requested.

2. TABLES AND COLUMNS:
Check whether the correct tables and columns are used.
Use only the tables and columns in the provided schema.

3. AGGREGATION CHECK — VERY IMPORTANT:

Carefully distinguish between these operations:

- COUNT: counts records or items.
- SUM: calculates the total of numeric values.
- AVG: calculates the arithmetic average of numeric values.

The SQL aggregation must match the user's wording.

Examples:
- "How many products?" requires COUNT.
- "Total quantity" requires SUM.
- "Average product price" requires AVG.

If the question asks for an average but SQL uses SUM
instead of AVG, the query MUST be marked INVALID.

Do not accept an incorrect aggregation just because
the SQL executes successfully or returns plausible values.

4. CALCULATIONS AND UNITS:

Check mathematical expressions and unit conversions
using the information in the provided database schema.

Do not assume all databases use the same currency
or measurement units.

If the schema states that prices are stored in paise,
conversion to rupees requires division by 100.0.

If the schema states that prices are already stored
in pounds sterling, do not divide those prices by 100.

Never introduce a unit conversion that is not required
by the database schema or the user's question.

5. FILTERS:
Check date ranges, categories, statuses and other conditions.

6. GROUPING:
Check whether GROUP BY uses the correct columns
for the requested result.

7. JOINS:
Check whether joins connect the correct tables
and relationships defined in the schema.

8. ORDERING AND LIMITS:
Check whether ORDER BY and LIMIT satisfy the question.

9. DATA SEMANTICS:

Pay attention to the meaning of records in the dataset.

For example, distinguish between:
- Total records.
- Distinct invoices.
- Distinct customers.
- Positive and negative quantities.
- Cancellation records and return records.

Do not treat these measurements as interchangeable.

Only apply these distinctions when relevant
to the provided database schema and user question.

10. FINAL DECISION:

If any important part of the SQL does not match
the original question, mark it INVALID.

Do not assume a query is correct simply because it executes.

RESPONSE FORMAT:

If correct, respond with exactly:
VALID

If incorrect, respond with:
INVALID: followed by a short explanation.

Do not generate corrected SQL.
Do not include any other introductory text.
"""

    response = generate_response(prompt).strip()

    # ==================================================
    # 4. PROCESS VALIDATION RESPONSE
    # ==================================================

    if response.upper().startswith("INVALID"):

        feedback = response[len("INVALID"):].strip(" :-\n")

        return {
            "is_valid": False,
            "feedback": feedback
        }

    elif response.upper().startswith("VALID"):

        return {
            "is_valid": True,
            "feedback": None
        }

    else:

        return {
            "is_valid": False,
            "feedback": (
                "The semantic validator returned an unclear response."
            )
        }


# ==================================================
# 5. BASIC CONFIGURATION TEST
# ==================================================

if __name__ == "__main__":

    from nl_to_sql import ONLINE_RETAIL_DATABASE_SCHEMA

    print("Testing semantic validator configuration...")

    print("\nNovaRetail:")
    print(
        "Paise-based price validation:",
        "CURRENT_PRICE_PAISE" in DATABASE_SCHEMA.upper()
    )
    print("\nOnline Retail:")
    print(
        "Paise-based price validation:",
        "CURRENT_PRICE_PAISE" in ONLINE_RETAIL_DATABASE_SCHEMA.upper()
    )

    print("\nBoth database schemas can be passed to the validator.")

