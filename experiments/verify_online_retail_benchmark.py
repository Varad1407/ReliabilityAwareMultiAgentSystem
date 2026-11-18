
from pathlib import Path
import sqlite3

from online_retail_benchmark import online_retail_benchmark


# Locate the project database
project_dir = Path(__file__).resolve().parent.parent
database_path = project_dir / "data" / "online_retail.db"

print("Database:", database_path)
print("=" * 70)

connection = sqlite3.connect(database_path)
cursor = connection.cursor()

passed = 0
failed = 0

for question in online_retail_benchmark:
    question_id = question["id"]

    try:
        cursor.execute(question["expected_sql"])
        actual_rows = [list(row) for row in cursor.fetchall()]
        expected_rows = question["expected_rows"]

        if actual_rows == expected_rows:
            print(f"Question {question_id}: PASS")
            passed += 1
        else:
            print(f"Question {question_id}: FAIL")
            print("Expected:", expected_rows)
            print("Actual:  ", actual_rows)
            failed += 1

    except Exception as error:
        print(f"Question {question_id}: ERROR")
        print(error)
        failed += 1

    print("-" * 70)

connection.close()

print("\nBENCHMARK VERIFICATION SUMMARY")
print(f"Passed: {passed}")
print(f"Failed: {failed}")
print(f"Total:  {passed + failed}")
