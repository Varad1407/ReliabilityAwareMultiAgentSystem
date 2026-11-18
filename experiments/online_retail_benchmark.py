online_retail_benchmark = [
    {
        "id": 1,
        "difficulty": "easy",
        "question": "How many distinct invoices are recorded in the Online Retail dataset?",
        "expected_sql": """
            SELECT COUNT(DISTINCT InvoiceNo) AS invoice_count
            FROM online_retail;
        """,
        "expected_rows": [[25900]]
    },
    {
        "id": 2,
        "difficulty": "easy",
        "question": "How many distinct countries are represented in the Online Retail dataset?",
        "expected_sql": """
            SELECT COUNT(DISTINCT Country) AS country_count
            FROM online_retail;
        """,
        "expected_rows": [[38]]
    },
    {
        "id": 3,
        "difficulty": "easy",
        "question": "How many records have a missing CustomerID?",
        "expected_sql": """
            SELECT COUNT(*) AS missing_customer_count
            FROM online_retail
            WHERE CustomerID IS NULL;
        """,
        "expected_rows": [[135080]]
    },
    {
        "id": 4,
        "difficulty": "easy",
        "question": "How many records belong to cancellation invoices?",
        "expected_sql": """
            SELECT COUNT(*) AS cancellation_records
            FROM online_retail
            WHERE InvoiceNo LIKE 'C%';
        """,
        "expected_rows": [[9288]]
    },
    {
        "id": 5,
        "difficulty": "medium",
        "question": "How many non-cancellation records have a negative quantity?",
        "expected_sql": """
            SELECT COUNT(*) AS return_records
            FROM online_retail
            WHERE InvoiceNo NOT LIKE 'C%'
              AND Quantity < 0;
        """,
        "expected_rows": [[1336]]
    },
    {
        "id": 6,
        "difficulty": "medium",
        "question": "Show the five countries with the highest number of records, sorted from highest to lowest record count. If two countries have the same count, sort alphabetically by country.",
        "expected_sql": """
            SELECT Country, COUNT(*) AS record_count
            FROM online_retail
            GROUP BY Country
            ORDER BY record_count DESC, Country ASC
            LIMIT 5;
        """,
        "expected_rows": [
            ["United Kingdom", 495478],
            ["Germany", 9495],
            ["France", 8557],
            ["EIRE", 8196],
            ["Spain", 2533]
        ],
        "ordering": [
            {"column_index": 1, "direction": "desc"},
            {"column_index": 0, "direction": "asc"}
        ],
        "limit": 5
    },
    {
        "id": 7,
        "difficulty": "medium",
        "question": "How many records were recorded in November 2011?",
        "expected_sql": """
            SELECT COUNT(*) AS record_count
            FROM online_retail
            WHERE InvoiceDate >= '2011-11-01'
              AND InvoiceDate < '2011-12-01';
        """,
        "expected_rows": [[84711]]
    },
    {
        "id": 8,
        "difficulty": "medium",
        "question": "Show the number of positive-quantity records, non-cancellation returns, and cancellation records.",
        "expected_sql": """
            SELECT
                CASE
                    WHEN InvoiceNo LIKE 'C%' THEN 'Cancellation'
                    WHEN Quantity < 0 THEN 'Return'
                    WHEN Quantity > 0 THEN 'Positive quantity'
                END AS transaction_type,
                COUNT(*) AS record_count
            FROM online_retail
            GROUP BY transaction_type
            ORDER BY transaction_type;
        """,
        "expected_rows": [
            ["Cancellation", 9288],
            ["Positive quantity", 531285],
            ["Return", 1336]
        ]
    },
    {
        "id": 9,
        "difficulty": "hard",
        "question": "Which month had the highest number of records, and how many records were recorded in that month?",
        "expected_sql": """
            SELECT
                strftime('%Y-%m', InvoiceDate) AS month,
                COUNT(*) AS record_count
            FROM online_retail
            GROUP BY month
            ORDER BY record_count DESC, month ASC
            LIMIT 1;
        """,
        "expected_rows": [
            ["2011-11", 84711]
        ],
        "ordering": [
            {"column_index": 1, "direction": "desc"},
            {"column_index": 0, "direction": "asc"}
        ]
    },
    {
        "id": 10,
        "difficulty": "hard",
        "question": "How many distinct product codes are present in the dataset?",
        "expected_sql": """
            SELECT COUNT(DISTINCT StockCode) AS product_count
            FROM online_retail;
        """,
        "expected_rows": [[4070]]
    }
]