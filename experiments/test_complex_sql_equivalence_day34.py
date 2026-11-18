
import sqlite3
from pathlib import Path

from src.agents import semantic_validation_agent_v2 as validator
from src.nl_to_sql import ONLINE_RETAIL_DATABASE_SCHEMA


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "data" / "online_retail.db"

# Mock LLM response to isolate deterministic validator checks
validator.generate_response = lambda prompt: "VALID"


def execute_query(connection, query):
    cursor = connection.execute(query)
    return cursor.fetchall()


def validate_query(question, query, result):
    return validator.semantic_validation_agent_v2(
        question,
        query,
        result,
        ONLINE_RETAIL_DATABASE_SCHEMA
    )


def main():

    connection = sqlite3.connect(
        f"file:{DB_PATH}?mode=ro",
        uri=True
    )

    try:

        # ====================================================
        # EXPERIMENT 1: NESTED SUBQUERY VS CTE
        # ====================================================

        question_1 = (
            "How many distinct customers are present "
            "in the Online Retail dataset?"
        )

        query_nested = """
        SELECT COUNT(*)
        FROM (
            SELECT DISTINCT CustomerID
            FROM online_retail
            WHERE CustomerID IS NOT NULL
        )
        """

        query_cte = """
        WITH distinct_customers AS (
            SELECT DISTINCT CustomerID
            FROM online_retail
            WHERE CustomerID IS NOT NULL
        )
        SELECT COUNT(*)
        FROM distinct_customers
        """

        result_nested = execute_query(connection, query_nested)
        result_cte = execute_query(connection, query_cte)

        validation_nested = validate_query(
            question_1, query_nested, result_nested
        )

        validation_cte = validate_query(
            question_1, query_cte, result_cte
        )

        equivalent_1 = result_nested == result_cte

        print("\nDAY 34 — EXPERIMENT 1")
        print("=" * 70)
        print("Nested subquery result:", result_nested)
        print("CTE result:", result_cte)
        print("Nested subquery validator:", validation_nested)
        print("CTE validator:", validation_cte)
        print("Results equivalent:", equivalent_1)
        print(
            "Both accepted:",
            validation_nested.get("is_valid", False)
            and validation_cte.get("is_valid", False)
        )

        # ====================================================
        # EXPERIMENT 2: CASE WHEN VS WHERE
        # ====================================================

        question_2 = (
            "How many cancellation records are present "
            "in the dataset?"
        )

        query_case_when = """
        SELECT SUM(
            CASE
                WHEN InvoiceNo GLOB 'C*' THEN 1
                ELSE 0
            END
        )
        FROM online_retail
        """

        query_where = """
        SELECT COUNT(*)
        FROM online_retail
        WHERE InvoiceNo GLOB 'C*'
        """

        result_case_when = execute_query(
            connection, query_case_when
        )

        result_where = execute_query(
            connection, query_where
        )

        validation_case_when = validate_query(
            question_2, query_case_when, result_case_when
        )

        validation_where = validate_query(
            question_2, query_where, result_where
        )

        equivalent_2 = result_case_when == result_where

        print("\n\nDAY 34 — EXPERIMENT 2")
        print("=" * 70)
        print("CASE WHEN result:", result_case_when)
        print("WHERE result:", result_where)
        print("CASE WHEN validator:", validation_case_when)
        print("WHERE validator:", validation_where)
        print("Results equivalent:", equivalent_2)
        print(
            "Both accepted:",
            validation_case_when.get("is_valid", False)
            and validation_where.get("is_valid", False)
        )

        # ====================================================
        # EXPERIMENT 3: STRFTIME VS SUBSTR DATE EXTRACTION
        # ====================================================

        question_3 = (
            "How many records are present in November 2011?"
        )

        query_strftime = """
        SELECT COUNT(*)
        FROM online_retail
        WHERE STRFTIME('%Y-%m', InvoiceDate) = '2011-11'
        """

        query_substr = """
        SELECT COUNT(*)
        FROM online_retail
        WHERE SUBSTR(InvoiceDate, 1, 7) = '2011-11'
        """

        result_strftime = execute_query(
            connection, query_strftime
        )

        result_substr = execute_query(
            connection, query_substr
        )

        validation_strftime = validate_query(
            question_3, query_strftime, result_strftime
        )

        validation_substr = validate_query(
            question_3, query_substr, result_substr
        )

        equivalent_3 = result_strftime == result_substr

        print("\n\nDAY 34 — EXPERIMENT 3")
        print("=" * 70)
        print("STRFTIME result:", result_strftime)
        print("SUBSTR result:", result_substr)
        print("STRFTIME validator:", validation_strftime)
        print("SUBSTR validator:", validation_substr)
        print("Results equivalent:", equivalent_3)
        print(
            "Both accepted:",
            validation_strftime.get("is_valid", False)
            and validation_substr.get("is_valid", False)
        )

        # ====================================================
        # EXPERIMENT 4: NOT EXISTS VS NOT GLOB
        # ====================================================

        question_4 = (
            "How many return records are present, "
            "excluding cancellation invoices?"
        )

        # Create a temporary table containing cancellation
        # invoice numbers. The temporary index makes the
        # correlated NOT EXISTS lookup efficient.
        connection.execute("""
            CREATE TEMP TABLE cancellation_invoices AS
            SELECT DISTINCT InvoiceNo
            FROM online_retail
        """)

        connection.execute("""
            CREATE UNIQUE INDEX idx_temp_cancellation_invoice
            ON cancellation_invoices(InvoiceNo)
        """)

        query_not_exists = """
        SELECT COUNT(*)
        FROM online_retail AS r
        WHERE r.Quantity < 0
        AND NOT EXISTS (
            SELECT 1
            FROM cancellation_invoices AS c
            WHERE c.InvoiceNo = r.InvoiceNo
            AND c.InvoiceNo GLOB 'C*'
        )
        """

        query_not_glob = """
        SELECT COUNT(*)
        FROM online_retail
        WHERE Quantity < 0
        AND InvoiceNo NOT GLOB 'C*'
        """

        result_not_exists = execute_query(
            connection, query_not_exists
        )

        result_not_glob = execute_query(
            connection, query_not_glob
        )

        validation_not_exists = validate_query(
            question_4, query_not_exists, result_not_exists
        )

        validation_not_glob = validate_query(
            question_4, query_not_glob, result_not_glob
        )

        equivalent_4 = result_not_exists == result_not_glob

        print("\n\nDAY 34 — EXPERIMENT 4")
        print("=" * 70)
        print("NOT EXISTS result:", result_not_exists)
        print("NOT GLOB result:", result_not_glob)
        print("NOT EXISTS validator:", validation_not_exists)
        print("NOT GLOB validator:", validation_not_glob)
        print("Results equivalent:", equivalent_4)
        print(
            "Both accepted:",
            validation_not_exists.get("is_valid", False)
            and validation_not_glob.get("is_valid", False)
        )

        # ====================================================
        # FINAL SUMMARY
        # ====================================================

        print("\n\nDAY 34 — FINAL SUMMARY")
        print("=" * 70)

        experiments = [
            ("Nested subquery vs CTE", equivalent_1),
            ("CASE WHEN vs WHERE", equivalent_2),
            ("STRFTIME vs SUBSTR", equivalent_3),
            ("NOT EXISTS vs NOT GLOB", equivalent_4)
        ]

        for name, equivalent in experiments:
            print(f"{name}: {'PASS' if equivalent else 'FAIL'}")

        total_equivalent = sum(
            equivalent for _, equivalent in experiments
        )

        print("\nTotal experiments:", len(experiments))
        print("Equivalent results:", total_equivalent)
        print(
            "Non-equivalent results:",
            len(experiments) - total_equivalent
        )

    finally:
        connection.close()


if __name__ == "__main__":
    main()
