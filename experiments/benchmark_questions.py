
benchmark_questions = [
    {
        "id": 1,
        "difficulty": "easy",
        "question": "How many customers are in the database?",
        "expected_sql": """
            SELECT COUNT(*) AS customer_count
            FROM customers;
        """
    },
    {
        "id": 2,
        "difficulty": "easy",
        "question": "List the names of all customers from Pune.",
        "expected_sql": """
            SELECT customer_name
            FROM customers
            WHERE city = 'Pune'
            ORDER BY customer_name;
        """
    },
    {
        "id": 3,
        "difficulty": "easy",
        "question": "How many products are in the Electronics category?",
        "expected_sql": """
            SELECT COUNT(*) AS product_count
            FROM products
            WHERE category = 'Electronics';
        """
    },
    {
        "id": 4,
        "difficulty": "medium",
        "question": "Show the number of orders for each order status.",
        "expected_sql": """
            SELECT status, COUNT(*) AS order_count
            FROM orders
            GROUP BY status
            ORDER BY status;
        """
    },
    {
        "id": 5,
        "difficulty": "medium",
        "question": "Show the total quantity ordered for each product, excluding cancelled orders, sorted from highest to lowest.",
        "expected_sql": """
            SELECT p.product_name,
                   SUM(oi.quantity) AS total_quantity_sold
            FROM products p
            JOIN order_items oi
                ON p.product_id = oi.product_id
            JOIN orders o
                ON oi.order_id = o.order_id
            WHERE o.status != 'Cancelled'
            GROUP BY p.product_id, p.product_name
            ORDER BY total_quantity_sold DESC;
        """,
        "ordering": [
            {"column_index": 1, "direction": "desc"}
        ]
    },
    {
        "id": 6,
        "difficulty": "easy",
        "question": "How many orders were placed in March 2025?",
        "expected_sql": """
            SELECT COUNT(*) AS order_count
            FROM orders
            WHERE order_date >= '2025-03-01'
              AND order_date < '2025-04-01';
        """
    },
    {
        "id": 7,
        "difficulty": "medium",
        "question": "List all customers from Mumbai who signed up during 2025.",
        "expected_sql": """
            SELECT customer_name
            FROM customers
            WHERE city = 'Mumbai'
              AND signup_date >= '2025-01-01'
              AND signup_date < '2026-01-01'
            ORDER BY customer_name;
        """
    },
    {
        "id": 8,
        "difficulty": "medium",
        "question": "Show the names of customers who have placed at least one Delivered order.",
        "expected_sql": """
            SELECT DISTINCT c.customer_name
            FROM customers c
            JOIN orders o
                ON c.customer_id = o.customer_id
            WHERE o.status = 'Delivered'
            ORDER BY c.customer_name;
        """
    },
    {
        "id": 9,
        "difficulty": "medium",
        "question": "Show the average current price of products in each category, in rupees.",
        "expected_sql": """
            SELECT category,
                   AVG(current_price_paise) / 100.0 AS average_price_rupees
            FROM products
            GROUP BY category
            ORDER BY category;
        """
    },
    {
        "id": 10,
        "difficulty": "medium",
        "question": "Find the five customers with the highest number of orders, excluding Cancelled orders. If customers have the same number of orders, rank them alphabetically by customer name.",
        "expected_sql": """
            SELECT c.customer_name,
                   COUNT(o.order_id) AS order_count
            FROM customers c
            JOIN orders o
                ON c.customer_id = o.customer_id
            WHERE o.status != 'Cancelled'
            GROUP BY c.customer_id, c.customer_name
            ORDER BY order_count DESC, c.customer_name ASC
            LIMIT 5;
        """,
        "ordering": [
            {"column_index": 1, "direction": "desc"},
            {"column_index": 0, "direction": "asc"}
        ]
    }
]
