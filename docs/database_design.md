# NovaRetail Experimental Database Design

## 1. Purpose

NovaRetail is a fictional retail business database designed for evaluating natural-language database analysis using LLM-based systems.

The database will provide a controlled environment for testing SQL generation, multi-table queries, analytical reasoning, error detection, and recovery.

## 2. Database Tables

### Customers
- customer_id (Primary Key)
- customer_name
- city
- signup_date

### Products
- product_id (Primary Key)
- product_name
- category
- current_price
- stock_quantity

### Orders
- order_id (Primary Key)
- customer_id (Foreign Key referencing Customers)
- order_date
- status

### Order Items
- order_item_id (Primary Key)
- order_id (Foreign Key referencing Orders)
- product_id (Foreign Key referencing Products)
- quantity
- unit_price

## 3. Relationships

- One customer can place multiple orders.
- Each order belongs to one customer.
- One order can contain multiple order items.
- Each order item references one product.
- One product can appear in multiple order items.

## 4. Important Design Decisions

The unit_price field is stored in Order Items to preserve the historical purchase price.

The current_price field in Products represents the current listed price.

Historical revenue calculations must use:

Revenue = quantity × unit_price

This avoids incorrect historical calculations when product prices change.

## 5. Planned Database Technology

SQLite will be used as the relational database management system.

Foreign key constraints will be enabled to preserve referential integrity.

## 6. Planned Experimental Use

The database will support:
- Simple SELECT queries.
- Filtering and sorting.
- Aggregations.
- JOIN operations.
- Revenue analysis.
- Date-based analysis.
- Multi-condition analytical questions.
- SQL execution and semantic error testing.