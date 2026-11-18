
from llm_client import generate_response
from agents.result_formatter import format_query_results


def analysis_agent(user_question, query_results, columns):

    # Step 1: Handle empty results
    if not query_results:
        return "No matching data was found."

    # Step 2: Use Python for structured results
    if len(query_results) > 1 or len(columns) > 1:

        return format_query_results(
            columns,
            query_results
        )

    # Step 3: Use the LLM for simple answers
    prompt = f"""
You are a data analysis assistant.

Answer the user's question using only the database results provided.

USER QUESTION:
{user_question}

DATABASE RESULTS:
{query_results}

RULES:
1. Give a clear and simple answer.
2. Use only the information in the database results.
3. Do not invent numbers, names, or facts.
4. Preserve numerical values exactly as provided.

ANSWER:
"""

    answer = generate_response(prompt)

    return answer.strip()
