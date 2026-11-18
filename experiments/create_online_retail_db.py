import pandas as pd
import sqlite3
from pathlib import Path

# Get the project directory
PROJECT_DIR = Path(__file__).resolve().parent.parent

# Define file paths
EXCEL_FILE = PROJECT_DIR / "data" / "Online Retail.xlsx"
DATABASE_FILE = PROJECT_DIR / "data" / "online_retail.db"

# Read the Excel dataset
print("Reading Excel dataset...")
df = pd.read_excel(EXCEL_FILE)

print("Dataset loaded successfully.")
print("Rows:", len(df))

# Connect to the new SQLite database
connection = sqlite3.connect(DATABASE_FILE)

# Import the dataset into SQLite
print("Importing data into SQLite...")
df.to_sql(
    "online_retail",
    connection,
    if_exists="replace",
    index=False
)

connection.close()

print("Database created successfully!")
print("Database location:", DATABASE_FILE)

# Verify imported records
connection = sqlite3.connect(DATABASE_FILE)

cursor = connection.cursor()

cursor.execute("SELECT COUNT(*) FROM online_retail")

row_count = cursor.fetchone()[0]

print("\n--- DATABASE VERIFICATION ---")
print("Records in SQLite:", row_count)

connection.close()

# Check missing values in SQLite
connection = sqlite3.connect(DATABASE_FILE)

cursor = connection.cursor()

print("\n--- MISSING VALUE VERIFICATION ---")

columns = [
    "Description",
    "CustomerID"
]

for column in columns:
    cursor.execute(
        f"SELECT COUNT(*) FROM online_retail WHERE {column} IS NULL"
    )

    missing_count = cursor.fetchone()[0]

    print(f"{column} missing values:", missing_count)

connection.close()

# Inspect transaction categories
connection = sqlite3.connect(DATABASE_FILE)

cursor = connection.cursor()

query = """
SELECT
    CASE
        WHEN InvoiceNo LIKE 'C%' THEN 'Cancellation'
        WHEN Quantity < 0 THEN 'Return'
        WHEN Quantity > 0 THEN 'Positive quantity'
        ELSE 'Zero quantity'
    END AS transaction_type,
    COUNT(*) AS record_count
FROM online_retail
GROUP BY transaction_type
ORDER BY transaction_type;
"""

cursor.execute(query)

print("\n--- TRANSACTION CATEGORY ANALYSIS ---")

for row in cursor.fetchall():
    print(row)

connection.close()

# Create transaction category views
connection = sqlite3.connect(DATABASE_FILE)

cursor = connection.cursor()

cursor.execute("""
CREATE VIEW IF NOT EXISTS cancellations AS
SELECT *
FROM online_retail
WHERE InvoiceNo LIKE 'C%';
""")

cursor.execute("""
CREATE VIEW IF NOT EXISTS positive_quantity_records AS
SELECT *
FROM online_retail
WHERE InvoiceNo NOT LIKE 'C%'
AND Quantity > 0;
""")

cursor.execute("""
CREATE VIEW IF NOT EXISTS returns AS
SELECT *
FROM online_retail
WHERE InvoiceNo NOT LIKE 'C%'
AND Quantity < 0;
""")

connection.commit()
connection.close()

print("\nThree SQL views created successfully!")

# Verify SQL views
connection = sqlite3.connect(DATABASE_FILE)

cursor = connection.cursor()

views = [
    "cancellations",
    "positive_quantity_records",
    "returns"
]

print("\n--- SQL VIEW VERIFICATION ---")

for view in views:
    cursor.execute(f"SELECT COUNT(*) FROM {view}")
    count = cursor.fetchone()[0]

    print(f"{view}: {count} records")

connection.close()