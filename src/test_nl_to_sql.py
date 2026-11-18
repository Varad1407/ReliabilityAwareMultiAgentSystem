from nl_to_sql import generate_sql
from sql_executor import execute_sql

question = "Show the top 5 customers by total purchase value."

print("User question:")
print(question)

print("\nGenerating SQL using Qwen...")

sql_query = generate_sql(question)

print("\nGenerated SQL:")
print(sql_query)

print("\nExecuting SQL...")

result = execute_sql(sql_query)

if result["success"]:

    print("\nQuery results:")

    for row in result["rows"]:
        print(row)

else:

    print("\nSQL execution failed:")
    print(result["error_type"])
    print(result["error"])