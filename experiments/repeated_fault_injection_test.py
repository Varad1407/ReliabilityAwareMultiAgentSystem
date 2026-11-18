
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from math import isclose

# --------------------------------------------------
# 1. PROJECT CONFIGURATION
# --------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR / "src"))

from benchmark_questions import benchmark_questions
from sql_executor import execute_sql

import agents.orchestrator as system_b_module
import agents.orchestrator_c as system_c_module


NUMBER_OF_TRIALS = 5

RESULTS_DIR = PROJECT_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)


# --------------------------------------------------
# 2. FAULT-INJECTION SCENARIOS
# --------------------------------------------------

SCENARIOS = [

    {
        "name": "Wrong database table",
        "question": "How many customers are in the database?",
        "faulty_sql": """
            SELECT COUNT(*) FROM products
        """
    },

    {
        "name": "Wrong date filter",
        "question": "How many orders were placed in March 2025?",
        "faulty_sql": """
            SELECT COUNT(*) FROM orders
            WHERE order_date >= '2025-04-01'
            AND order_date < '2025-05-01'
        """
    },

    {
        "name": "Wrong aggregation",
        "question": "Show the average current price of products in each category, in rupees.",
        "faulty_sql": """
            SELECT category,
                   SUM(current_price_paise) / 100.0
            FROM products
            GROUP BY category
            ORDER BY category
        """
    },

    {
        "name": "Missing unit conversion",
        "question": "Show the average current price of products in each category, in rupees.",
        "faulty_sql": """
            SELECT category,
                   AVG(current_price_paise)
            FROM products
            GROUP BY category
            ORDER BY category
        """
    }

]


# --------------------------------------------------
# 3. MATCH SCENARIOS WITH BENCHMARK QUESTIONS
# --------------------------------------------------

for scenario in SCENARIOS:

    matching_benchmark = None

    for benchmark in benchmark_questions:

        if scenario["question"] == benchmark["question"]:
            matching_benchmark = benchmark
            break

    if matching_benchmark is None:
        raise ValueError(
            f"No benchmark found for: {scenario['question']}"
        )

    scenario["benchmark"] = matching_benchmark


# --------------------------------------------------
# 4. INDEPENDENT RESULT COMPARISON
# --------------------------------------------------

def make_json_safe(value):

    if isinstance(value, dict):
        return {
            str(key): make_json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [make_json_safe(item) for item in value]

    return value


def values_match(actual, expected):

    if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
        return isclose(
            float(actual),
            float(expected),
            rel_tol=1e-6,
            abs_tol=1e-6
        )

    return actual == expected


def rows_match(actual_rows, expected_rows):

    if actual_rows is None:
        return False

    if len(actual_rows) != len(expected_rows):
        return False

    for actual_row, expected_row in zip(actual_rows, expected_rows):

        if len(actual_row) != len(expected_row):
            return False

        for actual_value, expected_value in zip(actual_row, expected_row):

            if not values_match(actual_value, expected_value):
                return False

    return True


def sql_semantically_correct(sql, scenario_name):
    if not sql:
        return False

    normalized_sql = " ".join(sql.lower().split())

    if scenario_name == "Wrong database table":
        return "from customers" in normalized_sql

    elif scenario_name == "Wrong date filter":
        return (
            "'2025-03-01'" in normalized_sql
            and "'2025-04-01'" in normalized_sql
            and "'2025-05-01'" not in normalized_sql
        )

    elif scenario_name == "Wrong aggregation":
        return (
            "avg(" in normalized_sql
            and "sum(" not in normalized_sql
        )

    elif scenario_name == "Missing unit conversion":
        return (
            "avg(" in normalized_sql
            and "/ 100" in normalized_sql
        )

    return False



# --------------------------------------------------
# 5. GENERATE INDEPENDENT EXPECTED RESULTS
# --------------------------------------------------

print("\nREPEATED FAULT-INJECTION EXPERIMENT")
print("=" * 60)

print("Trials per scenario:", NUMBER_OF_TRIALS)
print("Number of scenarios:", len(SCENARIOS))
print("Total planned trials:", len(SCENARIOS) * NUMBER_OF_TRIALS)

print("\nGENERATING EXPECTED RESULTS")
print("=" * 60)

for scenario in SCENARIOS:

    expected_result = execute_sql(
        scenario["benchmark"]["expected_sql"]
    )

    if not expected_result["success"]:
        raise RuntimeError(
            f"Reference SQL failed for {scenario['name']}: "
            f"{expected_result.get('error')}"
        )

    scenario["expected_rows"] = make_json_safe(
        expected_result["rows"]
    )

    scenario["expected_columns"] = make_json_safe(
        expected_result["columns"]
    )

    print("\nScenario:", scenario["name"])
    print("Benchmark ID:", scenario["benchmark"]["id"])
    print("Expected rows:", scenario["expected_rows"])


# --------------------------------------------------
# 6. STORE EXPERIMENT RESULTS
# --------------------------------------------------

all_results = []


# --------------------------------------------------
# 7. RUN REPEATED EXPERIMENTS
# --------------------------------------------------

for scenario in SCENARIOS:

    print("\n\n")
    print("#" * 60)
    print("SCENARIO:", scenario["name"])
    print("#" * 60)

    for trial_number in range(1, NUMBER_OF_TRIALS + 1):

        print("\nTRIAL", trial_number, "OF", NUMBER_OF_TRIALS)
        print("-" * 50)

        # Force both systems to receive identical faulty SQL.
        system_b_module.sql_agent = (
            lambda user_question, sql=scenario["faulty_sql"]: sql
        )

        system_c_module.sql_agent = (
            lambda user_question, sql=scenario["faulty_sql"]: sql
        )

        trial_result = {
            "scenario": scenario["name"],
            "benchmark_id": scenario["benchmark"]["id"],
            "trial": trial_number,
            "question": scenario["question"],
            "faulty_sql": scenario["faulty_sql"].strip(),
            "expected_rows": scenario["expected_rows"]
        }

        # ------------------------------------------
        # SYSTEM B: WITHOUT RECOVERY
        # ------------------------------------------

        print("\nSYSTEM B — WITHOUT RECOVERY")

        start_time = time.perf_counter()

        try:
            result_b = system_b_module.orchestrate(
                scenario["question"]
            )

            latency_b = time.perf_counter() - start_time

            actual_rows_b = result_b.get("rows")

            correct_b = (
                    result_b.get("success", False)
                    and rows_match(
                actual_rows_b,
                scenario["expected_rows"]
            )
                    and sql_semantically_correct(
                result_b.get("sql_query"),
                scenario["name"]
            )
            )

            trial_result["system_b"] = {
                "success": result_b.get("success", False),
                "latency_seconds": round(latency_b, 4),
                "sql_query": result_b.get("sql_query"),
                "rows": make_json_safe(actual_rows_b),
                "correct": correct_b,
                "error": result_b.get("error")
            }

            print("Success:", result_b.get("success"))
            print("Correct:", correct_b)
            print("Latency:", round(latency_b, 4), "seconds")

        except Exception as error:

            latency_b = time.perf_counter() - start_time

            trial_result["system_b"] = {
                "success": False,
                "latency_seconds": round(latency_b, 4),
                "correct": False,
                "error": str(error)
            }

            print("System B error:", error)

        # ------------------------------------------
        # SYSTEM C: WITH RECOVERY
        # ------------------------------------------

        print("\nSYSTEM C — WITH RECOVERY")

        start_time = time.perf_counter()

        try:
            result_c = system_c_module.orchestrate_c(
                scenario["question"]
            )

            latency_c = time.perf_counter() - start_time

            actual_rows_c = result_c.get("rows")

            correct_c = (
                    result_c.get("success", False)
                    and rows_match(
                actual_rows_c,
                scenario["expected_rows"]
            )
                    and sql_semantically_correct(
                result_c.get("sql_query"),
                scenario["name"]
            )
            )

            trial_result["system_c"] = {
                "success": result_c.get("success", False),
                "latency_seconds": round(latency_c, 4),
                "sql_query": result_c.get("sql_query"),
                "rows": make_json_safe(actual_rows_c),
                "correct": correct_c,
                "recovery_attempts": result_c.get(
                    "recovery_attempts", 0
                ),
                "semantic_validated": result_c.get(
                    "semantic_validated"
                ),
                "error": result_c.get("error")
            }

            print("Success:", result_c.get("success"))
            print("Correct:", correct_c)
            print("Latency:", round(latency_c, 4), "seconds")
            print(
                "Recovery attempts:",
                result_c.get("recovery_attempts", 0)
            )

        except Exception as error:

            latency_c = time.perf_counter() - start_time

            trial_result["system_c"] = {
                "success": False,
                "latency_seconds": round(latency_c, 4),
                "correct": False,
                "recovery_attempts": None,
                "error": str(error)
            }

            print("System C error:", error)

        all_results.append(trial_result)


# --------------------------------------------------
# 8. CALCULATE SUMMARY METRICS
# --------------------------------------------------

summary = {}

for scenario in SCENARIOS:

    scenario_trials = [
        result
        for result in all_results
        if result["scenario"] == scenario["name"]
    ]

    summary[scenario["name"]] = {}

    for system_name in ["system_b", "system_c"]:

        system_trials = [
            trial[system_name]
            for trial in scenario_trials
        ]

        successful_trials = sum(
            1 for trial in system_trials
            if trial.get("success", False)
        )

        correct_trials = sum(
            1 for trial in system_trials
            if trial.get("correct", False)
        )

        latencies = [
            trial["latency_seconds"]
            for trial in system_trials
            if "latency_seconds" in trial
        ]

        average_latency = (
            sum(latencies) / len(latencies)
            if latencies else None
        )

        system_summary = {
            "total_trials": len(system_trials),
            "successful_trials": successful_trials,
            "correct_trials": correct_trials,
            "success_rate": (
                successful_trials / len(system_trials)
                if system_trials else 0
            ),
            "correctness_rate": (
                correct_trials / len(system_trials)
                if system_trials else 0
            ),
            "average_latency_seconds": (
                round(average_latency, 4)
                if average_latency is not None else None
            )
        }

        if system_name == "system_c":

            recovery_counts = [
                trial["recovery_attempts"]
                for trial in system_trials
                if isinstance(trial.get("recovery_attempts"), int)
            ]

            system_summary["total_recovery_attempts"] = sum(
                recovery_counts
            )

            system_summary["average_recovery_attempts"] = (
                round(
                    sum(recovery_counts) / len(recovery_counts),
                    2
                )
                if recovery_counts else None
            )

        summary[scenario["name"]][system_name] = system_summary


# --------------------------------------------------
# 9. SAVE RESULTS WITHOUT OVERWRITING OLD FILES
# --------------------------------------------------

timestamp = datetime.now(timezone.utc).strftime(
    "%Y%m%d_%H%M%S"
)

output_path = (
    RESULTS_DIR
    / f"repeated_fault_injection_{timestamp}.json"
)

experiment_data = {
    "experiment": "Day 23 - Repeated Fault Injection",
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "trials_per_scenario": NUMBER_OF_TRIALS,
    "number_of_scenarios": len(SCENARIOS),
    "total_trials": len(all_results),
    "summary": summary,
    "individual_results": all_results
}

# Exclusive creation prevents accidental overwriting.
with open(output_path, "x", encoding="utf-8") as file:
    json.dump(
        experiment_data,
        file,
        indent=4,
        ensure_ascii=False
    )


# --------------------------------------------------
# 10. PRINT FINAL SUMMARY
# --------------------------------------------------

print("\n\n")
print("=" * 60)
print("REPEATED FAULT-INJECTION EXPERIMENT SUMMARY")
print("=" * 60)

for scenario_name, systems in summary.items():

    print("\nSCENARIO:", scenario_name)

    for system_name, metrics in systems.items():

        print("\n", system_name.upper())
        print("Successful trials:", metrics["successful_trials"])
        print("Correct trials:", metrics["correct_trials"])
        print(
            "Correctness rate:",
            round(metrics["correctness_rate"] * 100, 2),
            "%"
        )
        print(
            "Average latency:",
            metrics["average_latency_seconds"],
            "seconds"
        )

        if system_name == "system_c":
            print(
                "Total recovery attempts:",
                metrics["total_recovery_attempts"]
            )


print("\n" + "=" * 60)
print("EXPERIMENT COMPLETED")
print("Total trials recorded:", len(all_results))
print("Results saved to:", output_path)
print("=" * 60)
