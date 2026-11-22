"""
Unified experiment runner for Systems A, B and C.

All three systems:
- receive the same benchmark questions,
- use the same LLM settings (model, temperature, seed per repetition),
- are scored by the same function (src/scoring.py).

The frozen system code is NOT modified. LLM calls are routed through a
wrapper defined here so that temperature/seed can be controlled and the
number of LLM calls and tokens can be recorded.

Examples:
    python experiments/run_experiment.py --system A
    python experiments/run_experiment.py --system C --reps 3 --temperature 0.3
    python experiments/run_experiment.py --system B --ids 11 12 --mock
"""

import argparse
import contextlib
import io
import json
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

project_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_dir / "src"))
sys.path.insert(0, str(project_dir / "experiments"))

import llm_client
import nl_to_sql
import agents.analysis_agent as analysis_agent_module
import agents.semantic_validation_agent_v2 as validator_module
import agents.orchestrator_c_v3 as c_v3_module
from nl_to_sql import (generate_sql, ONLINE_RETAIL_DATABASE_SCHEMA,
                       ONLINE_RETAIL_SCHEMA_WITH_DEFINITIONS)

SCHEMAS = {
    "base": ONLINE_RETAIL_DATABASE_SCHEMA,              # Experiment 1
    "definitions": ONLINE_RETAIL_SCHEMA_WITH_DEFINITIONS,  # Experiment 2
}
from sql_executor import execute_sql
from agents.orchestrator import orchestrate
from agents.orchestrator_c_v2 import orchestrate_c_v2
from agents.orchestrator_c_v3 import orchestrate_c_v3
from database import online_retail_database_path
from online_retail_benchmark_v2 import online_retail_benchmark_v2
from online_retail_benchmark_holdout import online_retail_benchmark_holdout

BENCHMARKS = {
    "v2": online_retail_benchmark_v2,            # design/dev questions 11-40
    "holdout": online_retail_benchmark_holdout,  # final test only, questions 41-60
}
from scoring import score


# --------------------------------------------------
# LLM wrapper: controls settings and counts usage
# --------------------------------------------------

class LLMTracker:
    def __init__(self, temperature, mock=False):
        self.temperature = temperature
        self.mock = mock
        self.seed = 42
        self.current_item = None
        self.reset()

    def reset(self):
        self.calls = 0
        self.prompt_tokens = 0
        self.output_tokens = 0

    def __call__(self, prompt, temperature=None, seed=None):
        self.calls += 1
        if self.mock:
            return self._mock_response(prompt)

        data = json.dumps({
            "model": llm_client.MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature if temperature is None else temperature,
                "seed": self.seed if seed is None else seed,
            },
        }).encode("utf-8")
        request = urllib.request.Request(
            llm_client.OLLAMA_URL, data=data,
            headers={"Content-Type": "application/json"}, method="POST",
        )
        with urllib.request.urlopen(request, timeout=300) as response:
            result = json.loads(response.read().decode("utf-8"))
        self.prompt_tokens += result.get("prompt_eval_count", 0) or 0
        self.output_tokens += result.get("eval_count", 0) or 0
        return result["response"]

    def _mock_response(self, prompt):
        # Test mode without Ollama: SQL prompts get the reference SQL,
        # validator prompts get VALID, everything else a fixed answer.
        if prompt.rstrip().endswith("SQL QUERY:"):
            return self.current_item["expected_sql"]
        if "INVALID" in prompt:
            return "VALID"
        return "Mock answer."


def install_tracker(tracker):
    for module in (llm_client, nl_to_sql, analysis_agent_module, validator_module, c_v3_module):
        module.generate_response = tracker


# --------------------------------------------------
# The three systems, called the same way
# --------------------------------------------------

def run_system(system, question, schema, seed=42):
    db = online_retail_database_path

    if system == "A":
        sql = generate_sql(question, schema)
        result = execute_sql(sql, db)
        return {"success": result["success"], "sql_query": sql,
                "rows": result.get("rows", []), "error": result.get("error"),
                    "agreement": result.get("agreement"),
                    "trace": result.get("trace"),
                "recovery_attempts": 0}

    if system == "B":
        result = orchestrate(question, db_path=db, database_schema=schema)
        result.setdefault("recovery_attempts", 0)
        return result

    if system == "C":
        return orchestrate_c_v2(question, db_path=db, database_schema=schema)

    if system == "C3":
        return orchestrate_c_v3(question, db_path=db, database_schema=schema, base_seed=seed)

    raise ValueError(f"Unknown system: {system}")


# --------------------------------------------------
# Main loop
# --------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--system", required=True, choices=["A", "B", "C", "C3"])
    parser.add_argument("--reps", type=int, default=1)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--base-seed", type=int, default=42)
    parser.add_argument("--ids", type=int, nargs="*", help="Only run these question IDs")
    parser.add_argument("--schema", choices=list(SCHEMAS), default="base",
                        help="base = Experiment 1, definitions = Experiment 2")
    parser.add_argument("--benchmark", choices=list(BENCHMARKS), default="v2")
    parser.add_argument("--mock", action="store_true", help="Test plumbing without Ollama")
    args = parser.parse_args()

    questions = [q for q in BENCHMARKS[args.benchmark]
                 if not args.ids or q["id"] in args.ids]

    tracker = LLMTracker(args.temperature, mock=args.mock)
    install_tracker(tracker)

    results_dir = project_dir / "results"
    results_dir.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    tag = "mock_" if args.mock else ""
    output_path = results_dir / f"experiment_{tag}{args.benchmark}_{args.schema}_system_{args.system}_{stamp}.json"
    log_path = results_dir / f"experiment_{tag}{args.benchmark}_{args.schema}_system_{args.system}_{stamp}.log"

    print(f"System {args.system} | {len(questions)} questions x {args.reps} reps | "
          f"temperature={args.temperature} | benchmark={args.benchmark} | schema={args.schema} | mock={args.mock}")

    records = []
    with open(log_path, "w", encoding="utf-8") as log:
        for rep in range(1, args.reps + 1):
            tracker.seed = args.base_seed + rep - 1
            for item in questions:
                tracker.current_item = item
                tracker.reset()
                captured = io.StringIO()
                start = time.perf_counter()
                try:
                    with contextlib.redirect_stdout(captured):
                        result = run_system(args.system, item["question"], SCHEMAS[args.schema], tracker.seed)
                except Exception as error:
                    result = {"success": False, "rows": [], "sql_query": None,
                              "error": f"{type(error).__name__}: {error}"}
                latency = time.perf_counter() - start
                log.write(f"\n=== rep {rep} Q{item['id']} ===\n{captured.getvalue()}")

                verdict = score(result.get("rows"), item) if result.get("success") else \
                    {"strict": False, "lenient": False, "matched_columns": None}

                record = {
                    "rep": rep, "seed": tracker.seed, "id": item["id"],
                    "category": item["category"], "difficulty": item["difficulty"],
                    "executed": bool(result.get("success")),
                    "correct_strict": verdict["strict"],
                    "correct_lenient": verdict["lenient"],
                    "latency_seconds": round(latency, 3),
                    "llm_calls": tracker.calls,
                    "prompt_tokens": tracker.prompt_tokens,
                    "output_tokens": tracker.output_tokens,
                    "recovery_attempts": result.get("recovery_attempts", 0),
                    "sql": result.get("sql_query"),
                    "rows": [list(r) for r in (result.get("rows") or [])][:20],
                    "error": result.get("error"),
                }
                records.append(record)
                mark = "OK " if record["correct_lenient"] else "BAD"
                print(f"rep {rep} Q{item['id']:>2} {mark} exec={record['executed']!s:5} "
                      f"strict={record['correct_strict']!s:5} {latency:6.2f}s "
                      f"calls={tracker.calls} recov={record['recovery_attempts']}")

    n = len(records)
    summary = {
        "system": args.system, "benchmark": args.benchmark, "schema": args.schema, "model": llm_client.MODEL_NAME,
        "temperature": args.temperature, "reps": args.reps,
        "seeds": [args.base_seed + r for r in range(args.reps)],
        "questions": len(questions), "evaluations": n, "mock": args.mock,
        "execution_rate": round(sum(r["executed"] for r in records) / n, 4),
        "accuracy_strict": round(sum(r["correct_strict"] for r in records) / n, 4),
        "accuracy_lenient": round(sum(r["correct_lenient"] for r in records) / n, 4),
        "avg_latency_seconds": round(sum(r["latency_seconds"] for r in records) / n, 3),
        "avg_llm_calls": round(sum(r["llm_calls"] for r in records) / n, 3),
        "avg_prompt_tokens": round(sum(r["prompt_tokens"] for r in records) / n, 1),
        "avg_output_tokens": round(sum(r["output_tokens"] for r in records) / n, 1),
    }
    output_path.write_text(json.dumps({"summary": summary, "records": records},
                                      indent=2, ensure_ascii=False), encoding="utf-8")

    print("\nSUMMARY")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    print(f"\nSaved: {output_path.relative_to(project_dir)}")


if __name__ == "__main__":
    main()
