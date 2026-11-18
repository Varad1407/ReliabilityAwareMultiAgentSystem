
from nl_to_sql import generate_sql, DATABASE_SCHEMA


def sql_agent(user_question, database_schema=DATABASE_SCHEMA):
    """
    Receives a natural-language question and generates
    an SQL query using the selected database schema.
    """

    sql_query = generate_sql(
        user_question,
        database_schema
    )

    return sql_query
