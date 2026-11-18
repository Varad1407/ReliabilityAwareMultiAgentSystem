import json
from datetime import datetime, timezone
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR / "src"))

import agents.orchestrator as system_b_module
import agents.orchestrator_c as system_c_module

# Deliberately incorrect SQL for fault-injection testing
FAULTY_SQL = """
SELECT category,
       AVG(current_price_paise) AS average_price_rupees
FROM products
GROUP BY category
ORDER BY category
"""


# Force both systems to receive exactly the same SQL query
system_b_module.sql_agent = lambda user_question: FAULTY_SQL
system_c_module.sql_agent = lambda user_question: FAULTY_SQL

# Test question
question = "Show the average current price of products in each category, in rupees."


# Run System B
print("\nSYSTEM B — WITHOUT RECOVERY")
print("=" * 45)

result_b = system_b_module.orchestrate(question)

print("Success:", result_b["success"])
print("SQL:", result_b["sql_query"])
print("Error:", result_b.get("error"))


# Run System C
print("\nSYSTEM C — WITH RECOVERY")
print("=" * 45)

result_c = system_c_module.orchestrate_c(question)

print("Success:", result_c["success"])
print("SQL:", result_c["sql_query"])
print("Answer:", result_c.get("answer"))
print("Recovery attempts:", result_c["recovery_attempts"])
print("Error:", result_c.get("error"))

print("\nFAULT-INJECTION EXPERIMENT 4 SUMMARY")
print("=" * 45)

print("Fault type: Semantic error")
print("System B success:", result_b["success"])
print("System C success:", result_c["success"])
print("System C recovery attempts:", result_c["recovery_attempts"])

# Save fault-injection experiment results

results_dir = PROJECT_DIR / "results"
results_dir.mkdir(exist_ok=True)

experiment_data = {
    "experiment": "Fault Injection Experiment 4",
    "fault_type": "Semantic error",
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),

    "system_b": {
        "success": result_b["success"],
        "sql_query": result_b["sql_query"],
        "error": result_b.get("error")
    },

    "system_c": {
        "success": result_c["success"],
        "sql_query": result_c["sql_query"],
        "answer": result_c.get("answer"),
        "recovery_attempts": result_c["recovery_attempts"],
        "error": result_c.get("error")
    }
}

output_path = results_dir / "fault_injection_experiment_8_wrong_unit_conversion_recovery.json"

with open(output_path, "w", encoding="utf-8") as file:
    json.dump(experiment_data, file, indent=4, ensure_ascii=False)

print("\nExperiment results saved to:", output_path)