import sys
from pathlib import Path

# Locate the src folder
project_dir = Path(__file__).resolve().parent.parent
src_dir = project_dir / "src"

sys.path.insert(0, str(src_dir))

from sql_executor import execute_sql
from benchmark_questions import benchmark_questions


print("BENCHMARK QUERY VALIDATION")
print("=" * 50)

for item in benchmark_questions:

    print(f"\nQuestion {item['id']}: {item['question']}")

    result = execute_sql(item["expected_sql"])

    if result["success"]:
        print("Status: PASS")
        print("Columns:", result["columns"])
        print("Results:")

        for row in result["rows"]:
            print(row)

    else:
        print("Status: FAIL")
        print("Error:", result["error"])