import sqlite3
from pathlib import Path

# Get project directory
PROJECT_DIR = Path(__file__).resolve().parent.parent

# Database location
DATABASE_FILE = PROJECT_DIR / "data" / "online_retail.db"

# Connect to SQLite
connection = sqlite3.connect(DATABASE_FILE)

cursor = connection.cursor()

print("Connected to Online Retail database successfully!")

# Inspect database tables and views
cursor.execute("""
SELECT name, type
FROM sqlite_master
WHERE type IN ('table', 'view')
ORDER BY type, name;
""")

print("\n--- DATABASE STRUCTURE ---")

for item in cursor.fetchall():
    print(item)

connection.close()

# Inspect transaction date range
connection = sqlite3.connect(DATABASE_FILE)
cursor = connection.cursor()

cursor.execute("""
SELECT
    MIN(InvoiceDate),
    MAX(InvoiceDate)
FROM online_retail;
""")

date_range = cursor.fetchone()

print("\n--- DATASET DATE RANGE ---")
print("Earliest transaction:", date_range[0])
print("Latest transaction:", date_range[1])

connection.close()

# Inspect country distribution
connection = sqlite3.connect(DATABASE_FILE)
cursor = connection.cursor()

cursor.execute("""
SELECT
    Country,
    COUNT(*) AS transaction_records
FROM online_retail
GROUP BY Country
ORDER BY transaction_records DESC
LIMIT 10;
""")

print("\n--- TOP 10 COUNTRIES ---")

for row in cursor.fetchall():
    print(row)

connection.close()

# Inspect product diversity
connection = sqlite3.connect(DATABASE_FILE)
cursor = connection.cursor()

cursor.execute("""
SELECT COUNT(DISTINCT StockCode)
FROM online_retail;
""")

unique_products = cursor.fetchone()[0]

print("\n--- PRODUCT ANALYSIS ---")
print("Unique product codes:", unique_products)

cursor.execute("""
SELECT
    Description,
    COUNT(*) AS record_count
FROM online_retail
WHERE Description IS NOT NULL
GROUP BY Description
ORDER BY record_count DESC
LIMIT 10;
""")

print("\n--- TOP 10 PRODUCT DESCRIPTIONS ---")

for row in cursor.fetchall():
    print(row)

connection.close()

# Inspect invoice statistics
connection = sqlite3.connect(DATABASE_FILE)
cursor = connection.cursor()

cursor.execute("""
SELECT
    COUNT(DISTINCT InvoiceNo),
    COUNT(DISTINCT CustomerID),
    COUNT(DISTINCT Country)
FROM online_retail;
""")

invoice_stats = cursor.fetchone()

print("\n--- INVOICE STATISTICS ---")
print("Unique invoices:", invoice_stats[0])
print("Unique customers:", invoice_stats[1])
print("Unique countries:", invoice_stats[2])

connection.close()

# Inspect quantity and price ranges
connection = sqlite3.connect(DATABASE_FILE)
cursor = connection.cursor()

cursor.execute("""
SELECT
    MIN(Quantity),
    MAX(Quantity),
    AVG(Quantity),
    MIN(UnitPrice),
    MAX(UnitPrice),
    AVG(UnitPrice)
FROM online_retail;
""")

price_quantity_stats = cursor.fetchone()

print("\n--- QUANTITY AND PRICE STATISTICS ---")
print("Minimum quantity:", price_quantity_stats[0])
print("Maximum quantity:", price_quantity_stats[1])
print("Average quantity:", price_quantity_stats[2])
print("Minimum unit price:", price_quantity_stats[3])
print("Maximum unit price:", price_quantity_stats[4])
print("Average unit price:", price_quantity_stats[5])

connection.close()

# Inspect monthly transaction distribution
connection = sqlite3.connect(DATABASE_FILE)
cursor = connection.cursor()

cursor.execute("""
SELECT
    strftime('%Y-%m', InvoiceDate) AS month,
    COUNT(*) AS total_records,
    COUNT(DISTINCT InvoiceNo) AS unique_invoices
FROM online_retail
GROUP BY month
ORDER BY month;
""")

print("\n--- MONTHLY TRANSACTION DISTRIBUTION ---")

for row in cursor.fetchall():
    print(row)

connection.close()

# Inspect transaction types by month
connection = sqlite3.connect(DATABASE_FILE)
cursor = connection.cursor()

cursor.execute("""
SELECT
    strftime('%Y-%m', InvoiceDate) AS month,
    SUM(CASE WHEN InvoiceNo LIKE 'C%' THEN 1 ELSE 0 END) AS cancellations,
    SUM(CASE
        WHEN InvoiceNo NOT LIKE 'C%' AND Quantity < 0
        THEN 1 ELSE 0
    END) AS returns,
    SUM(CASE
        WHEN InvoiceNo NOT LIKE 'C%' AND Quantity > 0
        THEN 1 ELSE 0
    END) AS positive_quantity_records
FROM online_retail
GROUP BY month
ORDER BY month;
""")

print("\n--- MONTHLY TRANSACTION TYPES ---")

for row in cursor.fetchall():
    print(row)

connection.close()

# Verify monthly transaction classification
connection = sqlite3.connect(DATABASE_FILE)
cursor = connection.cursor()

cursor.execute("""
SELECT
    strftime('%Y-%m', InvoiceDate) AS month,
    COUNT(*) AS total_records,
    SUM(CASE WHEN InvoiceNo LIKE 'C%' THEN 1 ELSE 0 END)
    +
    SUM(CASE
        WHEN InvoiceNo NOT LIKE 'C%' AND Quantity < 0
        THEN 1 ELSE 0
    END)
    +
    SUM(CASE
        WHEN InvoiceNo NOT LIKE 'C%' AND Quantity > 0
        THEN 1 ELSE 0
    END) AS classified_records
FROM online_retail
GROUP BY month
ORDER BY month;
""")

print("\n--- MONTHLY CLASSIFICATION VALIDATION ---")

all_valid = True

for month, total, classified in cursor.fetchall():
    valid = total == classified
    print(month, "| Total:", total,
          "| Classified:", classified,
          "| Valid:", valid)

    if not valid:
        all_valid = False

print("\nAll monthly classifications valid:", all_valid)

connection.close()

# Inspect unclassified records
connection = sqlite3.connect(DATABASE_FILE)
cursor = connection.cursor()

cursor.execute("""
SELECT COUNT(*)
FROM online_retail
WHERE
    InvoiceNo IS NULL
    OR (
        InvoiceNo NOT LIKE 'C%'
        AND Quantity = 0
    );
""")

unclassified_count = cursor.fetchone()[0]

print("\n--- UNCLASSIFIED RECORD CHECK ---")
print("Unclassified records:", unclassified_count)

connection.close()