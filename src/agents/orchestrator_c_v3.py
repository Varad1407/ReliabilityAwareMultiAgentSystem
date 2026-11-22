"""
System C v3 — reliability-focused error detection and recovery.

Designed on Day 39 using ONLY the benchmark v2 questions (IDs 11-40), after
analysing why System C v2 failed in Experiments 1 and 2:
  - v2 keyword rules caused false rejections ("at least" -> ranking),
  - v2 recovery stopped as soon as the regenerated SQL was identical,
  - v2 almost never corrected a wrong query.

v3 design:
  1. Self-consistency: generate several SQL candidates, execute all of them
     and prefer the result that most candidates agree on.
  2. Result-based checks (no keyword rules): execution error, empty result,
     and "many rows returned for a single-value question".
  3. LLM judge that sees the question, SQL AND a preview of the result.
  4. Recovery with variation: if a repair returns the same SQL or the same
     result, retry at a higher temperature with a different seed.
  5. Abstain only when checks still fail after recovery AND the candidates
     disagree; a unanimous result is kept even if the judge objects.
"""

import re

from llm_client import generate_response
from nl_to_sql import DATABASE_SCHEMA, generate_sql
from sql_executor import execute_sql
from agents.analysis_agent import analysis_agent

NUM_CANDIDATES = 3
CANDIDATE_TEMPERATURE = 0.8
REPAIR_TEMPERATURE = 0.8
MAX_REPAIRS = 3
SEED_OFFSET = 1000
PREVIEW_ROWS = 10

SINGLE_VALUE_QUESTION = re.compile(
    r"^\s*(how many|how much|what (is|was|are|were) the (total|average|number|percentage|share)"
    r"|what percentage|by what percentage)\b",
    re.IGNORECASE,
)


# --------------------------------------------------
# Helpers
# --------------------------------------------------

def clean_sql(text):
    """Remove Markdown fences or a leading 'sql' label from LLM output."""
    text = text.strip()
    fence = re.search(r"```(?:sql)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if fence:
        text = fence.group(1).strip()
    if text.lower().startswith("sql\n"):
        text = text[4:]
    return text.strip()


def result_key(rows):
    """A hashable, rounding-tolerant fingerprint of a result set (order kept)."""
    def norm(v):
        if isinstance(v, float):
            return round(v, 2)
        return v
    return tuple(tuple(norm(v) for v in row) for row in rows)


def preview(rows):
    shown = [list(r) for r in rows[:PREVIEW_ROWS]]
    more = f" ... ({len(rows)} rows in total)" if len(rows) > PREVIEW_ROWS else ""
    return f"{shown}{more}"


def deterministic_check(question, execution):
    """Return None if OK, otherwise a short problem description."""
    if not execution["success"]:
        return f"The query failed to execute: {execution['error']}"
    rows = execution["rows"]
    if not rows:
        return "The query returned no rows."
    if all(v is None for row in rows for v in row):
        return "The query returned only NULL values."
    if SINGLE_VALUE_QUESTION.search(question) and len(rows) > 1:
        return (f"The question asks for a single value, but the query returned "
                f"{len(rows)} rows. A GROUP BY may be producing one row per group; "
                f"aggregate over the groups (for example with a subquery) instead.")
    return None


def llm_judge(question, sql, execution, database_schema, seed):
    prompt = f"""
You are a strict reviewer of SQLite queries for a data analysis system.

Decide whether the SQL query correctly answers the user's question,
using the schema and its business definitions.

DATABASE SCHEMA:
{database_schema}

USER QUESTION:
{question}

SQL QUERY:
{sql}

RESULT PREVIEW:
{preview(execution['rows'])}

Check: correct filters (business definitions, NULL handling, dates),
correct aggregation, correct grouping, requested columns, ordering and limit.

Reply with exactly one line:
VALID
or
INVALID: <one-sentence reason>
"""
    response = generate_response(prompt, temperature=0.0, seed=seed).strip()
    first = response.splitlines()[0].strip() if response else ""
    if first.upper().startswith("VALID"):
        return None
    if first.upper().startswith("INVALID"):
        return first[len("INVALID"):].strip(" :-") or "The reviewer judged the query incorrect."
    return None  # unclear reviewer output is not treated as an error


def repair_sql(question, sql, execution, problem, database_schema, temperature, seed, previous):
    tried = "\n\n".join(previous[-3:])
    rows_text = preview(execution["rows"]) if execution.get("success") else "(no result)"
    prompt = f"""
You are an expert SQLite query correction assistant.

DATABASE SCHEMA:
{database_schema}

USER QUESTION:
{question}

PREVIOUS SQL QUERY:
{sql}

ITS RESULT:
{rows_text}

PROBLEM FOUND:
{problem}

QUERIES ALREADY TRIED (do not repeat them exactly):
{tried}

RULES:
1. Write a corrected SQLite SELECT query that answers the question.
2. Follow the business definitions in the schema.
3. Return only the SQL query, without explanations or Markdown.

CORRECTED SQL QUERY:
"""
    return clean_sql(generate_response(prompt, temperature=temperature, seed=seed))


# --------------------------------------------------
# Main orchestrator
# --------------------------------------------------

def orchestrate_c_v3(user_question, db_path=None, database_schema=DATABASE_SCHEMA, base_seed=42):
    trace = []

    # 1. Generate candidates. Candidate 0 uses the default generation settings
    #    (identical to System A); the others are sampled with more variation.
    candidates = []
    for i in range(NUM_CANDIDATES):
        if i == 0:
            sql = clean_sql(generate_sql(user_question, database_schema))
        else:
            sql = clean_sql(_generate_varied(user_question, database_schema,
                                             CANDIDATE_TEMPERATURE, base_seed + SEED_OFFSET + i))
        execution = execute_sql(sql, db_path)
        problem = deterministic_check(user_question, execution)
        candidates.append({"sql": sql, "execution": execution, "problem": problem})
        trace.append(f"candidate {i}: problem={problem}")

    # 2. Vote among candidates that pass the deterministic checks.
    passing = [c for c in candidates if c["problem"] is None]
    votes = {}
    for c in passing:
        votes.setdefault(result_key(c["execution"]["rows"]), []).append(c)

    if votes:
        best_group = max(votes.values(), key=lambda g: (len(g), g[0] is candidates[0]))
        chosen = best_group[0]
        agreement = len(best_group)
    else:
        chosen = candidates[0]
        agreement = 0
    unanimous = agreement == NUM_CANDIDATES
    trace.append(f"agreement={agreement}/{NUM_CANDIDATES}")

    # 3. Check the chosen candidate (deterministic + LLM judge), repair if needed.
    sql, execution = chosen["sql"], chosen["execution"]
    problem = chosen["problem"] or llm_judge(user_question, sql, execution, database_schema, base_seed)
    tried = [c["sql"] for c in candidates]
    repairs = 0

    while problem and repairs < MAX_REPAIRS:
        if unanimous and chosen["problem"] is None and repairs == 0:
            # All candidates agree and pass result checks: trust consistency
            # over a single judge objection.
            trace.append(f"judge objection overruled by unanimous candidates: {problem}")
            problem = None
            break

        repairs += 1
        new_sql = repair_sql(user_question, sql, execution, problem, database_schema,
                             REPAIR_TEMPERATURE, base_seed + 2 * SEED_OFFSET + repairs, tried)
        new_exec = execute_sql(new_sql, db_path)
        tried.append(new_sql)

        same_sql = new_sql.strip() == sql.strip()
        same_result = (new_exec["success"] and execution.get("success")
                       and result_key(new_exec["rows"]) == result_key(execution["rows"]))
        trace.append(f"repair {repairs}: same_sql={same_sql} same_result={same_result}")
        if same_sql or same_result:
            continue  # try again with a new seed instead of giving up

        new_problem = deterministic_check(user_question, new_exec)
        if new_problem is None:
            new_problem = llm_judge(user_question, new_sql, new_exec, database_schema,
                                    base_seed + repairs)
        sql, execution, problem = new_sql, new_exec, new_problem
        trace.append(f"repair {repairs} problem={problem}")

    # 4. Decide: answer or abstain.
    if problem:
        deterministic_fail = deterministic_check(user_question, execution) is not None
        if deterministic_fail or agreement < 2:
            return {"success": False, "sql_query": sql,
                    "error": f"Abstained after {repairs} repair attempts: {problem}",
                    "recovery_attempts": repairs, "trace": trace}
        trace.append("judge objection remains, but a majority of candidates agree: answering")

    answer = analysis_agent(user_question, execution["rows"], execution["columns"])
    return {"success": True, "sql_query": sql, "columns": execution["columns"],
            "rows": execution["rows"], "truncated": execution.get("truncated", False),
            "answer": answer, "recovery_attempts": repairs, "agreement": agreement,
            "trace": trace}


def _generate_varied(question, database_schema, temperature, seed):
    """Same prompt as generate_sql, sampled with a different temperature/seed."""
    import nl_to_sql
    original = nl_to_sql.generate_response
    try:
        nl_to_sql.generate_response = lambda prompt: original(prompt, temperature=temperature, seed=seed)
        return nl_to_sql.generate_sql(question, database_schema)
    finally:
        nl_to_sql.generate_response = original
