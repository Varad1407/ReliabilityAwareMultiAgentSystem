from database import get_connection
import sqlite3
from pathlib import Path


# Find the project directory
project_dir = Path(__file__).resolve().parent.parent

# Define the database location
database_path = project_dir / "data" / "novaretail.db"


def test_database():

    with get_connection() as connection:
        connection.execute("PRAGMA foreign_keys = ON;")

        # Test 1: Check the number of records
        print("\n--- RECORD COUNTS ---")

        tables = [
            "customers",
            "products",
            "orders",
            "order_items"
        ]

        for table in tables:

            result = connection.execute(
                f"SELECT COUNT(*) FROM {table};"
            ).fetchone()

            print(f"{table}: {result[0]}")

        # Test 2: Display five customers and their orders
        print("\n--- CUSTOMER ORDERS ---")

        results = connection.execute("""
            SELECT
                customers.customer_name,
                orders.order_id,
                orders.order_date,
                orders.status
            FROM customers
            JOIN orders
                ON customers.customer_id = orders.customer_id
            LIMIT 5;
        """).fetchall()

        for row in results:
            print(row)

        # Test 3: Calculate total revenue
        print("\n--- TOTAL ORDER-ITEM VALUE (ALL STATUSES) ---")

        result = connection.execute("""
            SELECT SUM(quantity * unit_price_paise)
            FROM order_items;
        """).fetchone()

        print(f"Total order-item value in paise: {result[0]}")

        # Test 4: Check for orders before customer signup
        print("\n--- DATA QUALITY CHECK ---")

        result = connection.execute("""
            SELECT COUNT(*)
            FROM orders
            JOIN customers
                ON orders.customer_id = customers.customer_id
            WHERE orders.order_date < customers.signup_date;
        """).fetchone()

        print(f"Orders before customer signup: {result[0]}")

        # Test 5: Check foreign-key enforcement
        print("\n--- FOREIGN KEY INTEGRITY TEST ---")

        try:
            connection.execute("BEGIN;")

            connection.execute("""
                INSERT INTO orders (
                    customer_id,
                    order_date,
                    status
                )
                VALUES (9999, '2025-12-01', 'Pending');
            """)

            print("ERROR: Invalid customer ID was accepted!")

        except sqlite3.IntegrityError:
            print("PASS: Invalid customer ID was rejected.")

        finally:
            connection.rollback()


if __name__ == "__main__":
    test_database()