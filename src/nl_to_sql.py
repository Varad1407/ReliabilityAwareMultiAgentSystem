
from llm_client import generate_response


# ==================================================
# 1. NOVARETAIL DATABASE SCHEMA
# ==================================================

DATABASE_SCHEMA = """
Database: NovaRetail

Table: customers
Columns:
- customer_id (INTEGER, Primary Key)
- customer_name (TEXT)
- city (TEXT)
- signup_date (TEXT)

Table: products
Columns:
- product_id (INTEGER, Primary Key)
- product_name (TEXT)
- category (TEXT)
- current_price_paise (INTEGER)
- stock_quantity (INTEGER)

Table: orders
Columns:
- order_id (INTEGER, Primary Key)
- customer_id (INTEGER, Foreign Key -> customers.customer_id)
- order_date (TEXT)
- status (TEXT: Pending, Processing, Shipped, Delivered, Cancelled)

Table: order_items
Columns:
- order_item_id (INTEGER, Primary Key)
- order_id (INTEGER, Foreign Key -> orders.order_id)
- product_id (INTEGER, Foreign Key -> products.product_id)
- quantity (INTEGER)
- unit_price_paise (INTEGER)

Relationships:
- customers.customer_id = orders.customer_id
- orders.order_id = order_items.order_id
- products.product_id = order_items.product_id

Important:
- All prices are stored in paise, not rupees.
- Convert paise to rupees by dividing by 100.0.
- Historical purchase prices are stored in order_items.unit_price_paise.
- Current product prices are stored in products.current_price_paise.
"""


# ==================================================
# 2. ONLINE RETAIL DATABASE SCHEMA
# ==================================================

ONLINE_RETAIL_DATABASE_SCHEMA = """
Database: UCI Online Retail

Table: online_retail

Columns:
- InvoiceNo (TEXT)
- StockCode (TEXT)
- Description (TEXT, nullable)
- Quantity (INTEGER)
- InvoiceDate (DATETIME)
- UnitPrice (REAL)
- CustomerID (REAL, nullable)
- Country (TEXT)

Important dataset information:

1. This table contains transaction-level records from
   the UCI Online Retail dataset.

2. InvoiceNo identifies an invoice.
   Different rows can belong to the same invoice.

3. StockCode identifies a product code.

4. CustomerID can contain NULL values.
   Do not assume every record has a customer identifier.

5. UnitPrice is already expressed in the dataset's
   currency units (pounds sterling).
   Do not divide UnitPrice by 100.

6. Quantity can be positive or negative.

7. Cancellation records are identified by:
   InvoiceNo LIKE 'C%'

8. Non-cancellation return records are identified by:
   InvoiceNo NOT LIKE 'C%' AND Quantity < 0

9. Positive-quantity records are identified by:
   InvoiceNo NOT LIKE 'C%' AND Quantity > 0

10. For a simple record count, use COUNT(*).

11. To count distinct invoices, use:
    COUNT(DISTINCT InvoiceNo)

12. To count distinct products, use:
    COUNT(DISTINCT StockCode)

13. Record counts, invoice counts, customer counts,
    and quantities are different measurements.

14. Do not automatically treat positive-quantity records
    as confirmed completed sales.

15. InvoiceDate can be filtered using SQLite date
    comparisons and the strftime() function.
"""



# ==================================================
# 2b. ONLINE RETAIL SCHEMA WITH BUSINESS DEFINITIONS
# ==================================================
# Added Day 39 for Experiment 2 ("semantic layer" condition).
# The original ONLINE_RETAIL_DATABASE_SCHEMA above is unchanged so that
# Experiment 1 remains reproducible. All three systems receive the same text.

ONLINE_RETAIL_SCHEMA_WITH_DEFINITIONS = ONLINE_RETAIL_DATABASE_SCHEMA + """
Business definitions (use these unless the question explicitly says otherwise):

16. A "normal sale" record is a record where:
    InvoiceNo NOT LIKE 'C%' AND Quantity > 0 AND UnitPrice > 0

17. "Gross revenue" (also "revenue" or "sales") is:
    SUM(Quantity * UnitPrice) over normal-sale records only.

18. "Net revenue" is SUM(Quantity * UnitPrice) over all records,
    including cancellations, returns and adjustments.

19. A "purchase" means a normal sale.

20. "Customers" means distinct non-NULL CustomerID values.
"""

# ==================================================
# 3. SQL GENERATION
# ==================================================

def generate_sql(user_question, database_schema=DATABASE_SCHEMA):

    prompt = f"""
You are an expert SQLite query generator.

Your task is to convert the user's question into
a valid SQLite SELECT query.

Use only the database schema provided below.

DATABASE SCHEMA:
{database_schema}

RULES:
1. Generate only SQLite-compatible SQL.
2. Use only the tables and columns in the provided schema.
3. Use JOINs only when the schema supports them.
4. Understand the database-specific units and data semantics.
5. Do not assume that record counts and distinct invoice counts
   are the same.
6. Do not generate INSERT, UPDATE, DELETE, DROP or CREATE statements.
7. Return only the SQL query.
8. Do not include explanations or Markdown code blocks.

USER QUESTION:
{user_question}

SQL QUERY:
"""

    sql_query = generate_response(prompt)

    return sql_query.strip()


# ==================================================
# 4. SQL EXECUTION ERROR RECOVERY
# ==================================================

def regenerate_sql(
    user_question,
    failed_sql,
    error_message,
    database_schema=DATABASE_SCHEMA
):

    prompt = f"""
You are an expert SQLite query correction assistant.

Your task is to correct an SQL query that failed during execution.

DATABASE SCHEMA:
{database_schema}

ORIGINAL USER QUESTION:
{user_question}

FAILED SQL QUERY:
{failed_sql}

DATABASE ERROR:
{error_message}

RULES:
1. Correct the SQL query based on the database error.
2. Answer the original user question.
3. Use only the tables and columns in the provided schema.
4. Generate valid SQLite SELECT SQL only.
5. Respect the units and data semantics of the selected database.
6. Do not generate INSERT, UPDATE, DELETE, DROP or CREATE statements.
7. Return only the corrected SQL query.
8. Do not include explanations or Markdown code blocks.

CORRECTED SQL QUERY:
"""

    corrected_sql = generate_response(prompt)

    return corrected_sql.strip()


# ==================================================
# 5. SEMANTIC ERROR RECOVERY
# ==================================================

def regenerate_sql_semantic(
    user_question,
    failed_sql,
    semantic_feedback,
    database_schema=DATABASE_SCHEMA
):

    prompt = f"""
You are an expert SQLite query correction assistant.

Your task is to correct an SQL query that executes successfully
but does not correctly answer the user's original question.

DATABASE SCHEMA:
{database_schema}

ORIGINAL USER QUESTION:
{user_question}

INCORRECT SQL QUERY:
{failed_sql}

SEMANTIC VALIDATION FEEDBACK:
{semantic_feedback}

RULES:
1. Correct the SQL query using the semantic feedback.
2. Make sure the query answers the original user question.
3. Use only tables and columns from the provided schema.
4. Respect the units and data semantics of the selected database.
5. Generate valid SQLite SELECT SQL only.
6. Do not generate INSERT, UPDATE, DELETE, DROP or CREATE statements.
7. Return only the corrected SQL query.
8. Do not include explanations or Markdown code blocks.

CORRECTED SQL QUERY:
"""

    corrected_sql = generate_response(prompt)

    return corrected_sql.strip()


# ==================================================
# 6. BASIC SCHEMA CONFIGURATION TEST
# ==================================================

if __name__ == "__main__":

    print("NovaRetail schema loaded:")
    print("Database: NovaRetail")
    print("Default schema:", DATABASE_SCHEMA[:100], "...")

    print("\nOnline Retail schema loaded:")
    print("Database: UCI Online Retail")
    print("External schema:", ONLINE_RETAIL_DATABASE_SCHEMA[:100], "...")

    print("\nNL-to-SQL configuration loaded successfully.")
