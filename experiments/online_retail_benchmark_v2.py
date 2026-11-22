# Online Retail Benchmark v2
#
# Revenue definition (decided Day 39):
#   Gross revenue = SUM(Quantity * UnitPrice)
#   counting only rows where:
#     - InvoiceNo does not start with 'C' (not a cancellation)
#     - Quantity > 0
#     - UnitPrice > 0
#
# split = "test" means these questions were written AFTER the
# validator freeze. Never tune the validator using them.

online_retail_benchmark_v2 = [
    {
        "id": 11,
        "split": "test",
        "category": "revenue",
        "difficulty": "medium",
        "question": "What is the total gross revenue from normal sales, excluding cancellations, returns and zero-price rows?",
        "expected_sql": """
            SELECT ROUND(SUM(Quantity * UnitPrice), 2) AS gross_revenue
            FROM online_retail
            WHERE InvoiceNo NOT LIKE 'C%'
              AND Quantity > 0
              AND UnitPrice > 0;
        """,
        "expected_rows": [[10666684.54]],
        "verified_by": "Second formulation using SUM(CASE WHEN ...) gave the same result."
    },
    {
        "id": 12,
        "split": "test",
        "category": "revenue",
        "difficulty": "medium",
        "question": "Which 5 countries have the highest gross revenue? Exclude cancellations, returns and zero-price rows.",
        "expected_sql": """
        SELECT Country,
               ROUND(SUM(Quantity * UnitPrice), 2) AS gross_revenue
        FROM online_retail
        WHERE InvoiceNo NOT LIKE 'C%'
          AND Quantity > 0
          AND UnitPrice > 0
        GROUP BY Country
        ORDER BY gross_revenue DESC, Country ASC
        LIMIT 5;
    """,
        "expected_rows": [
            ["United Kingdom", 9025222.08],
            ["Netherlands", 285446.34],
            ["EIRE", 283453.96],
            ["Germany", 228867.14],
            ["France", 209715.11]
        ],
        "ordering": [
            {"column_index": 1, "direction": "desc"},
            {"column_index": 0, "direction": "asc"}
        ],
        "limit": 5,
        "verified_by": "Second formulation using SUM(CASE WHEN ...) gave the same top 5; 6th place (Australia, 138521.31) is not tied."
    },
]