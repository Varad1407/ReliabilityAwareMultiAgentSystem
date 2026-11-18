
import sqlite3
from pathlib import Path


def create_database():
    # Find the main project directory
    project_dir = Path(__file__).resolve().parent.parent

    # Define the schema and database file locations
    schema_path = project_dir / "data" / "schema.sql"
    database_path = project_dir / "data" / "novaretail.db"

    # Check that the SQL schema exists
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    # Read the SQL instructions
    schema = schema_path.read_text(encoding="utf-8")


    # Connect to SQLite and create the database
    with sqlite3.connect(database_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON;")
        connection.executescript(schema)

        # Verify table columns
        print("\nDatabase structure:")

        for table_name in ["customers", "products", "orders", "order_items"]:
            columns = connection.execute(
                f"PRAGMA table_info({table_name});"
            ).fetchall()

            print(f"\n{table_name}:")
            for column in columns:
                print(f"  - {column[1]} ({column[2]})")

        # Verify foreign key relationships
        print("\nForeign key relationships:")

        for table_name in ["orders", "order_items"]:
            foreign_keys = connection.execute(
                f"PRAGMA foreign_key_list({table_name});"
            ).fetchall()

            print(f"\n{table_name}:")
            for fk in foreign_keys:
                print(f"  - {fk[3]} references {fk[2]}.{fk[4]}")

        # Get the names of the created tables
        tables = connection.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            ORDER BY name;
        """).fetchall()

    print("Database created successfully!")
    print(f"Database location: {database_path}")
    print("\nTables created:")

    for table in tables:
        print("-", table[0])


if __name__ == "__main__":
    create_database()
