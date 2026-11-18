
from agents.sql_agent import sql_agent
from agents.analysis_agent import analysis_agent
from sql_executor import execute_sql
from nl_to_sql import DATABASE_SCHEMA, ONLINE_RETAIL_DATABASE_SCHEMA
from database import online_retail_database_path


def orchestrate(
    user_question,
    db_path=None,
    database_schema=DATABASE_SCHEMA
):
    """
    Coordinates the SQL Agent and Analysis Agent.

    1. Generates SQL using the selected database schema.
    2. Executes SQL against the selected database.
    3. Sends results to the Analysis Agent.
    4. Returns the final answer.

    System B does not perform autonomous error recovery.
    """

    # Step 1: Generate SQL
    sql_query = sql_agent(user_question, database_schema)

    # Step 2: Execute SQL against the selected database
    execution_result = execute_sql(sql_query, db_path=db_path)

    # Step 3: Handle execution errors
    if not execution_result["success"]:
        return {
            "success": False,
            "sql_query": sql_query,
            "error_type": execution_result["error_type"],
            "error": execution_result["error"]
        }

    # Step 4: Send database results to Analysis Agent
    query_results = execution_result["rows"]
    columns = execution_result["columns"]

    final_answer = analysis_agent(
        user_question,
        query_results,
        columns
    )

    # Step 5: Return the complete result
    return {
        "success": True,
        "sql_query": sql_query,
        "columns": columns,
        "rows": query_results,
        "truncated": execution_result["truncated"],
        "answer": final_answer
    }


if __name__ == "__main__":

    # Test System B with Online Retail
    print("\nSYSTEM B - ONLINE RETAIL TEST")
    print("=" * 50)

    result = orchestrate(
        "How many distinct invoices are recorded in the dataset?",
        db_path=online_retail_database_path,
        database_schema=ONLINE_RETAIL_DATABASE_SCHEMA
    )

    print("Success:", result["success"])
    print("SQL:", result["sql_query"])

    if result["success"]:
        print("Rows:", result["rows"])
        print("Answer:", result["answer"])
    else:
        print("Error:", result["error"])

    # Test System B with NovaRetail
    print("\nSYSTEM B - NOVARETAIL TEST")
    print("=" * 50)

    result = orchestrate(
        "How many customers are in the database?"
    )

    print("Success:", result["success"])
    print("SQL:", result["sql_query"])

    if result["success"]:
        print("Rows:", result["rows"])
        print("Answer:", result["answer"])
    else:
        print("Error:", result["error"])
