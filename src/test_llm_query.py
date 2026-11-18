import sys
from pathlib import Path

# Add src directory to Python path
project_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_dir / "src"))

from sql_executor import execute_sql


query = """
SELECT
    c.customer_name,
    SUM(oi.quantity * oi.unit_price_paise) / 100.0
        AS total_purchase_value_rupees
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
JOIN order_items oi
    ON o.order_id = oi.order_id
WHERE o.status = 'Delivered'
GROUP BY c.customer_id, c.customer_name
ORDER BY total_purchase_value_rupees DESC
LIMIT 5;
"""

result = execute_sql(query)

if result["success"]:
    print("\nTOP 5 CUSTOMERS BY PURCHASE VALUE")
    print("-" * 50)

    for row in result["rows"]:
        print(f"Customer: {row[0]}")
        print(f"Purchase value: ₹{row[1]:,.2f}")
        print("-" * 50)

else:
    print("SQL execution failed:")
    print(result["error"])