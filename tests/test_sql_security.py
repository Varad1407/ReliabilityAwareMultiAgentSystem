import sqlite3
import unittest
import sys
from pathlib import Path

# Add the src directory to Python's import path
project_dir = Path(__file__).resolve().parent.parent
src_dir = project_dir / "src"

sys.path.insert(0, str(src_dir))

from database import get_readonly_connection


class TestSQLSecurity(unittest.TestCase):

    def setUp(self):
        # Create a fresh read-only connection for each test
        self.connection = get_readonly_connection()

    def tearDown(self):
        # Close the connection after each test
        self.connection.close()

    # Test 1: SELECT should be allowed
    def test_select_allowed(self):

        result = self.connection.execute(
            "SELECT COUNT(*) FROM customers;"
        )

        self.assertEqual(result.fetchone()[0], 30)

    # Test 2: JOIN should be allowed
    def test_select_join_allowed(self):

        result = self.connection.execute("""
            SELECT customers.customer_name, orders.order_id
            FROM customers
            JOIN orders
            ON customers.customer_id = orders.customer_id
            LIMIT 5;
        """)

        rows = result.fetchall()

        self.assertLessEqual(len(rows), 5)

    # Test 3: SUM should be allowed
    def test_select_sum_allowed(self):

        result = self.connection.execute(
            "SELECT SUM(quantity) FROM order_items;"
        )

        self.assertIsNotNone(result.fetchone()[0])

    # Test 4: INSERT should be blocked
    def test_insert_blocked(self):

        with self.assertRaises(sqlite3.DatabaseError):
            self.connection.execute("""
                INSERT INTO customers
                (customer_name, city, signup_date)
                VALUES ('Test User', 'Pune', '2025-01-01');
            """)

    # Test 5: UPDATE should be blocked
    def test_update_blocked(self):

        with self.assertRaises(sqlite3.DatabaseError):
            self.connection.execute("""
                UPDATE customers
                SET city = 'Pune'
                WHERE customer_id = 1;
            """)

    # Test 6: DELETE should be blocked
    def test_delete_blocked(self):

        with self.assertRaises(sqlite3.DatabaseError):
            self.connection.execute("""
                DELETE FROM customers
                WHERE customer_id = 1;
            """)

    # Test 7: CREATE TABLE should be blocked
    def test_create_table_blocked(self):

        with self.assertRaises(sqlite3.DatabaseError):
            self.connection.execute("""
                CREATE TABLE security_test (
                    id INTEGER PRIMARY KEY
                );
            """)

    # Test 8: PRAGMA should be blocked
    def test_pragma_blocked(self):

        with self.assertRaises(sqlite3.DatabaseError):
            self.connection.execute(
                "PRAGMA table_info(customers);"
            )

    # Test 9: ATTACH DATABASE should be blocked
    def test_attach_blocked(self):

        with self.assertRaises(sqlite3.DatabaseError):
            self.connection.execute(
                "ATTACH DATABASE ':memory:' AS test_database;"
            )

if __name__ == "__main__":
    unittest.main(verbosity=2)



