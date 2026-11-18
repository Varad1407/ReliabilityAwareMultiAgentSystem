
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "online_retail.db"

QUERIES = {
    "NOT EXISTS": """
        SELECT COUNT(*)
        FROM online_retail o
        WHERE o.Quantity < 0
        AND NOT EXISTS (
            SELECT 1
            FROM online_retail c
            WHERE c.InvoiceNo = o.InvoiceNo
            AND c.InvoiceNo GLOB 'C*'
        )
    """,

    "NOT GLOB": """
        SELECT COUNT(*)
        FROM online_retail
        WHERE Quantity < 0
        AND InvoiceNo NOT GLOB 'C*'
    """,

    "SUBSTR": """
        SELECT COUNT(*)
        FROM online_retail
        WHERE Quantity < 0
        AND SUBSTR(InvoiceNo, 1, 1) != 'C'
    """
}


def main():
    print("\nDAY 36 — SQLITE QUERY PLAN INSPECTION")
    print("=" * 65)

    connection = sqlite3.connect(
        f"file:{DB_PATH.as_posix()}?mode=ro",
        uri=True
    )

    try:
        for name, query in QUERIES.items():
            print(f"\nQUERY: {name}")
            print("-" * 65)

            cursor = connection.execute(
                "EXPLAIN QUERY PLAN " + query
            )

            for row in cursor.fetchall():
                print(row)

    finally:
        connection.close()


if __name__ == "__main__":
    main()
