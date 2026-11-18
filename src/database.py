
import sqlite3
from pathlib import Path


# --------------------------------------------------
# PROJECT CONFIGURATION
# --------------------------------------------------

project_dir = Path(__file__).resolve().parent.parent

# Default database: NovaRetail
database_path = project_dir / "data" / "novaretail.db"

# External database: UCI Online Retail
online_retail_database_path = (
    project_dir / "data" / "online_retail.db"
)


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

def get_connection(db_path=None):
    """
    Create a regular SQLite database connection.

    If no database path is provided, NovaRetail is used.
    """

    selected_database = (
        Path(db_path) if db_path else database_path
    )

    connection = sqlite3.connect(selected_database)

    # Enable foreign key enforcement
    connection.execute("PRAGMA foreign_keys = ON;")

    return connection


# --------------------------------------------------
# SQLITE SECURITY AUTHORIZER
# --------------------------------------------------

def database_authorizer(
    action,
    arg1,
    arg2,
    database_name,
    trigger_name
):
    """
    Allow read-only SQL operations.
    Block database modifications and other operations.
    """

    allowed_actions = {
        sqlite3.SQLITE_SELECT,
        sqlite3.SQLITE_READ,
        sqlite3.SQLITE_FUNCTION,
        sqlite3.SQLITE_RECURSIVE
    }

    if action in allowed_actions:
        return sqlite3.SQLITE_OK

    return sqlite3.SQLITE_DENY


# --------------------------------------------------
# READ-ONLY DATABASE CONNECTION
# --------------------------------------------------

def get_readonly_connection(db_path=None):
    """
    Create a read-only SQLite connection.

    If no database path is provided, NovaRetail is used.
    The SQLite authorizer is applied to the connection.
    """

    selected_database = (
        Path(db_path) if db_path else database_path
    )

    readonly_path = (
        selected_database.resolve().as_uri() + "?mode=ro"
    )

    connection = sqlite3.connect(
        readonly_path,
        uri=True
    )

    # Enable SQLite security authorizer
    connection.set_authorizer(database_authorizer)

    return connection


# --------------------------------------------------
# TESTING
# --------------------------------------------------

if __name__ == "__main__":

    # ----------------------------------------------
    # TEST 1: NOVARETAIL DATABASE CONNECTION
    # ----------------------------------------------

    print("TEST 1: NOVARETAIL DATABASE CONNECTION")

    connection = get_connection()

    print("Database connected successfully!")

    cursor = connection.execute(
        "SELECT COUNT(*) FROM customers;"
    )

    customer_count = cursor.fetchone()[0]

    print(f"Total customers: {customer_count}")

    connection.close()

    print("Database connection closed.")


    # ----------------------------------------------
    # TEST 2: ONLINE RETAIL DATABASE CONNECTION
    # ----------------------------------------------

    print("\nTEST 2: ONLINE RETAIL DATABASE CONNECTION")

    connection = get_connection(
        online_retail_database_path
    )

    cursor = connection.execute(
        "SELECT COUNT(*) FROM online_retail;"
    )

    record_count = cursor.fetchone()[0]

    print(f"Total Online Retail records: {record_count}")

    connection.close()


    # ----------------------------------------------
    # TEST 3: SQLITE AUTHORIZER TESTS
    # ----------------------------------------------

    print("\nTEST 3: SQLITE AUTHORIZER TESTS")

    readonly_connection = get_readonly_connection()

    test_queries = [
        (
            "SELECT",
            "SELECT COUNT(*) FROM customers;",
            True
        ),
        (
            "SELECT JOIN",
            """
            SELECT customers.customer_name, orders.order_id
            FROM customers
            JOIN orders
            ON customers.customer_id = orders.customer_id
            LIMIT 5;
            """,
            True
        ),
        (
            "SELECT SUM",
            "SELECT SUM(quantity) FROM order_items;",
            True
        ),
        (
            "INSERT",
            """
            INSERT INTO customers
            (customer_name, city, signup_date)
            VALUES ('Test User', 'Pune', '2025-01-01');
            """,
            False
        ),
        (
            "UPDATE",
            """
            UPDATE customers
            SET city = 'Pune'
            WHERE customer_id = 1;
            """,
            False
        ),
        (
            "DELETE",
            """
            DELETE FROM customers
            WHERE customer_id = 1;
            """,
            False
        ),
        (
            "CREATE TABLE",
            """
            CREATE TABLE security_test (
                id INTEGER PRIMARY KEY
            );
            """,
            False
        ),
        (
            "PRAGMA",
            "PRAGMA table_info(customers);",
            False
        ),
        (
            "ATTACH DATABASE",
            "ATTACH DATABASE ':memory:' AS test_database;",
            False
        )
    ]

    for test_name, query, should_succeed in test_queries:

        print(f"\nTesting {test_name}...")

        try:
            readonly_connection.execute(query)

            if should_succeed:
                print(f"PASS: {test_name} was allowed.")
            else:
                print(
                    f"FAIL: {test_name} was unexpectedly allowed."
                )

        except sqlite3.DatabaseError as error:

            if should_succeed:
                print(
                    f"FAIL: {test_name} was unexpectedly blocked."
                )
                print("Error:", error)

            else:
                print(f"PASS: {test_name} was blocked.")
                print("Error:", error)

    readonly_connection.close()


    # ----------------------------------------------
    # TEST 4: ONLINE RETAIL READ-ONLY CONNECTION
    # ----------------------------------------------

    print("\nTEST 4: ONLINE RETAIL READ-ONLY CONNECTION")

    readonly_connection = get_readonly_connection(
        online_retail_database_path
    )

    cursor = readonly_connection.execute(
        "SELECT COUNT(*) FROM online_retail;"
    )

    print(
        "Online Retail read-only record count:",
        cursor.fetchone()[0]
    )

    readonly_connection.close()

    print("\nAll database tests completed.")
