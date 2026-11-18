
from agents.sql_agent import sql_agent
from agents.semantic_validation_agent_v2 import semantic_validation_agent_v2
from agents.error_detection_agent import error_detection_agent
from agents.analysis_agent import analysis_agent

from sql_executor import execute_sql
from nl_to_sql import DATABASE_SCHEMA, regenerate_sql, regenerate_sql_semantic


def orchestrate_c_v2(
    user_question,
    db_path=None,
    database_schema=DATABASE_SCHEMA
):
    max_recovery_attempts = 2
    recovery_attempts = 0

    print("\n--- SYSTEM C V2 ---")
    print("Question:", user_question)

    # Step 1: Generate initial SQL
    sql_query = sql_agent(
        user_question,
        database_schema
    )

    print("\nInitial SQL:")
    print(sql_query)

    while True:

        # Step 2: Execute SQL
        execution_result = execute_sql(
            sql_query,
            db_path
        )

        # Step 3: Detect execution errors
        error_result = error_detection_agent(
            execution_result
        )

        if error_result["has_error"]:

            if recovery_attempts >= max_recovery_attempts:
                return {
                    "success": False,
                    "error": "Maximum recovery attempts reached.",
                    "sql_query": sql_query,
                    "recovery_attempts": recovery_attempts
                }

            print("\nExecution error detected.")
            print("Attempting recovery...")

            corrected_sql = regenerate_sql(
                user_question,
                sql_query,
                error_result["error"],
                database_schema
            )

        else:

            # Step 4: Validate SQL semantics using V2
            semantic_result = semantic_validation_agent_v2(
                user_question,
                sql_query,
                execution_result["rows"],
                database_schema
            )

            print("\nSemantic validation:")
            print(semantic_result)

            if semantic_result["is_valid"]:
                break

            if recovery_attempts >= max_recovery_attempts:
                return {
                    "success": False,
                    "error": "Semantic validation failed after maximum recovery attempts.",
                    "sql_query": sql_query,
                    "validation_feedback": semantic_result.get("feedback"),
                    "recovery_attempts": recovery_attempts
                }

            print("\nSemantic error detected.")
            print("Attempting semantic recovery...")

            corrected_sql = regenerate_sql_semantic(
                user_question,
                sql_query,
                semantic_result.get("feedback", "SQL does not match the question."),
                database_schema
            )

        # Step 5: Prevent repeated identical SQL
        if corrected_sql.strip() == sql_query.strip():
            return {
                "success": False,
                "error": "Recovery failed: regenerated SQL is identical to previous SQL.",
                "sql_query": sql_query,
                "recovery_attempts": recovery_attempts
            }

        sql_query = corrected_sql
        recovery_attempts += 1

        print("\nCorrected SQL:")
        print(sql_query)

    # Step 6: Generate final natural-language answer
    analysis_result = analysis_agent(
        user_question,
        execution_result["rows"],
        execution_result["columns"]
    )

    return {
        "success": True,
        "sql_query": sql_query,
        "columns": execution_result["columns"],
        "rows": execution_result["rows"],
        "truncated": execution_result.get("truncated", False),
        "answer": analysis_result,
        "recovery_attempts": recovery_attempts,
        "semantic_validated": True
    }
