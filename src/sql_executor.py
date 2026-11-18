
import sqlite3
import time

from database import (
    get_readonly_connection,
    online_retail_database_path
)


# --------------------------------------------------
# QUERY EXECUTION SAFETY LIMITS
# --------------------------------------------------

MAX_EXECUTION_TIME = 5  # seconds
MAX_RESULT_ROWS = 100


# --------------------------------------------------
# SQL VALIDATION
# --------------------------------------------------

def validate_sql(query):

    query = query.strip()

    if not query:
        return False, "SQL query is empty."

    first_keyword = query.split(maxsplit=1)[0].upper()

    if first_keyword not in ("SELECT", "WITH"):
        return False, "Only SELECT queries and CTE queries are allowed."

    if "--" in query or "/*" in query or "*/" in query:
        return False, "SQL comments are not allowed."

    statements = query.rstrip(";").split(";")

    if len(statements) > 1:
        return False, "Multiple SQL statements are not allowed."

    return True, "SQL query is valid."


# --------------------------------------------------
# SQL QUERY EXECUTION
# --------------------------------------------------

def execute_sql(query, db_path=None):
    """
    Execute a validated SQL query using a read-only connection.

    If db_path is not provided, NovaRetail is used.
    A different database can be selected by passing its path.
    """

    is_valid, message = validate_sql(query)

    if not is_valid:
        return {
            "success": False,
            "error_type": "VALIDATION_ERROR",
            "error": message
        }

    connection = None

    try:

        # Connect to the selected database
        connection = get_readonly_connection(db_path)

        # Set a query execution timeout
        start_time = time.monotonic()

        def query_timeout():

            elapsed_time = time.monotonic() - start_time

            if elapsed_time > MAX_EXECUTION_TIME:
                return 1

            return 0

        connection.set_progress_handler(query_timeout, 1000)

        cursor = connection.execute(query)

        columns = [
            description[0]
            for description in cursor.description
        ]

        # Fetch one extra row to detect truncation
        rows = cursor.fetchmany(MAX_RESULT_ROWS + 1)

        truncated = len(rows) > MAX_RESULT_ROWS

        rows = rows[:MAX_RESULT_ROWS]

        return {
            "success": True,
            "columns": columns,
            "rows": rows,
            "truncated": truncated
        }

    except sqlite3.OperationalError as error:

        error_message = str(error)

        if "interrupted" in error_message.lower():
            error_type = "TIMEOUT"
            error_message = "Query exceeded the maximum execution time."
        else:
            error_type = "SQL_EXECUTION_ERROR"

        return {
            "success": False,
            "error_type": error_type,
            "error": error_message
        }

    except sqlite3.Error as error:

        return {
            "success": False,
            "error_type": "DATABASE_ERROR",
            "error": str(error)
        }

    finally:

        if connection is not None:
            connection.close()


# --------------------------------------------------
# TESTING
# --------------------------------------------------

if __name__ == "__main__":

    # ----------------------------------------------
    # TEST 1: NOVARETAIL DEFAULT DATABASE
    # ----------------------------------------------

    print("\nTEST 1: NOVARETAIL DEFAULT DATABASE")

    result = execute_sql(
        "SELECT COUNT(*) FROM customers;"
    )

    print("Result:", result)


    # ----------------------------------------------
    # TEST 2: ONLINE RETAIL DATABASE
    # ----------------------------------------------

    print("\nTEST 2: ONLINE RETAIL DATABASE")

    result = execute_sql(
        "SELECT COUNT(*) FROM online_retail;",
        online_retail_database_path
    )

    print("Result:", result)


    # ----------------------------------------------
    # TEST 3: NOVARETAIL QUERY TESTS
    # ----------------------------------------------

    print("\nTEST 3: NOVARETAIL QUERY EXECUTION TESTS")

    test_queries = [

        """
        WITH city_orders AS (
            SELECT customer_id, COUNT(*) AS order_count
            FROM orders
            GROUP BY customer_id
        )
        SELECT customer_id, order_count
        FROM city_orders
        ORDER BY order_count DESC
        LIMIT 5;
        """,

        "SELECT * FROM customers LIMIT 5;",

        "SELECT * FROM orders;",

        "SELECT 1 AS test_number FROM orders CROSS JOIN orders;",

        "SELECT COUNT(*) FROM orders;",

        "SELECT * FROM unknown_table;",

        """
        INSERT INTO customers
        (customer_name, city, signup_date)
        VALUES ('Test User', 'Pune', '2025-01-01');
        """,

        """
        WITH RECURSIVE numbers(x) AS (
            SELECT 1
            UNION ALL
            SELECT x + 1 FROM numbers WHERE x < 1000000000
        )
        SELECT SUM(x) FROM numbers;
        """
    ]

    for query in test_queries:

        print("\nQuery:", query)

        result = execute_sql(query)

        print("Result:", result)


    # ----------------------------------------------
    # TEST 4: ONLINE RETAIL READ-ONLY QUERY
    # ----------------------------------------------

    print("\nTEST 4: ONLINE RETAIL READ-ONLY QUERY")

    result = execute_sql(
        """
        SELECT Country, COUNT(*) AS record_count
        FROM online_retail
        GROUP BY Country
        ORDER BY record_count DESC
        LIMIT 5;
        """,
        online_retail_database_path
    )

    print("Result:", result)


    # ----------------------------------------------
    # TEST 5: DIRECT READ-ONLY PROTECTION
    # ----------------------------------------------

    print("\nTEST 5: DIRECT READ-ONLY PROTECTION")

    connection = None

    try:

        connection = get_readonly_connection()

        connection.execute("""
            INSERT INTO customers (
                customer_name,
                city,
                signup_date
            )
            VALUES ('Test User', 'Pune', '2025-01-01');
        """)

        print("ERROR: Database allowed a write!")

    except sqlite3.Error as error:

        print("PASS: Database blocked the write.")
        print("SQLite error:", error)

    finally:

        if connection is not None:
            connection.close()


    print("\nAll SQL Executor tests completed.")
