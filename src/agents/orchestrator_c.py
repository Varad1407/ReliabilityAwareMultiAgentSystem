
from agents.sql_agent import sql_agent
from agents.analysis_agent import analysis_agent
from agents.error_detection_agent import error_detection_agent
from agents.semantic_validation_agent import semantic_validation_agent

from sql_executor import execute_sql

from nl_to_sql import (
    DATABASE_SCHEMA,
    ONLINE_RETAIL_DATABASE_SCHEMA,
    regenerate_sql,
    regenerate_sql_semantic
)

from database import online_retail_database_path


def orchestrate_c(
    user_question,
    db_path=None,
    database_schema=DATABASE_SCHEMA
):

    max_recovery_attempts = 2
    recovery_attempts = 0

    # Step 1: Generate initial SQL using selected schema
    sql_query = sql_agent(
        user_question,
        database_schema
    )

    while True:

        # Step 2: Execute SQL against selected database
        execution_result = execute_sql(
            sql_query,
            db_path=db_path
        )

        # Step 3: Check for SQL execution errors
        detection_result = error_detection_agent(execution_result)

        if detection_result["has_error"]:

            # Stop if recovery limit is reached
            if recovery_attempts >= max_recovery_attempts:
                return {
                    "success": False,
                    "sql_query": sql_query,
                    "error_type": execution_result["error_type"],
                    "error": detection_result["error"],
                    "recovery_attempts": recovery_attempts
                }

            # Correct SQL execution error
            corrected_sql = regenerate_sql(
                user_question,
                sql_query,
                detection_result["error"],
                database_schema
            )

        else:

            # Step 4: Check semantic correctness
            semantic_result = semantic_validation_agent(
                user_question,
                sql_query,
                execution_result["rows"],
                database_schema
            )

            # Stop if semantic validation passes
            if semantic_result["is_valid"]:
                break

            # Stop if recovery limit is reached
            if recovery_attempts >= max_recovery_attempts:
                return {
                    "success": False,
                    "sql_query": sql_query,
                    "error_type": "SEMANTIC_VALIDATION_ERROR",
                    "error": semantic_result["feedback"],
                    "recovery_attempts": recovery_attempts
                }

            # Correct semantic error
            corrected_sql = regenerate_sql_semantic(
                user_question,
                sql_query,
                semantic_result["feedback"],
                database_schema
            )

        # Step 5: Avoid repeating the same SQL query
        if corrected_sql.strip() == sql_query.strip():
            return {
                "success": False,
                "sql_query": sql_query,
                "error_type": "RECOVERY_FAILED",
                "error": "The correction generated the same SQL query.",
                "recovery_attempts": recovery_attempts
            }

        # Step 6: Update SQL and recovery counter
        sql_query = corrected_sql
        recovery_attempts += 1

    # Step 7: Generate final natural-language answer
    query_results = execution_result["rows"]
    columns = execution_result["columns"]

    final_answer = analysis_agent(
        user_question,
        query_results,
        columns
    )

    # Step 8: Return the result
    return {
        "success": True,
        "sql_query": sql_query,
        "columns": columns,
        "rows": query_results,
        "truncated": execution_result["truncated"],
        "answer": final_answer,
        "recovery_attempts": recovery_attempts,
        "semantic_validated": True
    }


if __name__ == "__main__":

    # ==============================================
    # TEST 1: NOVARETAIL (DEFAULT)
    # ==============================================

    question = (
        "Find the five customers with the highest number "
        "of orders, excluding Cancelled orders. "
        "If customers have the same number of orders, "
        "rank them alphabetically by customer name."
    )

    result = orchestrate_c(question)


    # ==============================================
    # TEST 2: ONLINE RETAIL
    # ==============================================

    online_question = "How many distinct invoices are in the dataset?"

    online_result = orchestrate_c(
        online_question,
        db_path=online_retail_database_path,
        database_schema=ONLINE_RETAIL_DATABASE_SCHEMA
    )

    print("\nSYSTEM C - ONLINE RETAIL TEST")
    print("=" * 45)
    print("Success:", online_result["success"])
    print("Final SQL:", online_result["sql_query"])
    print("Rows:", online_result.get("rows"))
    print("Answer:", online_result.get("answer"))
    print("Recovery attempts:", online_result["recovery_attempts"])
    print("Semantic validated:", online_result.get("semantic_validated"))
    print("Error:", online_result.get("error"))


    print("\nSYSTEM C - NOVARETAIL TEST")
    print("=" * 45)
    print("Success:", result["success"])
    print("Final SQL:", result["sql_query"])
    print("Answer:", result.get("answer"))
    print("Recovery attempts:", result["recovery_attempts"])
    print("Semantic validated:", result.get("semantic_validated"))
    print("Error:", result.get("error"))

    # ==============================================
    # ONLINE RETAIL USAGE EXAMPLE
    # ==============================================

    # To use Online Retail, call:
    #
    # online_result = orchestrate_c(
    #     "How many distinct invoices are in the dataset?",
    #     db_path=online_retail_database_path,
    #     database_schema=ONLINE_RETAIL_DATABASE_SCHEMA
    # )
    #
    # print(online_result)
