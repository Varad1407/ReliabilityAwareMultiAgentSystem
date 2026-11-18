
import re
import calendar

from llm_client import generate_response
from nl_to_sql import DATABASE_SCHEMA


# ==================================================
# 1. HELPER FUNCTIONS
# ==================================================

def invalid_result(feedback):
    return {
        "is_valid": False,
        "feedback": feedback
    }


def valid_result():
    return {
        "is_valid": True,
        "feedback": None
    }


def normalize_sql(sql_query):
    """
    Normalize SQL for easier pattern checking.
    """
    return re.sub(r"\s+", " ", sql_query.upper()).strip()


# ==================================================
# 2. DETERMINISTIC AGGREGATION VALIDATION
# ==================================================






def validate_aggregation(question, sql):

    question_lower = question.lower()
    sql_upper = sql.upper()

    uses_sum = bool(re.search(r"\bSUM\s*\(", sql_upper))
    uses_avg = bool(re.search(r"\bAVG\s*\(", sql_upper))

    if (
        "average" in question_lower
        and uses_sum
        and not uses_avg
    ):
        return (
            "The question requests an average, "
            "but the SQL uses SUM instead of AVG."
        )

    if (
        "total quantity" in question_lower
        and uses_avg
        and not uses_sum
    ):
        return (
            "The question requests total quantity, "
            "but the SQL uses AVG instead of SUM."
        )

    # Check distinct invoice counts.
    asks_distinct_invoices = (
        "distinct invoice" in question_lower
        or "unique invoice" in question_lower
    )

    if asks_distinct_invoices:

        # Formulation 1: COUNT(DISTINCT InvoiceNo)
        uses_distinct_invoice_count = bool(
            re.search(
                r"\bCOUNT\s*\(\s*DISTINCT\s+InvoiceNo\s*\)",
                sql,
                re.IGNORECASE
            )
        )

        # Formulation 2: COUNT(*) over a CTE
        # that selects DISTINCT InvoiceNo.
        has_distinct_invoice_cte = bool(
            re.search(
                r"\bWITH\s+\w+\s+AS\s*\(\s*"
                r"SELECT\s+DISTINCT\s+InvoiceNo\b",
                sql,
                re.IGNORECASE | re.DOTALL
            )
        )

        counts_from_invoice_cte = bool(
            re.search(
                r"\)\s*SELECT\s+COUNT\s*\(\s*\*\s*\)"
                r"\s+FROM\s+\w+",
                sql,
                re.IGNORECASE | re.DOTALL
            )
        )

        uses_distinct_invoice_cte = (
            has_distinct_invoice_cte and counts_from_invoice_cte
        )

        if not (
            uses_distinct_invoice_count
            or uses_distinct_invoice_cte
        ):
            return (
                "The question requests the number of "
                "distinct invoices, but the SQL does not "
                "use a recognized distinct invoice count."
            )

    # Check distinct customer counts.
    asks_distinct_customers = (
        "distinct customer" in question_lower
        or "unique customer" in question_lower
    )

    if asks_distinct_customers:

        # Formulation 1: COUNT(DISTINCT CustomerID)
        uses_distinct_customer_count = bool(
            re.search(
                r"\bCOUNT\s*\(\s*DISTINCT\s+CustomerID\s*\)",
                sql,
                re.IGNORECASE
            )
        )

        # Formulation 2: COUNT(*) over a DISTINCT subquery.
        uses_distinct_customer_subquery = bool(
            re.search(
                r"\bCOUNT\s*\(\s*\*\s*\)\s*"
                r"FROM\s*\(\s*SELECT\s+DISTINCT\s+CustomerID\b",
                sql,
                re.IGNORECASE | re.DOTALL
            )
        )

        # Formulation 3: COUNT(*) over a DISTINCT CTE.
        has_distinct_customer_cte = bool(
            re.search(
                r"\bWITH\s+\w+\s+AS\s*\(\s*"
                r"SELECT\s+DISTINCT\s+CustomerID\b",
                sql,
                re.IGNORECASE | re.DOTALL
            )
        )

        counts_from_cte = bool(
            re.search(
                r"\)\s*SELECT\s+COUNT\s*\(\s*\*\s*\)"
                r"\s+FROM\s+\w+",
                sql,
                re.IGNORECASE | re.DOTALL
            )
        )

        uses_distinct_customer_cte = (
            has_distinct_customer_cte and counts_from_cte
        )

        # Formulation 4: COUNT(*) over a GROUP BY subquery.
        uses_grouped_customer_subquery = bool(
            re.search(
                r"\bCOUNT\s*\(\s*\*\s*\)\s*"
                r"FROM\s*\(\s*SELECT\s+CustomerID\b"
                r"[\s\S]*?\bGROUP\s+BY\s+CustomerID\b"
                r"[\s\S]*?\)",
                sql,
                re.IGNORECASE
            )
        )

        if not (
            uses_distinct_customer_count
            or uses_distinct_customer_subquery
            or uses_distinct_customer_cte
            or uses_grouped_customer_subquery
        ):
            return (
                "The question requests the number of "
                "distinct customers, but the SQL does not "
                "use a recognized distinct customer count."
            )

    return None







# ==================================================
# 3. DATABASE-SPECIFIC UNIT VALIDATION
# ==================================================


def validate_price_units(question, sql, database_schema):

    question_lower = question.lower()
    schema_upper = database_schema.upper()
    sql_upper = sql.upper()

    stores_prices_in_paise = (
        "CURRENT_PRICE_PAISE" in schema_upper
        or "UNIT_PRICE_PAISE" in schema_upper
    )

    if not stores_prices_in_paise:
        return None

    uses_paise_column = (
        "CURRENT_PRICE_PAISE" in sql_upper
        or "UNIT_PRICE_PAISE" in sql_upper
    )

    # Recognize division by 100 or 100.0,
    # while preventing /1000 from being accepted.
    division_conversion = bool(
        re.search(
            r"/\s*100(?:\.0+)?(?![\d.])",
            sql_upper
        )
    )

    # Recognize multiplication by 0.01.
    multiplication_conversion = bool(
        re.search(
            r"\*\s*0?\.01(?![\d.])",
            sql_upper
        )
    )

    has_conversion = (
        division_conversion or multiplication_conversion
    )

    if (
        "rupees" in question_lower
        and uses_paise_column
        and not has_conversion
    ):
        return (
            "The question requests prices in rupees, "
            "but the SQL does not contain a recognized "
            "paise-to-rupees conversion. "
            "Use division by 100 or multiplication by 0.01."
        )

    return None



# ==================================================
# 4. DATE FILTER VALIDATION
# ==================================================





def validate_date_filter(question, sql):

    question_lower = question.lower()

    months = {
        "january": 1,
        "february": 2,
        "march": 3,
        "april": 4,
        "may": 5,
        "june": 6,
        "july": 7,
        "august": 8,
        "september": 9,
        "october": 10,
        "november": 11,
        "december": 12
    }

    month_pattern = (
        r"\b("
        + "|".join(months.keys())
        + r")\s+(20\d{2})\b"
    )

    match = re.search(month_pattern, question_lower)

    if not match:
        return None

    month_name = match.group(1)
    year = int(match.group(2))
    month = months[month_name]

    start_date = f"{year}-{month:02d}-01"

    if month == 12:
        next_month_date = f"{year + 1}-01-01"
    else:
        next_month_date = f"{year}-{month + 1:02d}-01"

    last_day = calendar.monthrange(year, month)[1]
    last_date = f"{year}-{month:02d}-{last_day:02d}"

    # Method 1: STRFTIME('%Y-%m', InvoiceDate) = 'YYYY-MM'
    strftime_year_month = bool(
        re.search(
            rf"STRFTIME\s*\(\s*['\"]%Y-%m['\"]\s*,[^)]*\)"
            rf"\s*=\s*['\"]{year}-{month:02d}['\"]",
            sql,
            re.IGNORECASE
        )
    )

    if strftime_year_month:
        return None

    # Method 2: SUBSTR(InvoiceDate, 1, 7) = 'YYYY-MM'
    substr_year_month = bool(
        re.search(
            rf"SUBSTR\s*\(\s*InvoiceDate\s*,\s*1\s*,\s*7\s*\)"
            rf"\s*=\s*['\"]{year}-{month:02d}['\"]",
            sql,
            re.IGNORECASE
        )
    )

    if substr_year_month:
        return None


    # Method 3: Separate STRFTIME year and month extraction.
    # Supports both direct comparisons and CAST(... AS INTEGER).

    strftime_year = bool(
        re.search(
            rf"STRFTIME\s*\(\s*['\"]%Y['\"]\s*,[^)]*\)"
            rf"\s*(?:AS\s+\w+\s*)?\)?"
            rf"\s*=\s*['\"]?{year}['\"]?",
            sql,
            re.IGNORECASE
        )
    )

    strftime_month = bool(
        re.search(
            rf"STRFTIME\s*\(\s*['\"]%m['\"]\s*,[^)]*\)"
            rf"\s*(?:AS\s+\w+\s*)?\)?"
            rf"\s*=\s*['\"]?{month:02d}['\"]?",
            sql,
            re.IGNORECASE
        )
    )

    if strftime_year and strftime_month:
        return None


    # Method 4: Inclusive BETWEEN date boundaries
    has_valid_between = bool(
        re.search(
            rf"\bBETWEEN\s*['\"]{re.escape(start_date)}['\"]"
            rf"\s+AND\s+['\"]{re.escape(last_date)}['\"]",
            sql,
            re.IGNORECASE
        )
    )

    if has_valid_between:
        return None

    # Method 5: Separate date boundaries
    has_valid_start = bool(
        re.search(
            rf">=\s*['\"]{re.escape(start_date)}['\"]",
            sql,
            re.IGNORECASE
        )
    )

    has_valid_end = (
        bool(
            re.search(
                rf"<\s*['\"]{re.escape(next_month_date)}['\"]",
                sql,
                re.IGNORECASE
            )
        )
        or bool(
            re.search(
                rf"<=\s*['\"]{re.escape(last_date)}['\"]",
                sql,
                re.IGNORECASE
            )
        )
    )

    if not has_valid_start or not has_valid_end:
        return (
            f"The question requests {month_name} {year}, "
            f"but the SQL does not contain valid date boundaries "
            f"({start_date} inclusive to {next_month_date} exclusive). "
            f"Check the date filter and comparison operators."
        )

    return None






# ==================================================
# 5. CANCELLATION AND RETURN VALIDATION
# ==================================================


def validate_transaction_filters(
    question,
    sql,
    database_schema
):

    question_lower = question.lower()
    schema_upper = database_schema.upper()

    # Apply these checks only to Online Retail databases.
    is_online_retail = (
        "INVOICENO" in schema_upper
        and "CANCELLATION RECORDS" in schema_upper
    )

    if not is_online_retail:
        return None

    asks_for_non_cancellations = (
        "non-cancellation" in question_lower
        or "non cancellation" in question_lower
        or "excluding cancellations" in question_lower
        or "exclude cancellations" in question_lower
        or "excluding cancellation" in question_lower
        or "excluding cancelled invoices" in question_lower
        or "excluding canceled invoices" in question_lower
        or "exclude cancelled invoices" in question_lower
        or "exclude canceled invoices" in question_lower
        or "excluding cancelled invoice" in question_lower
        or "excluding canceled invoice" in question_lower
        or "exclude cancelled invoice" in question_lower
        or "exclude canceled invoice" in question_lower
    )

    if not asks_for_non_cancellations:
        return None

    # Method 1: InvoiceNo NOT LIKE 'C%'
    excludes_with_not_like = bool(
        re.search(
            r"(?:\w+\.)?INVOICENO\s+NOT\s+LIKE\s+['\"]C%['\"]",
            sql,
            re.IGNORECASE
        )
    )

    # Method 2: NOT (InvoiceNo LIKE 'C%')
    excludes_with_not = bool(
        re.search(
            r"NOT\s*\(\s*(?:\w+\.)?INVOICENO\s+LIKE\s+['\"]C%['\"]\s*\)",
            sql,
            re.IGNORECASE
        )
    )

    # Method 3: SUBSTR(InvoiceNo, 1, 1) <> 'C'
    excludes_with_substr = bool(
        re.search(
            r"SUBSTR\s*\(\s*(?:\w+\.)?INVOICENO\s*,\s*1\s*,\s*1\s*\)\s*(?:<>|!=)\s*['\"]C['\"]",
            sql,
            re.IGNORECASE
        )
    )

    # Method 4: InvoiceNo NOT GLOB 'C*'
    excludes_with_not_glob = bool(
        re.search(
            r"(?:\w+\.)?INVOICENO\s+NOT\s+GLOB\s+['\"]C\*['\"]",
            sql,
            re.IGNORECASE
        )
    )

    # Method 5: NOT EXISTS with a matching cancellation invoice.
    excludes_with_not_exists = bool(
        re.search(
            r"\bNOT\s+EXISTS\s*\("
            r"\s*SELECT\b"
            r"[\s\S]*?\bWHERE\b"
            r"[\s\S]*?\b(?:\w+\.)?INVOICENO\s*=\s*(?:\w+\.)?INVOICENO"
            r"[\s\S]*?\bAND\b"
            r"[\s\S]*?\b(?:\w+\.)?INVOICENO\s+GLOB\s*['\"]C\*['\"]",
            sql,
            re.IGNORECASE
        )
    )

    if not (
        excludes_with_not_like
        or excludes_with_not
        or excludes_with_substr
        or excludes_with_not_glob
        or excludes_with_not_exists
    ):
        return (
            "The question explicitly excludes cancellation "
            "records, but the SQL does not exclude invoices "
            "whose InvoiceNo starts with C."
        )

    return None





# ==================================================
# 6. SORTING AND LIMIT VALIDATION
# ==================================================


def validate_sorting(question, sql):

    question_lower = question.lower()

    asks_highest = any(
        phrase in question_lower
        for phrase in [
            "highest",
            "most",
            "largest",
            "top"
        ]
    )

    asks_lowest = any(
        phrase in question_lower
        for phrase in [
            "lowest",
            "least",
            "smallest",
            "bottom"
        ]
    )

    if not asks_highest and not asks_lowest:
        return None

    order_match = re.search(
        r"\bORDER\s+BY\b(.*?)(?:\bLIMIT\b|$)",
        sql,
        re.IGNORECASE
    )

    if not order_match:
        return (
            "The question requests a ranking, "
            "but the SQL does not contain ORDER BY."
        )

    order_clause = order_match.group(1)

    if asks_highest and not asks_lowest:
        if not re.search(r"\bDESC\b", order_clause, re.IGNORECASE):
            return (
                "The question requests the highest values, "
                "but the SQL does not sort the results "
                "in descending order."
            )

    if asks_lowest and not asks_highest:
        if not re.search(r"\bASC\b", order_clause, re.IGNORECASE):
            return (
                "The question requests the lowest values, "
                "but the SQL does not sort the results "
                "in ascending order."
            )

    asks_alphabetical_tiebreak = (
        "alphabetically" in question_lower
        or "alphabetical" in question_lower
    )

    if asks_alphabetical_tiebreak:
        has_alphabetical_order = bool(
            re.search(
                r"\b(COUNTRY|CUSTOMER_NAME|PRODUCT_NAME)\s+ASC\b",
                order_clause,
                re.IGNORECASE
            )
        )

        if not has_alphabetical_order:
            return (
                "The question requests alphabetical "
                "tie-breaking, but the SQL does not "
                "include the relevant text column "
                "in ascending order."
            )

    # Detect explicit top-N or bottom-N requests.
    number_words = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10
    }

    limit_match = re.search(
        r"\b(?:top|bottom)\s+(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\b",
        question_lower
    )

    if limit_match:
        requested_number = limit_match.group(1)

        expected_limit = (
            int(requested_number)
            if requested_number.isdigit()
            else number_words[requested_number]
        )

        sql_limit = re.search(
            r"\bLIMIT\s+(\d+)\b",
            sql,
            re.IGNORECASE
        )

        if not sql_limit:
            return (
                f"The question requests {expected_limit} results, "
                "but the SQL does not contain the required LIMIT."
            )

        actual_limit = int(sql_limit.group(1))

        if actual_limit != expected_limit:
            return (
                f"The question requests {expected_limit} "
                f"results, but the SQL uses LIMIT {actual_limit}."
            )

    return None



# ==================================================
# 7. HYBRID SEMANTIC VALIDATION AGENT
# ==================================================

def semantic_validation_agent_v2(
    user_question,
    sql_query,
    query_results,
    database_schema=DATABASE_SCHEMA
):

    sql = normalize_sql(sql_query)

    # ----------------------------------------------
    # CHECK 1: Aggregation
    # ----------------------------------------------

    feedback = validate_aggregation(
        user_question,
        sql
    )

    if feedback:
        return invalid_result(feedback)

    # ----------------------------------------------
    # CHECK 2: Price units
    # ----------------------------------------------

    feedback = validate_price_units(
        user_question,
        sql,
        database_schema
    )

    if feedback:
        return invalid_result(feedback)

    # ----------------------------------------------
    # CHECK 3: Date filters
    # ----------------------------------------------

    feedback = validate_date_filter(
        user_question,
        sql
    )

    if feedback:
        return invalid_result(feedback)

    # ----------------------------------------------
    # CHECK 4: Cancellation and return semantics
    # ----------------------------------------------

    feedback = validate_transaction_filters(
        user_question,
        sql,
        database_schema
    )

    if feedback:
        return invalid_result(feedback)

    # ----------------------------------------------
    # CHECK 5: Sorting and ranking
    # ----------------------------------------------

    feedback = validate_sorting(
        user_question,
        sql
    )

    if feedback:
        return invalid_result(feedback)

    # ----------------------------------------------
    # CHECK 6: LLM semantic validation
    # ----------------------------------------------

    prompt = f"""
You are a strict semantic SQL validation assistant.

Determine whether the SQL query correctly answers
the original user question.

DATABASE SCHEMA:
{database_schema}

USER QUESTION:
{user_question}

GENERATED SQL:
{sql_query}

DATABASE RESULTS:
{query_results}

VALIDATION REQUIREMENTS:

1. Understand exactly what information the user requested.

2. Check whether the correct tables and columns are used.

3. Check whether COUNT, SUM, AVG and other aggregations
   match the meaning of the question.

4. Check mathematical calculations and units using
   the provided database schema.

5. Check all filters, including dates, categories,
   statuses and transaction conditions.

6. Check GROUP BY and JOIN conditions.

7. Check ORDER BY direction and LIMIT.

8. Distinguish between records, distinct invoices,
   distinct customers and quantities.

9. Do not assume that a query is correct simply because
   it executes successfully or returns plausible values.

10. If any important part of the query does not match
    the original question, mark it INVALID.

RESPONSE FORMAT:

If correct, respond with exactly:
VALID

If incorrect, respond with:
INVALID: followed by a short explanation.

Do not generate corrected SQL.
Do not include introductory text.
"""

    response = generate_response(prompt).strip()

    response_upper = response.upper()

    if response_upper == "VALID":
        return valid_result()

    if response_upper.startswith("INVALID"):
        feedback = response[len("INVALID"):].strip(" :-\n")

        return invalid_result(feedback)

    return invalid_result(
        "The semantic validator returned an unclear response."
    )


# ==================================================
# 8. BASIC CONFIGURATION TEST
# ==================================================

if __name__ == "__main__":

    from nl_to_sql import ONLINE_RETAIL_DATABASE_SCHEMA

    print("Testing Semantic Validation Agent V2")
    print("=" * 50)

    print("\nNovaRetail schema loaded:")
    print("Paise-based price validation:",
          "CURRENT_PRICE_PAISE" in DATABASE_SCHEMA.upper())

    print("\nOnline Retail schema loaded:")
    print("Cancellation validation enabled:",
          "CANCELLATION RECORDS" in ONLINE_RETAIL_DATABASE_SCHEMA.upper())

    print("\nSemantic Validation Agent V2 loaded successfully.")
