
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
SRC_DIR = PROJECT_DIR / "src"

sys.path.insert(0, str(PROJECT_DIR))
sys.path.insert(0, str(SRC_DIR))

from online_retail_benchmark import online_retail_benchmark
from sql_executor import execute_sql
from database import online_retail_database_path
from nl_to_sql import ONLINE_RETAIL_DATABASE_SCHEMA

import agents.orchestrator as system_b_module
import agents.orchestrator_c_v2 as system_c_module


NUMBER_OF_TRIALS = 20

RESULTS_DIR = PROJECT_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)


# --------------------------------------------------
# 2. FAULT-INJECTION SCENARIOS
# --------------------------------------------------

SCENARIOS = [

    {
        "name": "Incorrect NULL handling",
        "question": "How many records have a missing CustomerID?",
        "faulty_sql": """
            SELECT COUNT(*)
            FROM online_retail
            WHERE CustomerID = NULL
        """,
        "benchmark": {
            "id": "D29-Q1",
            "expected_sql": """
                SELECT COUNT(*)
                FROM online_retail
                WHERE CustomerID IS NULL
            """
        }
    },

    {
        "name": "Counting records instead of distinct invoices",
        "question": "How many distinct invoices are recorded in the dataset?",
        "faulty_sql": """
            SELECT COUNT(*)
            FROM online_retail
        """,
        "benchmark": {
            "id": "D29-Q2",
            "expected_sql": """
                SELECT COUNT(DISTINCT InvoiceNo)
                FROM online_retail
            """
        }
    },

    {
        "name": "Incorrect monthly grouping",
        "question": "Show the number of records for each month in 2011.",
        "faulty_sql": """
            SELECT strftime('%Y', InvoiceDate) AS year,
                   COUNT(*) AS record_count
            FROM online_retail
            WHERE InvoiceDate >= '2011-01-01'
              AND InvoiceDate < '2012-01-01'
            GROUP BY year
            ORDER BY year
        """,
        "benchmark": {
            "id": "D29-Q3",
            "expected_sql": """
                SELECT strftime('%Y-%m', InvoiceDate) AS month,
                       COUNT(*) AS record_count
                FROM online_retail
                WHERE InvoiceDate >= '2011-01-01'
                  AND InvoiceDate < '2012-01-01'
                GROUP BY month
                ORDER BY month
            """
        }
    },

    {
        "name": "Counting records instead of distinct products",
        "question": "How many distinct product codes are present in the dataset?",
        "faulty_sql": """
            SELECT COUNT(*)
            FROM online_retail
        """,
        "benchmark": {
            "id": "D29-Q4",
            "expected_sql": """
                SELECT COUNT(DISTINCT StockCode)
                FROM online_retail
            """
        }
    }

]


# --------------------------------------------------
# 3. MATCH SCENARIOS WITH BENCHMARK QUESTIONS
# --------------------------------------------------

for scenario in SCENARIOS:

    # Use the custom reference benchmark supplied for Day 29.
    if (
        "benchmark" in scenario
        and "expected_sql" in scenario["benchmark"]
    ):
        continue

    # Otherwise, search the original benchmark.
    matching_benchmark = None

    for benchmark in online_retail_benchmark:

        if scenario["question"] == benchmark["question"]:
            matching_benchmark = benchmark
            break

    if matching_benchmark is None:
        raise ValueError(
            f"No benchmark found for: {scenario['question']}"
        )

    scenario["benchmark"] = matching_benchmark


# --------------------------------------------------
# 4. RESULT COMPARISON FUNCTIONS
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


# --------------------------------------------------
# 5. SCENARIO-SPECIFIC SQL CHECKS
# --------------------------------------------------

def sql_semantically_correct(sql, scenario_name):

    if not sql:
        return False

    normalized_sql = " ".join(sql.lower().split())

    if scenario_name == "Incorrect NULL handling":

        return "customerid is null" in normalized_sql

    elif scenario_name == "Counting records instead of distinct invoices":

        return "count(distinct invoiceno)" in normalized_sql


    elif scenario_name == "Incorrect monthly grouping":

        return (

                "strftime('%Y-%m'" in sql

                and "group by" in normalized_sql

                and "2011-01-01" in normalized_sql

                and "2012-01-01" in normalized_sql

        )


    elif scenario_name == "Counting records instead of distinct products":

        return "count(distinct stockcode)" in normalized_sql

    return False


# --------------------------------------------------
# 6. GENERATE INDEPENDENT EXPECTED RESULTS
# --------------------------------------------------

print("\nREPEATED ONLINE RETAIL FAULT-INJECTION EXPERIMENT")
print("=" * 65)

print("Trials per scenario:", NUMBER_OF_TRIALS)
print("Number of scenarios:", len(SCENARIOS))
print("Total planned trials:", len(SCENARIOS) * NUMBER_OF_TRIALS)

print("\nGENERATING INDEPENDENT EXPECTED RESULTS")
print("=" * 65)

for scenario in SCENARIOS:

    expected_result = execute_sql(
        scenario["benchmark"]["expected_sql"],
        db_path=online_retail_database_path
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
# 7. RUN THE EXPERIMENT
# --------------------------------------------------

all_results = []

for scenario in SCENARIOS:

    print("\n\n")
    print("#" * 65)
    print("SCENARIO:", scenario["name"])
    print("#" * 65)

    for trial_number in range(1, NUMBER_OF_TRIALS + 1):

        print("\nTRIAL", trial_number, "OF", NUMBER_OF_TRIALS)
        print("-" * 50)

        # Give both systems the same faulty initial SQL.
        # *args and **kwargs allow the updated orchestrators
        # to pass database_schema without breaking the monkeypatch.

        system_b_module.sql_agent = (
            lambda user_question, *args,
            sql=scenario["faulty_sql"], **kwargs: sql
        )

        system_c_module.sql_agent = (
            lambda user_question, *args,
            sql=scenario["faulty_sql"], **kwargs: sql
        )

        trial_result = {
            "scenario": scenario["name"],
            "benchmark_id": scenario["benchmark"]["id"],
            "trial": trial_number,
            "question": scenario["question"],
            "faulty_sql": scenario["faulty_sql"].strip(),
            "expected_rows": scenario["expected_rows"],
            "expected_columns": scenario["expected_columns"]
        }

        # ------------------------------------------
        # SYSTEM B — WITHOUT RECOVERY
        # ------------------------------------------

        print("\nSYSTEM B — WITHOUT RECOVERY")

        start_time = time.perf_counter()

        try:

            result_b = system_b_module.orchestrate(
                scenario["question"],
                db_path=online_retail_database_path,
                database_schema=ONLINE_RETAIL_DATABASE_SCHEMA
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
        # SYSTEM C — WITH RECOVERY
        # ------------------------------------------

        print("\nSYSTEM C — WITH RECOVERY")

        start_time = time.perf_counter()

        try:

            result_c = system_c_module.orchestrate_c_v2(
                scenario["question"],
                db_path=online_retail_database_path,
                database_schema=ONLINE_RETAIL_DATABASE_SCHEMA
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

            recovery_attempts = result_c.get(
                "recovery_attempts", 0
            )

            trial_result["system_c"] = {
                "success": result_c.get("success", False),
                "latency_seconds": round(latency_c, 4),
                "sql_query": result_c.get("sql_query"),
                "rows": make_json_safe(actual_rows_c),
                "correct": correct_c,
                "recovery_attempts": recovery_attempts,
                "semantic_validated": result_c.get(
                    "semantic_validated",
                    result_c.get("semantic_validation_used")
                ),
                "error": result_c.get("error")
            }

            print("Success:", result_c.get("success"))
            print("Correct:", correct_c)
            print("Latency:", round(latency_c, 4), "seconds")
            print("Recovery attempts:", recovery_attempts)

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
            "execution_success_rate": (
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
# 9. SAVE RESULTS WITHOUT OVERWRITING
# --------------------------------------------------

timestamp = datetime.now(timezone.utc).strftime(
    "%Y%m%d_%H%M%S"
)

output_path = (
    RESULTS_DIR
    / f"repeated_online_retail_fault_injection_{timestamp}.json"
)

experiment_data = {
    "experiment": "Day 27 - Online Retail Repeated Fault Injection",
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "dataset": "UCI Online Retail",
    "trials_per_scenario": NUMBER_OF_TRIALS,
    "number_of_scenarios": len(SCENARIOS),
    "total_trials": len(all_results),
    "summary": summary,
    "individual_results": all_results
}

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
print("=" * 65)
print("ONLINE RETAIL FAULT-INJECTION EXPERIMENT SUMMARY")
print("=" * 65)

for scenario_name, systems in summary.items():

    print("\nSCENARIO:", scenario_name)

    for system_name, metrics in systems.items():

        print("\n", system_name.upper())
        print("Successful trials:", metrics["successful_trials"])
        print("Correct trials:", metrics["correct_trials"])

        print(
            "Execution success rate:",
            round(metrics["execution_success_rate"] * 100, 2),
            "%"
        )

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


print("\n" + "=" * 65)
print("EXPERIMENT COMPLETED")
print("Total trials recorded:", len(all_results))
print("Results saved to:", output_path)
print("=" * 65)
