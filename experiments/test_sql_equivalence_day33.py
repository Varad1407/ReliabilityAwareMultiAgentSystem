
import sqlite3
from pathlib import Path

from agents import semantic_validation_agent_v2 as validator
from nl_to_sql import ONLINE_RETAIL_DATABASE_SCHEMA


# Isolate deterministic validation rules.
validator.generate_response = lambda prompt: "VALID"


# Locate the Online Retail database.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "data" / "online_retail.db"


# Four pairs of equivalent SQL formulations.
TEST_PAIRS = [

    {
        "name": "Date filtering",
        "question": "How many records were recorded in November 2011?",
        "queries": [
            {
                "name": "DATE with BETWEEN",
                "sql": """
                    SELECT COUNT(*)
                    FROM online_retail
                    WHERE DATE(InvoiceDate)
                    BETWEEN '2011-11-01' AND '2011-11-30'
                """
            },
            {
                "name": "Inclusive start and exclusive end",
                "sql": """
                    SELECT COUNT(*)
                    FROM online_retail
                    WHERE InvoiceDate >= '2011-11-01'
                    AND InvoiceDate < '2011-12-01'
                """
            }
        ]
    },

    {
        "name": "Cancellation filtering",
        "question": "Count negative quantity records excluding cancellations.",
        "queries": [
            {
                "name": "NOT GLOB",
                "sql": """
                    SELECT COUNT(*)
                    FROM online_retail
                    WHERE Quantity < 0
                    AND InvoiceNo NOT GLOB 'C*'
                """
            },
            {
                "name": "SUBSTR",
                "sql": """
                    SELECT COUNT(*)
                    FROM online_retail
                    WHERE Quantity < 0
                    AND SUBSTR(InvoiceNo, 1, 1) != 'C'
                """
            }
        ]
    },

    {
        "name": "Sorting by country record count",
        "question": "Show the top 5 countries by number of records.",
        "queries": [
            {
                "name": "ORDER BY COUNT(*)",
                "sql": """
                    SELECT Country, COUNT(*) AS total
                    FROM online_retail
                    GROUP BY Country
                    ORDER BY COUNT(*) DESC
                    LIMIT 5
                """
            },
            {
                "name": "ORDER BY aggregate alias",
                "sql": """
                    SELECT Country, COUNT(*) AS total
                    FROM online_retail
                    GROUP BY Country
                    ORDER BY total DESC
                    LIMIT 5
                """
            }
        ]
    },

    {
        "name": "Distinct customer counting",
        "question": "How many distinct customers are in the database?",
        "queries": [
            {
                "name": "COUNT DISTINCT",
                "sql": """
                    SELECT COUNT(DISTINCT CustomerID)
                    FROM online_retail
                """
            },
            {
                "name": "DISTINCT subquery",
                "sql": """
                    SELECT COUNT(*)
                    FROM (
                        SELECT DISTINCT CustomerID
                        FROM online_retail
                        WHERE CustomerID IS NOT NULL
                    )
                """
            }
        ]
    }

]


def execute_query(connection, sql):

    cursor = connection.cursor()
    cursor.execute(sql)

    return cursor.fetchall()


def run_experiment():

    print("\nDAY 33 - EXECUTABLE SQL EQUIVALENCE TEST")
    print("=" * 75)

    if not DATABASE_PATH.exists():
        print("ERROR: Online Retail database not found.")
        print(f"Expected location: {DATABASE_PATH}")
        return

    connection = sqlite3.connect(
        f"file:{DATABASE_PATH}?mode=ro",
        uri=True
    )

    total_pairs = 0
    equivalent_pairs = 0
    execution_failures = 0
    validator_acceptances = 0
    validator_rejections = 0

    try:

        for pair_number, pair in enumerate(TEST_PAIRS, start=1):

            total_pairs += 1

            print(f"\nPAIR {pair_number}: {pair['name']}")
            print("-" * 75)

            pair_results = []

            for query_number, query in enumerate(
                pair["queries"], start=1
            ):

                print(f"\nQuery {query_number}: {query['name']}")

                try:

                    results = execute_query(
                        connection,
                        query["sql"]
                    )

                    pair_results.append(results)

                    print(f"Execution successful: True")
                    print(f"Database result: {results}")

                    validation = (
                        validator.semantic_validation_agent_v2(
                            user_question=pair["question"],
                            sql_query=query["sql"],
                            query_results=results,
                            database_schema=ONLINE_RETAIL_DATABASE_SCHEMA
                        )
                    )

                    is_valid = validation["is_valid"]

                    if is_valid:
                        validator_acceptances += 1
                    else:
                        validator_rejections += 1

                    print(f"Validator accepted: {is_valid}")

                    if validation["feedback"]:
                        print(
                            f"Validator feedback: "
                            f"{validation['feedback']}"
                        )

                except Exception as error:

                    execution_failures += 1
                    pair_results.append(None)

                    print("Execution successful: False")
                    print(f"Error: {error}")

            # Compare actual database results.
            if (
                len(pair_results) == 2
                and pair_results[0] is not None
                and pair_results[1] is not None
            ):

                if pair_results[0] == pair_results[1]:

                    equivalent_pairs += 1
                    print("\nEQUIVALENCE: PASS")

                else:

                    print("\nEQUIVALENCE: FAIL")
                    print("The two queries returned different results.")

            else:

                print("\nEQUIVALENCE: NOT EVALUATED")

    finally:

        connection.close()

    print("\n" + "=" * 75)
    print("DAY 33 FINAL RESULTS")
    print("=" * 75)

    print(f"Total query pairs: {total_pairs}")
    print(f"Equivalent pairs: {equivalent_pairs}")
    print(f"Non-equivalent or incomplete pairs: "
          f"{total_pairs - equivalent_pairs}")
    print(f"Execution failures: {execution_failures}")
    print(f"Validator acceptances: {validator_acceptances}")
    print(f"Validator rejections: {validator_rejections}")

    print(
        f"SQL equivalence rate: "
        f"{equivalent_pairs / total_pairs * 100:.2f}%"
    )

    print("\nDay 33 experiment completed.")


if __name__ == "__main__":
    run_experiment()
