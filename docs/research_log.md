# Research Log

## Project Information

**Research Title:** Design and Evaluation of a Reliability-Aware Multi-Agent LLM System with Autonomous Error Detection and Recovery for Natural Language Data Analysis.

**Project Type:** Master's Thesis — Practical Implementation and Experimental Evaluation.

## Day 1 — Development Environment Setup

### 1. Hardware Configuration

- Computer: MacBook Air
- Processor: Apple M5
- Memory: 16 GB RAM
- Architecture: ARM64
- Operating System: macOS 26.6.2

### 2. Software Configuration

- IDE: PyCharm
- Python Environment Manager: Anaconda / Conda
- Python Version: 3.12.16
- Environment Name: `reliability-agents`
- Git Version: 2.54.0

### 3. Python Environment

A dedicated Conda environment was created to isolate the thesis project's dependencies.

Environment creation command:

```bash
conda create -n reliability-agents python=3.12 -y
```

Environment activation command:

```bash
conda activate reliability-agents
```

Verified Python interpreter:

```text
/opt/anaconda3/envs/reliability-agents/bin/python
```

### 4. Project Directory Structure

The following project directories were created:

```text
ReliabilityAwareMultiAgentSystem/
│
├── data/
├── src/
│   └── main.py
├── experiments/
├── results/
├── tests/
├── docs/
│
└── README.md
```

### 5. Initial Application

Created the initial Python application in:

`src/main.py`

The application displays the project title, environment status, Python version, and initialisation message.

### 6. First Application Test

**Test Objective:** Verify that the configured Python environment can execute the initial project application.

**Execution File:** `src/main.py`

**Python Version:** 3.12.16

**Expected Result:** The application displays the project information and initialisation message.

**Actual Result:** The application executed successfully and displayed all expected output.

**Execution Status:** PASS

**Exit Code:** 0

**Conclusion:** The development environment and initial application execution were verified successfully.

## 7. Initial Technical Decisions

- Use a dedicated Python environment for dependency isolation.
- Use SQLite as the planned database for controlled experiments.
- Investigate LangGraph for multi-agent workflow orchestration.
- Compare single-agent, multi-agent without recovery, and multi-agent with recovery configurations.
- Evaluate both answer correctness and computational overhead.

These technology choices are provisional until implementation and testing confirm them.

## 8. Pending Tasks

- [ ] Finalise the project documentation.
- [ ] Design the experimental database schema.
- [ ] Prepare a sample dataset.
- [ ] Connect Python to SQLite.
- [ ] Implement the initial natural-language-to-SQL baseline.
- [ ] Review relevant academic literature.
- [ ] Define the benchmark questions and evaluation metrics.

## Research Notes

Record implementation decisions, problems, experiments, results, and relevant literature here as the project progresses.


## Day 2 — Database Schema Implementation

### Database
- Database name: NovaRetail
- Database engine: SQLite
- Database file: `data/novaretail.db`

### Tables Created
1. customers
2. products
3. orders
4. order_items

### Relationships Verified
- orders.customer_id references customers.customer_id
- order_items.order_id references orders.order_id
- order_items.product_id references products.product_id

### Verification Results
- All four tables created successfully.
- All expected columns and data types verified.
- All three foreign-key relationships verified.
- Database initialization script executed successfully.

### Execution Status
PASS

### Pending Tasks
- Generate reproducible sample data.
- Verify database constraints.
- Implement Python database connection.
- Create benchmark questions with independently verified answers.


## Day 2 — Database Implementation Completed

**Date:** 6 November 2026

### Completed tasks
- Designed NovaRetail relational database.
- Created four SQLite tables: customers, products, orders and order_items.
- Implemented primary keys, foreign keys and SQL constraints.
- Developed Python synthetic data generators.
- Generated 30 customers, 20 products, 100 orders and 257 order items.
- Implemented database seeding using Python's sqlite3 module.
- Created SQL JOIN and revenue aggregation tests.
- Added data-quality validation for customer signup dates.
- Corrected currency column names to use paise instead of cents.

### Validation results
- Total records: 407
- Orders before customer signup: 0
- Database creation: PASS
- Database seeding: PASS
- Database verification: PASS
- Python execution exit code: 0

### Next milestone
Create a reusable database connection module (`src/database.py`) to support future multi-agent integration.

### Dataset limitation
NovaRetail currently uses synthetic data for controlled development and debugging. External validation using a public real-world dataset remains pending.


---

## Day 3 — Database Connection and SQL Execution

### Completed Tasks

- Created a reusable database connection module: `src/database.py`.
- Implemented a reusable SQLite connection function.
- Created `src/sql_executor.py` for SQL query validation and execution.
- Implemented basic SQL validation.
- Restricted query execution to SELECT statements.
- Added error handling for SQL execution failures.
- Tested SQL queries against the NovaRetail database.

### Testing Results

| Test | Result |
|---|---|
| Retrieve customer records | PASS |
| Count orders | PASS |
| Query a nonexistent table | PASS |
| Handle SQL execution errors | PASS |

### Outcome

Python successfully connects to the SQLite database and executes valid SQL queries. Invalid database references are handled through controlled error responses.

---

## Day 4 — Read-Only Database Security

### Completed Tasks

- Implemented a separate read-only SQLite connection in `src/database.py`.
- Updated `src/sql_executor.py` to use the read-only connection.
- Added a direct test of SQLite read-only protection.
- Improved database connection handling by explicitly closing connections.
- Verified that valid SELECT queries continue to execute successfully.

### Testing Results

| Test | Expected Result | Actual Result |
|---|---|---|
| Retrieve customer records | Successful execution | PASS |
| Count orders | 100 orders | PASS |
| Query nonexistent table | Controlled error | PASS |
| INSERT through SQL validator | Rejected | PASS |
| Direct INSERT through SQLite | Rejected by read-only mode | PASS |

### Key Findings

1. The SQL validation layer rejects queries that do not begin with SELECT.
2. SQLite read-only mode independently prevents database modifications.
3. Valid SELECT queries execute successfully using the read-only connection.
4. Invalid database references return controlled error messages.

### Current Implementation Status

The database connection, SQL execution and basic read-only protection mechanisms are implemented and tested.

### Next Steps

- Implement SQLite authorizer restrictions.
- Improve SQL validation and execution safeguards.
- Add a comprehensive SQL test suite.
- Begin preparing the natural-language-to-SQL LLM integration.



---

## Day 5 — SQLite Authorizer and Automated Security Testing

### Completed Tasks

- Implemented a SQLite database authorizer in `src/database.py`.
- Adopted a default-deny security policy.
- Explicitly allowed the SQLite operations required for read-only queries:
  - SELECT
  - READ
  - FUNCTION
  - RECURSIVE
- Blocked database operations not included in the allowlist.
- Created `tests/test_sql_security.py` using Python's `unittest` framework.
- Implemented nine automated security tests.

### Testing Results

| Test | Expected Result | Actual Result |
|---|---|---|
| SELECT query | Allowed | PASS |
| SELECT with JOIN | Allowed | PASS |
| SELECT with SUM | Allowed | PASS |
| INSERT | Blocked | PASS |
| UPDATE | Blocked | PASS |
| DELETE | Blocked | PASS |
| CREATE TABLE | Blocked | PASS |
| PRAGMA | Blocked | PASS |
| ATTACH DATABASE | Blocked | PASS |

**Overall result: 9/9 tests passed.**

### Key Findings

1. SQLite authorizer restrictions provide an additional security layer.
2. Read-only queries continue to work with the authorizer enabled.
3. Attempts to perform tested database modifications and restricted operations are rejected.
4. Automated tests make it possible to verify the security policy consistently.

### Current Limitations

- The security tests cover nine specific operations, not every possible SQL operation or attack.
- SQL validation and query resource limits still require improvement.
- Additional testing is needed before describing the executor as production-ready.

### Outcome

The initial SQLite security layer and automated test suite are implemented successfully.

### Next Steps

- Improve SQL validation.
- Add query execution and result-size limits.
- Begin preparing the natural-language-to-SQL integration.

---

## Day 6 — SQL Validation and Query Execution Safeguards

### Completed Tasks

- Improved SQL query validation in `src/sql_executor.py`.
- Restricted query execution to SELECT statements and CTE queries.
- Added rejection of SQL comments and multiple SQL statements.
- Implemented a maximum query execution time of 5 seconds using SQLite's progress handler.
- Used Python's `time.monotonic()` for elapsed-time measurement.
- Implemented a maximum result limit of 100 rows.
- Added result truncation detection.
- Implemented structured error classification for SQL execution failures.

### Testing Results

| Test | Expected Result | Actual Result |
|---|---|---|
| CTE query | Successful execution | PASS |
| SELECT customer records | Successful execution | PASS |
| SELECT order records | Successful execution | PASS |
| COUNT aggregation | Successful execution | PASS |
| CROSS JOIN exceeding 100 rows | Maximum 100 rows returned with truncation flag | PASS |
| Query referencing unknown table | Controlled SQL execution error | PASS |
| INSERT query | Rejected by SQL validation | PASS |
| Long-running recursive CTE | Interrupted by execution timeout | PASS |
| Direct database write attempt | Blocked by SQLite authorizer | PASS |

### Key Findings

1. Valid SELECT and CTE queries execute successfully.
2. The executor limits query results to a maximum of 100 rows.
3. The truncation flag identifies when additional query results exist beyond the configured limit.
4. Long-running recursive queries are interrupted when the execution-time limit is exceeded.
5. SQL execution failures are classified into structured error categories, including validation errors, SQL execution errors and timeouts.
6. The read-only connection and SQLite authorizer provide additional protection against database modifications.

### Current Limitations

- SQL validation currently relies on basic string-based checks and requires a more robust SQL parsing approach.
- The five-second execution limit and 100-row result limit require further evaluation under different workloads.
- Current testing covers selected query behaviours and does not establish complete protection against every SQL attack.
- Semantic correctness of SQL queries has not yet been evaluated.
- Natural-language-to-SQL generation has not yet been integrated.

### Outcome

The initial SQL validation and execution safeguards have been implemented and manually tested against the NovaRetail database.

The SQL executor can execute valid read-only queries, detect execution failures, interrupt long-running queries and limit returned result sizes.

### Next Steps

- Improve SQL validation using a more robust parsing approach.
- Expand automated testing to cover the SQL executor itself.
- Select and configure an LLM provider for natural-language-to-SQL generation.
- Implement the first single-agent natural-language-to-SQL baseline.
- Begin evaluating generated SQL queries for execution and answer correctness.

## Day 7 — Local LLM Setup and Initial SQL Generation Experiment

### 1. Objective
Install and configure a locally hosted Large Language Model (LLM) to support the Natural Language to SQL component of the proposed reliability-aware multi-agent system, without relying on paid API services.

### 2. Environment Setup
- Local LLM runtime: Ollama
- Ollama version: 0.40.15
- Model: Qwen2.5 7B
- Model storage: Approximately 4.7 GB
- Hardware: Apple Silicon (ARM64), 16 GB unified memory
- Operating system: macOS
- API expenditure: Zero

### 3. Model Installation and Verification
Successfully installed Ollama and downloaded Qwen2.5 7B.

The model was launched locally using:

```bash
ollama run qwen2.5:7b
```

An initial natural-language question was provided to test SQL generation capabilities.

### 4. Initial SQL Generation Experiment

Task: Identify the top five customers by total purchase value, considering only delivered orders, and report purchase values in Indian rupees.

The model generated SQL using:
- Customers, orders and order_items tables.
- Appropriate JOIN operations.
- A Delivered status filter.
- GROUP BY aggregation.
- ORDER BY descending.
- LIMIT 5.

### 5. Error Identified

The initial SQL used integer division when converting paise into rupees:

```sql
SUM(oi.quantity * oi.unit_price_paise / 100)
```

This could produce inaccurate financial calculations because SQLite may perform integer division.

The expression was corrected to:

```sql
SUM(oi.quantity * oi.unit_price_paise) / 100.0
```

This preserves fractional rupee values.

### 6. Python Integration Test

Created:

`src/test_llm_query.py`

The corrected SQL was executed through the existing `execute_sql()` function against the NovaRetail SQLite database.

Observed results:

| Customer | Purchase value |
|---|---:|
| Omkar Pawar | ₹157,245.00 |
| Ananya Singh | ₹96,972.00 |
| Kavya Menon | ₹89,165.00 |
| Kabir Shah | ₹78,350.00 |
| Sneha Rao | ₹67,275.00 |

Execution completed successfully with exit code 0.

### 7. Observations
- Local LLM inference is operational.
- The model can generate SQL from natural-language instructions.
- The generated query followed the intended database relationships.
- A numerical precision issue was identified during manual inspection.
- The corrected SQL executed successfully through the existing safe SQL executor.

### 8. Research Significance
This experiment demonstrates why SQL execution success alone is insufficient for measuring system reliability.

A query may execute successfully while still producing inaccurate numerical results. The proposed reliability mechanism must therefore investigate both execution errors and logical or numerical correctness.

This is an initial exploratory experiment, not a formal benchmark result.

### 9. Limitations
- Only one initial SQL-generation task was tested.
- The initial model-generated query was manually inspected and corrected.
- No systematic semantic accuracy evaluation has been conducted.
- No automated error detection or recovery mechanism has been integrated yet.
- Model latency and token usage have not yet been benchmarked.

### 10. Next Steps
1. Connect Ollama directly to Python.
2. Implement automatic natural-language-to-SQL generation.
3. Pass generated SQL through the existing validation and execution pipeline.
4. Build the single-agent baseline.
5. Begin systematic SQL accuracy testing.

### Day 8 — Python-to-LLM Integration and Initial NL-to-SQL Baseline

**Completed:**
- Connected Python to the locally hosted Qwen2.5 7B model through the Ollama HTTP API.
- Created `src/llm_client.py` using Python's built-in HTTP and JSON libraries.
- Verified successful prompt submission and response retrieval.
- Created `src/nl_to_sql.py` with NovaRetail database schema context and SQL-generation instructions.
- Created `src/test_nl_to_sql.py` to test natural-language-to-SQL generation and execution.
- Integrated the SQL generator with the existing read-only SQL executor.

**Initial experiment:**

Question: "Show the top 5 customers by total purchase value."

- First generation: SQL execution failed because the model incorrectly referenced `o.quantity` and `o.unit_price_paise` instead of the columns belonging to `order_items`.
- Second generation: The model generated valid column references and the query executed successfully.
- Five customer results were returned.
- This demonstrates observed variation in SQL-generation correctness across two runs.

**Limitations:**
- Only two attempts have been observed; this is not sufficient to estimate model reliability.
- The query currently includes every order status.
- Semantic correctness still requires comparison with an independently verified expected result.
- No autonomous error detection or recovery has been implemented.

**Next steps:**
- Define benchmark questions and their expected SQL/results.
- Run repeatable baseline experiments.
- Measure execution accuracy, semantic correctness and latency.
- Implement the multi-agent architecture and recovery mechanism after establishing the baseline.

### Day 9 — Initial SQL Benchmark Development

**Completed:**
- Created `experiments/benchmark_questions.py`.
- Defined 10 natural-language benchmark questions with expected SQL queries.
- Covered counting, filtering, joins, aggregation, date conditions, sorting, DISTINCT and currency conversion.
- Created `experiments/validate_benchmark.py` to execute the expected queries against the read-only SQLite database.
- Successfully executed all 10 expected SQL queries.

**Validation result:**
- Expected SQL queries passed: 10/10.
- Questions cover easy and medium difficulty levels.
- Expected outputs were recorded for subsequent comparison with LLM-generated queries.

**Research note:**
Successful execution validates SQL compatibility, but does not independently establish semantic correctness or LLM generation accuracy. Expected outputs must be preserved as ground truth for later experiments.

**Next steps:**
- Expand and review the benchmark.
- Establish repeatable model settings.
- Evaluate the single-agent NL-to-SQL baseline before implementing autonomous recovery.

### Day 10 — Controlled LLM Generation Experiment

**Configuration:**
- Model: Qwen2.5 7B
- Runtime: Ollama local API
- Temperature: 0.0
- Seed: 42
- Test question: "Show the top 5 customers by total purchase value."

**Observations:**
- Two generation attempts were conducted using identical inputs and settings.
- Both attempts generated the same SQL query.
- Both attempts failed during SQL execution.
- The generated query incorrectly referenced `o.quantity`, although `quantity` belongs to the `order_items` table, aliased as `oi`.
- The database executor correctly classified the failure as `SQL_EXECUTION_ERROR`.

**Interpretation:**
The two observed runs produced consistent but incorrect SQL. This illustrates that controlled generation and reproducibility do not guarantee correctness.

**Limitations:**
- Two runs are insufficient to establish general model determinism or reliability.
- This is an initial observation, not a statistical evaluation.
- No autonomous error detection or recovery was used.

**Next step:**
Implement a controlled single-agent baseline evaluation using the benchmark questions.

### Day 11 — Single-Agent Baseline Evaluation

**Objective:** Establish the initial performance of the single-agent NL-to-SQL system.

**Experimental configuration:**
- Model: Qwen2.5 7B
- Runtime: Ollama local API
- Temperature: 0.0
- Seed: 42
- Database: NovaRetail synthetic SQLite database
- Benchmark: 10 natural-language questions
- Execution: Read-only SQL executor with query timeout and result-row limit.

**Results:**
- Total benchmark questions: 10
- SQL execution successes: 10
- SQL execution success rate: 100%
- Correct answers: 10
- Result correctness rate: 100%
- Ground-truth execution errors: 0

**Evaluation methodology:**
Generated SQL results were compared against independently prepared expected SQL results. Numeric comparisons used floating-point tolerance, and row ordering was ignored for result-set comparisons. The benchmark's tenth question explicitly specified alphabetical tie-breaking.

**Interpretation:**
The single-agent system successfully executed all ten benchmark questions and produced matching result sets in this experimental run.

**Limitations:**
- Only one run per question has been evaluated.
- The benchmark contains only ten questions.
- Synthetic data does not establish generalisation to real-world databases.
- Latency variability, token usage and computational cost require further measurement.
- SQL execution success alone does not establish semantic correctness.

**Next steps:**
1. Expand and strengthen the benchmark.
2. Conduct repeated baseline trials.
3. Build the multi-agent system without autonomous recovery.
4. Implement autonomous error detection and bounded recovery.
5. Compare all three system configurations under identical conditions.

---

## Day 12 — Baseline Evaluation Utilities and Automated Testing

### Objective

Strengthen the evaluation process for the single-agent NL-to-SQL baseline by implementing reusable result-comparison utilities and automated tests.

### Completed Tasks

- Created `src/evaluation_utils.py`.
- Implemented `values_match()` to compare numeric values using floating-point tolerance.
- Implemented `rows_match()` to compare result rows without requiring a particular row order.
- Implemented `ordering_matches()` to verify explicitly specified ordering rules, including tie-breakers.
- Updated `experiments/evaluate_baseline.py` to compare generated results against expected benchmark results.
- Added handling for different result-field names in the baseline experiment output.
- Created `tests/test_evaluation.py` containing eight automated tests.

### Testing Results

| Test | Result |
|---|---|
| Matching result rows regardless of row order | PASS |
| Detecting incorrect result values | PASS |
| Validating descending order | PASS |
| Rejecting incorrect descending order | PASS |
| Validating alphabetical tie-breaking | PASS |
| Rejecting incorrect alphabetical tie-breaking | PASS |
| Handling equal values without a tie-break rule | PASS |
| Comparing floating-point values with tolerance | PASS |

**Overall automated test result: 8/8 tests passed.**

### Initial Baseline Evaluation

The updated evaluator was executed against the existing single-agent baseline results.

- Total benchmark questions: 10
- Successful SQL executions: 10
- Correct final answers: 10
- SQL execution success rate: 100%
- Answer correctness rate: 100%

These results represent the existing initial baseline run, with one run per question.

### Key Findings

1. Result comparison should distinguish between row values and row ordering.
2. Row order can be ignored when the natural-language question does not specify an order.
3. Explicit ordering requirements and tie-breakers can be checked separately.
4. Floating-point tolerance helps avoid insignificant numerical comparison errors.
5. Automated tests help verify that the evaluation logic behaves as intended.

### Limitations

- Only one baseline run per question has been evaluated.
- The benchmark currently contains ten questions.
- The benchmark uses synthetic data and does not establish real-world generalisation.
- Repeated experiments and external dataset validation remain pending.
- Latency variability, token usage and computational cost still need to be measured.
- SQL execution success alone does not establish semantic correctness.

### Outcome

The initial baseline evaluation pipeline and its core comparison utilities have been implemented successfully.

The evaluator reports 10/10 successful SQL executions and 10/10 matching answers for the current baseline run. All eight automated evaluation utility tests also passed.

These results should be interpreted as initial experimental findings, not evidence of general 100% system reliability.

### Next Milestone

Begin System B: a multi-agent LLM system without autonomous error detection and recovery.

System A will remain unchanged so that all three system configurations can eventually be compared under consistent experimental conditions.

## Day 13 — Multi-Agent System B Implementation and Initial Evaluation

### Objective
Implement and evaluate System B, a multi-agent natural-language database analysis system without autonomous error recovery.

### Components implemented
1. SQL Agent (`src/agents/sql_agent.py`): generates SQL using the existing NL-to-SQL module.
2. Analysis Agent (`src/agents/analysis_agent.py`): converts database query results into natural-language answers.
3. Orchestrator (`src/agents/orchestrator.py`): coordinates SQL generation, execution, and answer generation.
4. Existing SQL Executor reused without modification, preserving its read-only database access, execution timeout, and result-row limit.

### Experiment
Created `experiments/run_multi_agent.py` to evaluate System B using the same ten benchmark questions as System A.

Results saved to `results/multi_agent_system_b.json`.

### Initial results

- Total benchmark questions: 10
- SQL execution successes: 10
- SQL execution failures: 0
- Database answer correctness: 10/10 (100%)

All ten database result sets matched the expected benchmark results, including the required ordering for Questions 5 and 10.

### Comparison with System A

Both System A and System B achieved 100% SQL execution success and 100% database answer correctness in their initial ten-question evaluations.

System B adds multi-agent coordination and natural-language answer generation, but no improvement in database correctness has yet been demonstrated.

### Observed issue

The natural-language answer for Question 10 did not preserve the correct ranking of customers by order count, despite the underlying database results passing evaluation.

This indicates that database-result correctness and natural-language answer correctness must be evaluated separately.

### Limitations

- Only ten benchmark questions.
- Initial evaluation runs only.
- Synthetic NovaRetail database.
- No repeated-run statistical analysis.
- Natural-language answer correctness not yet systematically evaluated.
- No autonomous error detection or recovery implemented.

### Next steps

1. Evaluate natural-language answer correctness.
2. Compare execution time and computational overhead between System A and System B.
3. Design and implement System C with bounded autonomous error detection and recovery.
4. Conduct repeated experiments using consistent conditions.

# Day 14 — System C Implementation and Initial Evaluation

## 1. Objective

The objective of Day 14 was to implement System C, a reliability-aware multi-agent system with autonomous SQL error detection and bounded recovery.

System C extends the multi-agent architecture developed in System B. Its main purpose is to detect SQL execution failures, generate corrected SQL queries using the LLM, and retry execution within a predefined limit.

System A and System B were kept separate and unchanged to preserve the experimental baselines.

## 2. Error Detection Agent

Created:

`src/agents/error_detection_agent.py`

Implemented a deterministic error detection function that examines the SQL executor's result.

The agent checks the `success` field:

- If SQL execution succeeds, it reports that no error was detected.
- If SQL execution fails, it reports the execution error.

This component detects SQL execution failures. It does not independently evaluate semantic correctness or detect incorrect natural-language answers.

## 3. SQL Correction Function

Updated:

`src/nl_to_sql.py`

Implemented a new function:

`regenerate_sql(user_question, failed_sql, error_message)`

The function sends the following information to the local LLM:

- Original user question.
- Failed SQL query.
- Database error message.
- Database schema and SQL generation rules.

The LLM then generates a corrected SQLite SELECT query.

The function was tested using an intentionally incorrect query:

`SELECT COUNT(customer) FROM customers`

The correction function generated:

`SELECT COUNT(customer_id) FROM customers`

The corrected query executed successfully.

## 4. System C Orchestrator

Created and updated:

`src/agents/orchestrator_c.py`

Implemented the System C orchestration workflow:

1. Generate the initial SQL query.
2. Execute the query using the existing SQL executor.
3. Detect execution errors.
4. If an error occurs, request a corrected query from the LLM.
5. Execute the corrected query.
6. Repeat recovery when necessary, subject to a maximum of two recovery attempts.
7. Generate the final natural-language answer if execution succeeds.
8. Return the final result, SQL query, execution status and number of recovery attempts.

System C uses the existing SQL executor and analysis agent. System B's orchestrator was not modified.

## 5. Recovery Testing

Two controlled tests were performed.

### Test 1: Successful recovery

An intentionally incorrect SQL query was supplied:

`SELECT COUNT(customer) FROM customers`

The database returned an error because the column did not exist.

The error detection component identified the failure. The correction function generated a valid query:

`SELECT COUNT(customer_id) FROM customers`

The corrected query executed successfully.

Result:

- Initial execution: Failed.
- Recovery attempts: 1.
- Final execution: Successful.
- Final answer: 30 customers are in the database.

### Test 2: Recovery limit

A second test deliberately forced the correction mechanism to return another invalid SQL query.

The initial query and both corrected queries failed.

Result:

- Initial execution: Failed.
- First recovery attempt: Failed.
- Second recovery attempt: Failed.
- Total recovery attempts: 2.
- Final execution status: Failed.
- System stopped without an infinite retry loop.

This confirmed that the recovery mechanism respects its configured maximum of two attempts.

## 6. System C Benchmark Experiment

Created:

`experiments/run_system_c.py`

The script executed all ten benchmark questions using System C and saved the experiment results to:

`results/multi_agent_system_c.json`

The experiment recorded:

- Question ID and question.
- Generated SQL query.
- SQL execution status.
- Execution errors.
- Returned columns and rows.
- Truncation status.
- Final natural-language answer.
- Number of recovery attempts.
- Elapsed execution time.

### Initial benchmark results

| Metric | Result |
|---|---:|
| Total benchmark questions | 10 |
| Successful SQL executions | 10 |
| Failed SQL executions | 0 |
| Recovery attempts | 0 |
| Approximate total elapsed time | 37.4 seconds |

All ten questions executed successfully without requiring recovery.

## 7. System C Evaluation

Created:

`experiments/evaluate_system_c.py`

The evaluator reused the existing evaluation utilities:

- `rows_match()`
- `ordering_matches()`

For each benchmark question, the evaluator executed the expected SQL query and compared the expected database results with the results returned by System C.

### Evaluation results

| Metric | Result |
|---|---:|
| Total benchmark questions | 10 |
| Successful SQL executions | 10 |
| Correct database answers | 10 |
| Execution success rate | 100.00% |
| Database answer correctness rate | 100.00% |

All ten benchmark questions passed the database-result evaluation.

## 8. Observations and Limitations

1. System C successfully implemented SQL execution error detection and bounded autonomous recovery.
2. The controlled recovery test demonstrated that an invalid SQL query could be corrected and successfully executed.
3. The retry-limit test confirmed that recovery stops after two attempts.
4. None of the ten benchmark questions triggered recovery. Therefore, the benchmark did not demonstrate a measurable recovery benefit.
5. The database-result evaluator does not evaluate the correctness of the final natural-language answer.
6. Question 10 exposed a natural-language ranking error: the Analysis Agent listed a customer with five orders before a customer with six orders, despite the SQL query specifying descending order. This demonstrates that correct SQL results do not guarantee correct natural-language answers.
7. The current evaluation uses ten synthetic benchmark questions and a single experiment run. The results should be treated as preliminary.
8. Repeated experiments, controlled fault-injection tests, natural-language answer evaluation and external dataset validation remain necessary.

## 9. Current System Comparison

| Feature | System A | System B | System C |
|---|---|---|---|
| Single-agent baseline | Yes | No | No |
| Multi-agent coordination | No | Yes | Yes |
| SQL error detection | No autonomous recovery | Execution failure handling | Yes |
| Autonomous SQL correction | No | No | Yes |
| Bounded recovery | No | No | Yes |
| Initial database-answer accuracy | 10/10 | 10/10 | 10/10 |

The initial results show that all three configurations achieved the same database-answer correctness on the ten-question benchmark. The benefit of System C's recovery mechanism has not yet been established through this benchmark because no recovery was triggered.

## 10. Next Steps

- Evaluate natural-language answer correctness separately from database-result correctness.
- Design controlled fault-injection experiments to compare System B and System C under equivalent SQL failure conditions.
- Repeat experiments to measure consistency and variability.
- Measure end-to-end latency and recovery overhead.
- Investigate external dataset validation using the public UCI Online Retail dataset.
- Continue documenting limitations and experimental observations.

**Day 14 status: System C implementation, controlled recovery tests and initial benchmark evaluation completed.**

# Day 15 — Controlled Fault-Injection Experiments

## Objective

The objective of Day 15 was to compare System B (multi-agent system without recovery) and System C (multi-agent system with autonomous error detection and recovery) under deliberately introduced SQL failures.

Both systems were given the same faulty SQL query in each experiment. This was achieved by temporarily replacing the imported `sql_agent` function in both orchestrator modules using Python lambda functions.

The experiments were conducted using the NovaRetail SQLite database.

## Experimental Setup

Created:

`experiments/fault_injection_test.py`

The experiment script:
- Injects a deliberately incorrect SQL query.
- Provides the same query to System B and System C.
- Executes both systems.
- Compares their outcomes.
- Saves the results as separate JSON files in the `results/` directory.

## Experiment 1 — Invalid Column

Injected SQL:

```sql
SELECT COUNT(nonexistent_column) FROM customers
```

Results:

- System B failed because the specified column did not exist.
- System C detected the execution error.
- System C generated a corrected SQL query using `customer_id`.
- The corrected query executed successfully.
- System C returned the answer: 30 customers.
- Recovery attempts: 1.

Result: System C successfully recovered from the invalid-column error.

## Experiment 2 — Invalid Table

Injected SQL:

```sql
SELECT COUNT(*) FROM nonexistent_table
```

Results:

- System B failed because the specified table did not exist.
- System C detected the execution error.
- System C generated a corrected query using the `customers` table.
- The corrected query executed successfully.
- System C returned the answer: 30 customers.
- Recovery attempts: 1.

Result: System C successfully recovered from the invalid-table error.

## Experiment 3 — Malformed SQL / Validation Rejection

Injected SQL:

```sql
SELEC COUNT(*) FROM customers
```

Results:

- System B rejected the query.
- System C detected the validation error.
- System C generated a corrected SQL query.
- The corrected query executed successfully.
- System C returned the answer: 30 customers.
- Recovery attempts: 1.

The SQL executor rejected the malformed query during its pre-execution validation because it did not begin with an allowed SELECT or WITH keyword.

Result: System C successfully recovered from the malformed SQL query.

## Experiment 4 — Semantic Error

Injected SQL:

```sql
SELECT COUNT(*) FROM products
```

Original user question:

"How many customers are in the database?"

The injected SQL is syntactically valid and executes successfully, but it queries the products table instead of the customers table.

Database facts:
- Customers: 30
- Products: 20

Results:

- System B executed the query successfully and returned 20.
- System C also executed the query successfully.
- System C generated the natural-language answer: "20 customers are in the database."
- System C did not detect the semantic error.
- Recovery attempts: 0.

Result: Both systems produced an incorrect answer because the SQL query was executable but did not answer the original question.

This experiment demonstrated an important limitation of the current System C error-detection mechanism. It checks SQL execution success or failure but does not independently verify whether the query is semantically correct.

## Summary of Fault-Injection Experiments

| Experiment | Fault type | System B | System C |
|---|---|---|---|
| 1 | Invalid column | Failed | Recovered |
| 2 | Invalid table | Failed | Recovered |
| 3 | Malformed SQL / validation rejection | Failed | Recovered |
| 4 | Semantic error | Incorrect result | Incorrect result |

System C recovered from all three tested SQL execution or validation failures. However, it failed to detect the semantic error in Experiment 4.

## Research Interpretation

The experiments provide preliminary evidence that the autonomous recovery mechanism can handle selected SQL execution and validation failures.

However, the results also demonstrate that successful SQL execution does not necessarily mean that the correct answer has been produced.

The current error-detection component only checks the execution status returned by the SQL executor. It does not verify the semantic relationship between the original user question, the generated SQL query and the resulting database answer.

Therefore, the current implementation has a limitation in detecting semantically incorrect but executable SQL queries.

## Limitations

1. Only four fault categories have been tested.
2. The experiments have not yet been repeated for statistical evaluation.
3. The benchmark uses a synthetic database.
4. Semantic correctness is not currently checked by the recovery mechanism.
5. The experiments do not yet establish general reliability across different databases or LLMs.

## Next Steps

1. Preserve and organize all four experiment result files separately.
2. Investigate possible approaches to semantic error detection.
3. Expand the fault-injection experiments.
4. Conduct repeated experiments under consistent conditions.
5. Measure latency and computational cost.
6. Compare the reliability of Systems A, B and C using quantitative results.

**Day 15 status: Completed — initial controlled fault-injection experiments.**

# Day 16 — Semantic Error Detection and Recovery

## Objective

Extend System C to detect and recover from semantic SQL errors, in addition to SQL execution errors.

The Day 15 experiments demonstrated that a query can execute successfully while answering the wrong question. The existing execution-error detector could not identify this type of failure.

## 1. Semantic Validation Agent

Created:

`src/agents/semantic_validation_agent.py`

Implemented an LLM-based semantic validation component using the local Qwen2.5 7B model.

The agent receives:
- Original user question.
- Generated SQL query.
- Database query results.

It determines whether the SQL query addresses the original question and returns:
- `VALID` when the query is semantically correct.
- `INVALID` with a short explanation when the query is incorrect.

The component was tested using two cases:

**Test 1 — Correct SQL**

Question: How many customers are in the database?

SQL:
`SELECT COUNT(*) FROM customers`

Result: Semantic validation passed.

**Test 2 — Incorrect SQL**

SQL:
`SELECT COUNT(*) FROM products`

Result: Semantic validation rejected the query and identified that the `customers` table should have been used.

Both tests produced the expected validation outcomes.

## 2. Semantic SQL Correction

Added a new function, `regenerate_sql_semantic()`, to:

`src/nl_to_sql.py`

The function receives:
- Original user question.
- Incorrect SQL query.
- Semantic validation feedback.

It uses the database schema and feedback to generate a corrected SQLite SELECT query.

The correction function was tested independently.

Original SQL:

`SELECT COUNT(*) FROM products`

Semantic feedback:

The query should use the customers table, not the products table.

Corrected SQL:

`SELECT COUNT(*) FROM customers`

The correction function successfully generated the expected SQL.

## 3. Integration into System C

Updated:

`src/agents/orchestrator_c.py`

System C now supports two recovery paths:

1. SQL execution errors are detected by the Error Detection Agent and corrected using `regenerate_sql()`.
2. Semantically incorrect SQL is detected by the Semantic Validation Agent and corrected using `regenerate_sql_semantic()`.

Both recovery paths use a shared maximum recovery limit of two attempts.

System C now reports success only when:
- SQL execution succeeds.
- Semantic validation passes.

If semantic validation continues to fail after the maximum number of attempts, the system returns:

`success: False`

with the error type:

`SEMANTIC_VALIDATION_ERROR`

## 4. Controlled Experiments

### Experiment 1 — Normal execution

Question: How many customers are in the database?

Generated SQL:

`SELECT COUNT(*) FROM customers`

Results:
- SQL execution: Successful.
- Semantic validation: Passed.
- Final answer: 30 customers.
- Recovery attempts: 0.
- Overall success: True.

### Experiment 2 — Semantic error recovery

The initial SQL query was deliberately replaced with:

`SELECT COUNT(*) FROM products`

The query executed successfully but returned 20 instead of the required customer count.

System C:
1. Executed the incorrect SQL.
2. Detected the semantic mismatch.
3. Generated corrected SQL.
4. Executed the corrected query.
5. Passed semantic validation.
6. Returned the correct answer.

Results:
- Final SQL: `SELECT COUNT(*) FROM customers`
- Final answer: 30 customers.
- Recovery attempts: 1.
- Semantic validation: Passed.
- Overall success: True.

### Experiment 3 — Recovery limit

A controlled test forced the semantic validator to reject every query.

Two different corrected queries were supplied to simulate repeated semantic correction attempts.

Results:
- Recovery attempts: 2.
- Final SQL: `SELECT COUNT(*) FROM order_items`
- Semantic validation: Not passed.
- Overall success: False.
- Error type: `SEMANTIC_VALIDATION_ERROR`.

This confirmed that System C stops after two recovery attempts and does not report success when semantic validation fails.

## 5. Day 16 Outcome

The System C implementation now includes:
- SQL execution error detection.
- SQL execution error recovery.
- Semantic SQL validation.
- Semantic SQL correction.
- Bounded recovery with a maximum of two attempts.
- Explicit failure reporting when semantic validation does not pass.

The controlled experiments demonstrated that System C can recover from a tested semantic SQL error while preserving its recovery limit.

## 6. Limitations

The semantic validator uses an LLM and may produce incorrect judgments. Successful validation does not guarantee that the SQL query is factually correct.

The experiments conducted on this day were controlled tests using the synthetic NovaRetail database. They do not establish general semantic validation accuracy or statistically significant reliability improvements.

Further evaluation is required using the benchmark questions, repeated experiments, and independently verified expected results.

## 7. Next Steps

- Run the updated System C against the complete ten-question benchmark.
- Evaluate semantic validation and final natural-language answer correctness separately from SQL execution accuracy.
- Compare Systems A, B, and C under consistent experimental conditions.
- Investigate false-positive and false-negative semantic validation decisions.

# Day 17 — Updated System C Benchmark and Evaluation

## Objective

The objective of Day 17 was to evaluate the updated System C after integrating semantic validation and improving the Analysis Agent's response instructions.

A specific issue had been observed in Question 10: although the SQL query returned customers in the correct ranking order, the Analysis Agent incorrectly rearranged the results in its natural-language response.

## 1. Analysis Agent Prompt Improvement

The `RULES` section in `src/agents/analysis_agent.py` was updated.

The new instructions require the Analysis Agent to:

1. Give a clear and simple answer.
2. Use only information in the database results.
3. Avoid inventing numbers, names, or facts.
4. Report when no matching data is found.
5. Preserve the exact order of database rows.
6. Never independently rearrange, sort, or rank results.
7. Preserve numerical values exactly.
8. Include every relevant row.

The purpose was to prevent the Analysis Agent from changing the order or values returned by the database.

## 2. Updated System C Benchmark Experiment

The experiment was executed using:

`experiments/run_system_c.py`

All ten benchmark questions completed successfully.

**Results:**

- Total benchmark questions: 10
- Successful SQL executions: 10
- Failed SQL executions: 0
- Total recovery attempts: 0
- Process completed successfully.

The results were saved to:

`results/multi_agent_system_c.json`

### Question 10 — Ranking Verification

Question 10 asked for the five customers with the highest number of non-cancelled orders, with alphabetical ranking for customers having the same order count.

The final answer was:

| Rank | Customer | Orders |
|---|---|---:|
| 1 | Rohan Mehta | 6 |
| 2 | Aditya Verma | 5 |
| 3 | Arjun Nair | 4 |
| 4 | Karan Sethi | 4 |
| 5 | Maya Fernandes | 4 |

The response preserved the correct database ordering, resolving the previously observed ranking mismatch in this run.

## 3. System C Evaluation

The updated evaluation was executed using:

`experiments/evaluate_system_c.py`

All ten benchmark questions passed.

**Evaluation results:**

| Metric | Result |
|---|---:|
| Total benchmark questions | 10 |
| Successful SQL executions | 10 |
| Correct database answers | 10 |
| Execution success rate | 100% |
| Database answer correctness rate | 100% |

The evaluator compared the actual database results against the expected results obtained by executing the benchmark's expected SQL queries.

## 4. Observations

1. System C successfully executed all ten benchmark questions.
2. All ten database results matched the expected results.
3. The semantic validation mechanism accepted all ten queries.
4. No recovery was required during this normal benchmark run.
5. The updated Analysis Agent instructions resolved the observed Question 10 ranking-order issue in this run.
6. Question 5 returned all twenty product rows in the database-provided order.

## 5. Limitations

The results represent one benchmark run involving ten questions on the synthetic NovaRetail database.

The 100% database-answer correctness rate does not establish general reliability or statistical significance.

The evaluator checks SQL execution and database result correctness. It does not independently establish the correctness of every natural-language response.

The semantic validator is LLM-based and its own accuracy still requires independent evaluation.

Repeated experiments and further testing are necessary before drawing broader conclusions.

## 6. Conclusion

Day 17 confirmed that the updated System C successfully passed all ten benchmark questions, achieving 100% SQL execution success and 100% database-answer correctness in this run.

The Analysis Agent prompt was also improved to preserve database row order, addressing the previously observed ranking mismatch in Question 10.

The next stage will focus on evaluating natural-language answer quality separately from SQL execution and database-result correctness.

**Day 17 Status: Completed.**

## Day 18 — Natural-Language Answer Quality Evaluation

### Objective

Evaluate the quality of the final natural-language answers generated by System C independently of SQL execution and database result correctness.

### Evaluation criteria

Four criteria were selected:

1. **Factual accuracy:** Whether the customer names and order counts stated in the answer match the database results.
2. **Completeness:** Whether every expected result is included.
3. **Ordering:** Whether the answer preserves the order of the database results.
4. **Clarity:** Whether the answer is presented in a readable format.

Each criterion receives 1 point for a pass and 0 points for a failure. The maximum score is 4 points per question.

### Initial evaluation

A Python evaluation script was created:

`experiments/evaluate_natural_language.py`

The initial evaluator was designed for Question 10 and compared the generated answer against the actual database rows saved in the System C experiment results.

The evaluator was subsequently updated to recognize three answer formats:
- Raw Python-style lists.
- Customer names followed by order counts.
- Numbered lists containing customer names and order counts.

### Question 10 evaluation result

The latest System C answer included four customers but omitted Maya Fernandes and did not preserve the database ranking.

| Criterion | Score |
|---|---:|
| Factual accuracy | 1/1 |
| Completeness | 0/1 |
| Ordering | 0/1 |
| Clarity | 1/1 |
| **Total** | **2/4** |

### Key findings

- The generated SQL query was correct.
- The database returned five correctly ordered customer records.
- The Analysis Agent produced a readable answer but omitted one customer.
- The Analysis Agent also changed the ranking.
- Additional prompt instructions did not reliably prevent these errors.
- SQL execution and database result correctness do not guarantee that the final natural-language answer is accurate and complete.

### Architectural observation

A potential improvement is to use deterministic Python formatting for structured database results instead of relying on the LLM to reproduce and format every row.

Python can preserve the original database order and include every returned row without asking the LLM to reinterpret the results.

This is a proposed improvement and has not yet been implemented or experimentally evaluated.

### Limitations

- The current natural-language evaluator only evaluates Question 10.
- The four criteria use a preliminary binary scoring scheme.
- The evaluation is based on one experiment run.
- The results do not establish general natural-language answer reliability.
- Further testing is required before extending the evaluator to all ten benchmark questions.

### Next steps

1. Improve the handling of structured database results.
2. Test whether deterministic formatting preserves all rows and their order.
3. Evaluate the revised output against the same Question 10 database results.
4. Consider extending natural-language evaluation to the remaining benchmark questions.

## Day 19 — Improving Structured Result Reliability and Evaluating System C

### 1. Objective

The objective of Day 19 was to improve the reliability of final answers generated by the multi-agent system, particularly when database results contain multiple records or require a specific ranking.

Earlier experiments showed that the LLM-based Analysis Agent sometimes changed the order of database records or omitted records when generating natural-language answers.

The approach adopted was to use deterministic Python formatting for structured database results instead of relying on the LLM to reproduce them.

### 2. Python Result Formatter

Created:

`src/agents/result_formatter.py`

Implemented the function:

`format_query_results(columns, rows)`

The function:
- Receives database column names and query rows.
- Formats each returned record into a numbered line.
- Preserves the original order of database rows.
- Includes all rows received by the formatter.
- Uses the database column names as output labels.

The formatter was tested using five customer records. The output preserved all five records and their original order.

### 3. Analysis Agent Update

Updated:

`src/agents/analysis_agent.py`

The Analysis Agent now uses the following logic:

- Empty query results produce a deterministic no-results message.
- Results containing multiple rows or multiple columns are formatted using Python.
- Single-row, single-column results continue to use the LLM to generate a natural-language answer.

This separates deterministic structured-result formatting from LLM-based language generation.

### 4. System C Orchestrator Update

Updated:

`src/agents/orchestrator_c.py`

The orchestrator now passes three arguments to the Analysis Agent:

- User question
- Database query results
- Database column names

The System C orchestrator was tested with a simple customer-count question.

Observed result:

- SQL execution successful.
- Semantic validation successful.
- Final answer: 30 customers are in the database.
- Recovery attempts: 0.

A second test used the Question 10 customer-ranking benchmark.

The formatter correctly preserved all five customers:

1. Rohan Mehta — 6 orders
2. Aditya Verma — 5 orders
3. Arjun Nair — 4 orders
4. Karan Sethi — 4 orders
5. Maya Fernandes — 4 orders

The original ranking and alphabetical tie-breaker were preserved.

### 5. System B Compatibility Update

The Analysis Agent interface had changed from two arguments to three arguments.

Updated:

`src/agents/orchestrator.py`

The System B orchestrator was modified to pass database column names to the Analysis Agent.

This maintained compatibility without introducing System C's recovery mechanism into System B.

The System B benchmark was rerun successfully.

### 6. System B Benchmark and Evaluation

Executed:

- `experiments/run_multi_agent.py`
- `experiments/evaluate_multi_agent.py`

Results:

| Metric | Result |
|---|---:|
| Total benchmark questions | 10 |
| Successful SQL executions | 10 |
| Failed SQL executions | 0 |
| Correct database answers | 10 |
| Execution success rate | 100% |
| Database answer correctness rate | 100% |

All ten benchmark questions passed the database-answer evaluation.

### 7. System C Benchmark and Evaluation

Executed:

- `experiments/run_system_c.py`
- `experiments/evaluate_system_c.py`

Results:

| Metric | Result |
|---|---:|
| Total benchmark questions | 10 |
| Successful SQL executions | 10 |
| Failed SQL executions | 0 |
| Correct database answers | 10 |
| Recovery attempts during benchmark | 0 |
| Execution success rate | 100% |
| Database answer correctness rate | 100% |

All ten benchmark questions passed the database-answer evaluation.

The benchmark did not require autonomous recovery because the generated SQL queries executed successfully and passed validation.

### 8. Natural-Language Answer Evaluation

The previous natural-language evaluator did not recognize the new Python formatter output.

Updated:

`experiments/evaluate_natural_language.py`

The extraction logic was modified to recognize the new structured format:

`1. customer_name: Rohan Mehta | order_count: 6`

The evaluator checks four criteria:

1. Factual accuracy.
2. Completeness.
3. Ordering.
4. Clarity.

Question 10 evaluation:

| Criterion | Score |
|---|---:|
| Factual accuracy | 1/1 |
| Completeness | 1/1 |
| Ordering | 1/1 |
| Clarity | 1/1 |
| **Total** | **4/4** |

Expected records: 5

Extracted records: 5

All five customer names and order counts matched the database rows, and their order was preserved.

### 9. Interpretation and Findings

The latest benchmark runs showed that System B and System C both achieved 100% database-answer correctness across the ten benchmark questions.

Therefore, these results do not demonstrate higher database correctness for System C compared with System B.

The main improvement demonstrated on Day 19 was the deterministic formatting of structured database results.

The Question 10 natural-language evaluation improved to 4/4 after the formatter was introduced and the evaluator was updated to recognize its output.

System C's autonomous recovery capability remains supported by the separate Day 15 fault-injection experiments, where it recovered from three tested SQL execution or validation failures.

### 10. Limitations

- The benchmark contains only ten questions.
- The database is synthetic.
- The latest benchmark results represent individual runs rather than repeated statistical experiments.
- Natural-language evaluation currently covers Question 10 only.
- The natural-language evaluator is format-specific and preliminary.
- The formatter preserves returned rows but does not independently verify whether the SQL query itself is semantically correct.
- If query results are truncated, the formatter does not currently communicate that limitation in its output.
- No conclusion about general reliability or statistical significance can be drawn from these results.

### 11. Next Steps

1. Improve the readability of formatted column labels and numerical values.
2. Extend natural-language answer evaluation to all ten benchmark questions.
3. Conduct repeated experiments under consistent conditions.
4. Compare latency and recovery overhead across Systems A, B and C.
5. Prepare for external validation using a public retail dataset.

**Day 19 status: Completed.**

## Day 20 — Natural-Language Answer Evaluation and Evaluator Testing

### Objective

Extend the natural-language answer evaluation framework to evaluate all ten benchmark questions and test whether the evaluator can identify deliberately introduced answer errors.

### 1. Evaluation Across All Ten Benchmark Questions

Updated `experiments/evaluate_natural_language.py` to evaluate all ten results stored in `results/multi_agent_system_c.json`.

The evaluator assesses four criteria:

1. **Factual Accuracy:** Checks whether extracted answer records match the database rows returned by the system.
2. **Completeness:** Checks whether all expected records are present, including duplicate handling.
3. **Ordering:** Checks whether the extracted records preserve the order of the returned database rows.
4. **Clarity:** Checks whether the answer follows the expected output format.

Each criterion receives a binary score (1 = pass, 0 = fail), giving a maximum of four points per question and forty points overall.

### 2. Initial Evaluation Results

The evaluator was executed against all ten System C benchmark results.

- Questions evaluated: 10
- Total score: 40/40
- Overall score: 100%

All ten answers passed the four implemented evaluation checks.

These results indicate that the saved answers preserved the returned database records and their ordering under the current evaluation rules. They do not independently establish that every generated SQL query correctly interpreted its original natural-language question.

### 3. Controlled Evaluator Testing

Created `tests/test_natural_language_evaluation.py` to test the evaluator using deliberately modified answers.

Eight test cases were implemented:

1. Correct answer — all four criteria passed.
2. Incorrect customer name — factual accuracy, completeness and ordering failed.
3. Missing record — completeness and ordering failed.
4. Incorrect record ordering — ordering failed.
5. Incorrect numbering — clarity failed while the underlying records remained correct.
6. Duplicate record — completeness and ordering failed.
7. Empty answer — all four criteria failed.
8. Incorrect numerical answer — factual accuracy, completeness and ordering failed.

Final test execution:

- Tests run: 8
- Tests passed: 8
- Tests failed: 0

### 4. Files Created or Updated

- Updated `experiments/evaluate_natural_language.py`
- Created `tests/test_natural_language_evaluation.py`

### 5. Observations and Limitations

- The evaluator successfully identified the eight deliberately introduced error conditions.
- The current factual accuracy check compares extracted answer records against the database rows returned by SQL execution.
- It does not independently establish whether the generated SQL correctly represents the original question.
- The ordering check evaluates fidelity to returned database row order. It does not independently verify every ordering requirement in the original question.
- The clarity check is based on expected formatting rules and is not a comprehensive assessment of natural-language readability.
- The initial 40/40 benchmark result is preliminary and should not be interpreted as proof of complete semantic correctness.
- Further validation with more diverse answer formats and benchmark questions is still necessary.

### Conclusion

Day 20 extended natural-language answer evaluation from a single-question check to all ten benchmark questions. The evaluator achieved 40/40 on the current System C results and passed all eight controlled unit tests.

This provides initial evidence that the evaluation framework can detect several common answer errors. Further work is required to independently evaluate SQL interpretation, semantic correctness and answer quality.

## Day 21 — Schema-Aware Semantic Validation and Full System C Recovery Testing

### Objective
Improve semantic SQL validation by providing the validator with the NovaRetail database schema and test whether System C can detect and recover from semantic errors through its complete orchestration workflow.

### 1. Schema-Aware Semantic Validator
Updated `src/agents/semantic_validation_agent.py` to import and include `DATABASE_SCHEMA` from `src/nl_to_sql.py` in the validation prompt.

The validator now receives:
- Original natural-language question.
- Generated SQL query.
- Database schema, including tables, columns and relationships.
- SQL query results.

The validation instructions were expanded to check table and column selection, joins, filters, calculations, aggregations, ordering and limits.

### 2. Independent Semantic Validation Tests
Executed the existing semantic validation test file.

Results:
- Correct customer-count query: VALID.
- Incorrect but executable product-count query: INVALID.
- Semantic SQL correction: successfully generated a query using the customers table.

The validator correctly identified that querying the products table did not answer a question about the number of customers.

### 3. System C Integration Test
Executed `src/agents/orchestrator_c.py`.

Results:
- SQL generation successful.
- SQL execution successful.
- Semantic validation passed.
- Final answer contained all five customers in the correct ranking order.
- Recovery attempts: 0.

This confirmed that the updated validator remained compatible with the complete System C workflow under normal successful execution.

### 4. Full Orchestrator Semantic Fault-Injection Experiment
Updated the output filename in `experiments/fault_injection_test.py` to preserve the earlier experiment results.

Injected the same incorrect but executable SQL query into both systems:

`SELECT COUNT(*) FROM products`

Original question:

"How many customers are in the database?"

Results:

**System B — Without Recovery**
- SQL execution succeeded.
- No execution error was reported.
- The query counted products instead of customers.
- System B did not detect the semantic error.

**System C — With Recovery**
- SQL execution initially succeeded.
- Semantic validation detected the mismatch.
- The correction mechanism regenerated the SQL using the customers table.
- The corrected query executed successfully.
- Final answer: 30 customers.
- Recovery attempts: 1.

The experiment results were saved to:

`results/fault_injection_experiment_4_schema_aware.json`

### 5. Findings
The controlled experiment demonstrated that SQL execution success alone is insufficient to establish that a query answers the original natural-language question.

System C successfully detected and recovered from the injected semantic error, whereas System B returned a successful execution without detecting that the query addressed the wrong table.

### 6. Limitations
- This semantic fault-injection experiment used one question and one deliberately incorrect query.
- The semantic validator relies on an LLM and may produce incorrect judgments.
- Additional semantic error types and repeated trials are required.
- These results do not establish general semantic validation accuracy.

### Day 21 Status
Completed: schema-aware semantic validation, independent tests, integration testing and full-orchestrator semantic fault-injection testing.

## Day 22 — Extended Semantic Fault Injection and Hybrid Validation

### 1. Objective

Evaluate whether System C can detect and recover from additional semantic SQL errors beyond incorrect table selection.

Three fault types were investigated:

1. Incorrect date filtering.
2. Incorrect aggregation.
3. Incorrect unit conversion.

The experiments compared System B (multi-agent system without autonomous recovery) and System C (multi-agent system with semantic error detection and bounded recovery).

### 2. Experiment 1 — Incorrect Date Filter

**Question:**

"How many orders were placed in March 2025?"

**Injected error:**

The SQL query used an April 2025 date range instead of March 2025.

**Results:**

- System B executed the incorrect query successfully without detecting the semantic error.
- System C detected the incorrect date range.
- System C regenerated the SQL using the correct March 2025 date range.
- The corrected query returned 5 orders.
- Recovery attempts: 1.

**Outcome:** System C successfully recovered from the incorrect date-filter error.

### 3. Experiment 2 — Incorrect Aggregation

**Question:**

"Show the average current price of products in each category, in rupees."

**Injected error:**

The SQL query used `SUM()` instead of `AVG()`.

**Initial observation:**

The LLM-only semantic validator incorrectly accepted the SUM query as valid. System C therefore failed to detect the error in the initial experiment.

**Improvement implemented:**

A deterministic validation rule was added to identify cases where the question requests an average but the SQL uses SUM instead of AVG.

The validator was then tested again.

**Final results:**

- System B executed the incorrect SUM query successfully.
- System C identified the aggregation mismatch.
- System C regenerated the SQL using AVG().
- The corrected query returned the average price for each category.
- Recovery attempts: 1.

**Outcome:** System C successfully recovered after the deterministic aggregation check was introduced.

### 4. Experiment 3 — Incorrect Unit Conversion

**Question:**

"Show the average current price of products in each category, in rupees."

**Injected error:**

The database stores prices in paise, but the SQL query calculated the average without dividing by 100.

**Initial observation:**

The LLM-only semantic validator failed to identify the missing unit conversion. System C accepted the query and returned values 100 times larger than the expected rupee values.

**Improvement implemented:**

A deterministic validation rule was added to check whether queries involving `current_price_paise` include division by 100 when the question requests prices in rupees.

**Validator test:**

The incorrect SQL was tested independently.

- Expected validation result: INVALID.
- Actual validation result: INVALID.
- Feedback correctly identified the missing conversion.

**Final results:**

- System B executed the incorrect SQL without detecting the error.
- System C detected the missing conversion.
- System C regenerated the SQL using `AVG(current_price_paise / 100.0)`.
- The corrected results were returned in rupees.
- Recovery attempts: 1.

**Outcome:** System C successfully recovered from the unit-conversion error after the deterministic validation rule was introduced.

### 5. Semantic Validator Testing

Updated `experiments/test_semantic_validation.py` with a fifth test covering incorrect unit conversion.

The test suite covered:

1. Correct SQL validation.
2. Incorrect table detection.
3. Semantic SQL correction.
4. Incorrect aggregation detection.
5. Incorrect unit-conversion detection.

All five test sections executed successfully, with the unit-conversion test returning the expected INVALID result.

### 6. Key Findings

1. Successful SQL execution does not guarantee that a query answers the original natural-language question.
2. The initial LLM-only semantic validator failed to detect the tested aggregation and unit-conversion errors.
3. Targeted deterministic checks improved detection of these two error types.
4. System C successfully recovered from the tested wrong-date, wrong-aggregation and wrong-unit-conversion errors.
5. The hybrid validation approach combines deterministic checks with LLM-based semantic judgment.
6. Autonomous recovery requires both successful error detection and successful SQL regeneration.

### 7. Limitations

- Each fault-injection scenario was tested in a limited number of individual trials.
- The experiments use the synthetic NovaRetail database.
- The deterministic checks currently cover specific patterns and are not a comprehensive SQL semantic analysis system.
- The aggregation rule currently focuses on average-versus-sum mismatches.
- The unit-conversion rule focuses on `current_price_paise` and questions containing the term "rupees".
- The LLM validator may still miss other semantic errors.
- Repeated trials and evaluation using an external public dataset remain necessary.
- The current results do not establish general reliability or statistical significance.

### 8. Outcome

Day 22 extended the controlled fault-injection evaluation of System C.

The system successfully detected and recovered from three additional semantic error types after introducing targeted deterministic validation rules.

The experiments also demonstrated a limitation of relying exclusively on LLM-based semantic validation and provided practical evidence supporting the hybrid validation approach.

These findings are preliminary and require broader testing and repeated experimental trials.

## Day 23 — Repeated Fault-Injection Experiment

**Date:** 16 November 2026

### 1. Objective

Evaluate whether the reliability-aware multi-agent system (System C) can detect and recover from injected SQL errors across repeated trials. Compare its performance against System B, which does not implement autonomous recovery.

### 2. Experimental Setup

- Systems compared:
  - System B: Multi-agent system without autonomous recovery.
  - System C: Multi-agent system with error detection and autonomous recovery.
- Number of fault scenarios: 4
- Trials per scenario: 5
- Total trials: 20
- Database: NovaRetail SQLite database.
- LLM: Qwen2.5 7B through Ollama.
- Maximum recovery attempts: 2.

### 3. Fault Scenarios

1. Wrong database table.
2. Wrong date filter.
3. Wrong aggregation function.
4. Missing unit conversion from paise to rupees.

### 4. Experimental Results

| Scenario | System B Correct | System C Correct |
|---|---:|---:|
| Wrong database table | 0/5 | 5/5 |
| Wrong date filter | 0/5 | 5/5 |
| Wrong aggregation | 0/5 | 5/5 |
| Missing unit conversion | 0/5 | 5/5 |
| **Total** | **0/20** | **20/20** |

All 20 trials completed successfully at the execution level for both systems.

### 5. Latency Results

| Scenario | System B Average | System C Average |
|---|---:|---:|
| Wrong database table | 0.4015 s | 3.1931 s |
| Wrong date filter | 0.0744 s | 5.7488 s |
| Wrong aggregation | 0.0009 s | 1.3882 s |
| Missing unit conversion | 0.0008 s | 1.5711 s |
| **Overall average** | **0.1194 s** | **2.9753 s** |

System C required an average of one recovery attempt per trial, for a total of 20 recovery attempts.

### 6. SQL Validation

Representative recovered SQL queries from System C were manually inspected for all four scenarios.

The inspection confirmed that:
- The incorrect products table was replaced with the customers table.
- The incorrect April date range was corrected to March 2025.
- The SUM aggregation was replaced with AVG.
- The missing paise-to-rupees conversion was corrected.

The recovered queries produced results matching the independently calculated expected results.

### 7. Interpretation

System B successfully executed its SQL queries but failed the strict correctness checks in all 20 trials. This demonstrates that successful SQL execution alone does not guarantee a correct analytical answer.

System C achieved 20 correct outcomes out of 20 trials in this experiment. It recovered from all four injected fault types using one recovery attempt per trial.

However, System C introduced additional computational latency. Its overall average latency was approximately 2.9753 seconds, compared with 0.1194 seconds for System B.

This represents a trade-off between reliability and response time.

### 8. Limitations

- Only four predefined fault scenarios were evaluated.
- Each scenario was repeated five times.
- The semantic SQL validation uses scenario-specific heuristic checks rather than a general SQL semantic evaluator.
- Manual inspection was performed on representative recovered queries.
- The experiment uses a synthetic database and does not establish general performance across real-world databases.
- The latency results are specific to the local hardware and model configuration.

### 9. Conclusion

The repeated fault-injection experiment provides preliminary evidence that autonomous error detection and recovery can improve the correctness of natural-language database analysis under the tested fault conditions.

System C achieved 100% strict correctness across the 20 trials, while System B achieved 0%. This improvement came with increased latency.

Further experiments using a larger benchmark, additional fault types, and external datasets are required to establish the generalizability of these findings.

### 10. Results File

`results/repeated_fault_injection_20261116_172549.json`


## Day 24 — External Dataset Benchmark Verification

### Objective

Develop and verify an independent SQL benchmark using the public UCI Online Retail dataset to evaluate the reliability of the proposed natural-language database analysis systems beyond the synthetic NovaRetail database.

### Dataset

- Dataset: UCI Online Retail
- Database: `data/online_retail.db`
- Original records: 541,909
- Columns: 8
- Unique invoices: 25,900
- Unique non-null CustomerIDs: 4,372
- Unique countries: 38
- Unique product codes: 4,070

The original dataset was preserved. Missing CustomerID values, cancellation records, returns, and other records were not deleted.

### Benchmark Design

Created the external benchmark in:

`experiments/online_retail_benchmark.py`

The benchmark contains 10 natural-language questions:

- Easy: Questions 1–4
- Medium: Questions 5–8
- Hard: Questions 9–10

The questions cover:
- Distinct invoice counts
- Country counts
- Missing customer identifiers
- Cancellation records
- Return records
- Country-level record counts and ranking
- Monthly record counts
- Transaction classification
- Monthly record distribution
- Distinct product codes

Each question includes reference SQL and independently established expected results.

### Reference SQL Verification

Created:

`experiments/verify_online_retail_benchmark.py`

The verification script executes every reference SQL query against `online_retail.db` and compares the actual returned rows with the expected rows.

**Results:**

| Metric | Result |
|---|---:|
| Total benchmark questions | 10 |
| Passed | 10 |
| Failed | 0 |
| Verification success rate | 100% |

All 10 reference SQL queries returned results matching their expected outputs.

The script completed successfully with exit code 0.

### Interpretation

The external benchmark and its reference SQL queries are now verified against the actual SQLite database.

This establishes a reference evaluation set for comparing Systems A, B, and C on an external dataset.

However, this result does not demonstrate that the LLM agents can answer these questions correctly. That must be established through separate agent evaluation experiments.

### Limitations

- The benchmark currently contains only 10 questions.
- The questions primarily test structured SQL retrieval and aggregation.
- The benchmark does not yet measure natural-language answer correctness.
- Agent performance, recovery effectiveness, latency, and computational overhead on the external dataset remain to be evaluated.

### Conclusion

External dataset preparation and reference benchmark verification are complete. All 10 benchmark questions passed verification. The next phase is adapting the existing agent architecture to support the Online Retail database while preserving the NovaRetail configuration.

### Day 24 — System C External Dataset Benchmark

**Objective:**

Evaluate System C using the UCI Online Retail dataset to assess its ability to answer natural-language database questions beyond the synthetic NovaRetail database.

**Experiment Setup:**

- Dataset: UCI Online Retail
- Database: `data/online_retail.db`
- Benchmark questions: 10
- System evaluated: System C (Multi-Agent System with Error Detection and Autonomous Recovery)
- LLM: Qwen2.5 7B (local Ollama)

**Results:**

| Metric | Result |
|---|---:|
| Total questions | 10 |
| Successful SQL executions | 10/10 |
| Correct answers | 10/10 |
| Execution success rate | 100% |
| Answer accuracy | 100% |
| Total recovery attempts | 0 |
| Average latency | 2.9182 seconds |

**Question-Level Results:**

All ten benchmark questions were answered correctly. The questions covered:

1. Counting distinct invoices.
2. Counting distinct countries.
3. Identifying records with missing CustomerID values.
4. Counting cancellation invoice records.
5. Counting non-cancellation records with negative quantities.
6. Finding the five countries with the highest number of records.
7. Counting records from November 2011.
8. Classifying positive-quantity records, returns, and cancellations.
9. Identifying the month with the highest number of records.
10. Counting distinct product codes.

**Interpretation:**

System C successfully executed all ten benchmark questions and produced correct answers. No autonomous recovery attempts were required during this experiment. The results demonstrate that the system can operate with the external Online Retail database using configurable database paths and database schemas.

The average execution latency was approximately 2.92 seconds per question.

**Limitations:**

This was an initial evaluation using a benchmark of ten questions and a single run. The results do not establish general accuracy across larger or more diverse datasets. Question 8 was evaluated using a semantic comparison of labelled aggregate columns rather than requiring an identical output-row format to the reference SQL. Furthermore, this experiment evaluated normal operation and did not test autonomous recovery under injected faults.

**Conclusion:**

System C achieved 100% answer accuracy on the initial ten-question Online Retail benchmark. This provides preliminary evidence of successful external-dataset integration and natural-language query handling. Further comparative experiments with System B and repeated trials are required to evaluate the reliability improvements and computational overhead introduced by autonomous recovery.

**Results File:**

`results/online_retail_system_c_20261117_022105.json`

### Day 25 — System B External Dataset Benchmark

**Objective:**

Evaluate System B on the UCI Online Retail dataset using the same ten-question benchmark previously used to evaluate System C.

**Experiment Setup:**
- Dataset: UCI Online Retail
- Database: `data/online_retail.db`
- Benchmark questions: 10
- System: System B (Multi-Agent System without Autonomous Recovery)
- LLM: Qwen2.5 7B through local Ollama

**Results:**

| Metric | Result |
|---|---:|
| Total questions | 10 |
| Successful SQL executions | 10/10 |
| Correct answers | 10/10 |
| Execution success rate | 100% |
| Answer accuracy | 100% |
| Recovery attempts | 0 |
| Average latency | 1.6662 seconds |

**Interpretation:**

System B successfully executed all ten benchmark questions and produced correct answers. No recovery attempts were required.

Compared with System C, which achieved the same 100% accuracy with an average latency of 2.9182 seconds, System B was faster by approximately 1.252 seconds per question.

System C's additional semantic validation and recovery mechanisms may contribute to its higher latency.

**Limitations:**

This was a single evaluation run using ten predefined questions. The results do not establish performance variability or general accuracy across larger datasets. Since no failures occurred, this experiment does not directly measure autonomous recovery effectiveness.

**Conclusion:**

System B demonstrated successful natural-language database analysis on the external Online Retail dataset. Both Systems B and C achieved 100% accuracy in this initial normal-operation benchmark, while System B had lower average latency. Further repeated experiments and fault-injection tests are necessary to evaluate reliability differences.

**Results File:**

`results/online_retail_system_b_20261117_120718.json`

### Day 26 — Repeated Online Retail Benchmark: System B

**Objective:**

Evaluate the consistency of System B by repeating the ten-question Online Retail benchmark five times.

**Experimental Configuration:**
- Dataset: UCI Online Retail
- System: System B
- Repetitions: 5
- Questions per repetition: 10
- Total evaluations: 50
- Recovery mechanism: Not enabled
- Semantic validation: Not enabled

**Results:**

| Metric | Result |
|---|---:|
| Total evaluations | 50 |
| Successful executions | 50 |
| Correct answers | 50 |
| Execution success rate | 100% |
| Answer accuracy | 100% |
| Average latency | 1.6714 seconds |
| Minimum individual latency | 0.9402 seconds |
| Maximum individual latency | 2.9930 seconds |

All five repetitions achieved 10/10 successful executions and 10/10 correct answers.

**Interpretation:**

System B demonstrated consistent performance across the five repeated benchmark runs. Its overall average latency was 1.6714 seconds, close to the initial single-run average of 1.6662 seconds.

No execution failures or incorrect benchmark answers were observed.

**Limitations:**

The experiment uses five repetitions of ten predefined questions on one external dataset. It does not establish general reliability across unseen questions or other databases. The results also do not measure recovery effectiveness because System B does not implement autonomous recovery.

**Results File:**

`results/repeated_online_retail_system_b_20261117_121309.json`

**Conclusion:**

System B achieved 100% answer accuracy across 50 benchmark evaluations. These results provide an initial indication of repeatability under the tested conditions. System C must undergo the same repeated evaluation before a fair comparison can be made.

### Day 26 — Repeated Online Retail Benchmark: System C and Comparative Analysis

**Objective:**

Evaluate System C across five repetitions of the ten-question Online Retail benchmark and compare its normal-operation performance with System B.

**Experimental Configuration:**
- Dataset: UCI Online Retail
- Questions per repetition: 10
- Repetitions per system: 5
- Total evaluations per system: 50
- System B: Multi-agent without autonomous recovery
- System C: Multi-agent with autonomous error detection and recovery

**System C Results:**

| Metric | Result |
|---|---:|
| Total evaluations | 50 |
| Successful executions | 50 |
| Correct answers | 50 |
| Execution success rate | 100% |
| Answer accuracy | 100% |
| Recovery attempts | 0 |
| Average latency | 3.1534 seconds |
| Minimum individual latency | 2.0827 seconds |
| Maximum individual latency | 5.7838 seconds |

**Comparative Results:**

| Metric | System B | System C |
|---|---:|---:|
| Evaluations | 50 | 50 |
| Correct answers | 50 | 50 |
| Answer accuracy | 100% | 100% |
| Recovery attempts | 0 | 0 |
| Average latency | 1.6714 s | 3.1534 s |

System C's average latency was approximately 1.482 seconds higher than System B, representing an 88.7% increase relative to System B.

**Interpretation:**

Both systems achieved identical answer accuracy during normal operation. System C had higher latency, potentially reflecting the additional processing associated with its validation and recovery architecture.

No recovery attempts were triggered in System C during these 50 evaluations. Therefore, this experiment measures normal-operation performance rather than recovery effectiveness.

**Limitations:**

- Only ten predefined benchmark questions were evaluated.
- Each system was tested five times.
- Both systems were evaluated on the same external dataset.
- Results do not establish generalization to unseen questions or other databases.
- The experiment does not directly measure the effectiveness of autonomous recovery because no recovery was triggered.

**Conclusion:**

Both systems demonstrated consistent performance on the tested benchmark. System B was faster, while System C incurred additional latency without an accuracy improvement during normal operation. The reliability benefit of System C must therefore be assessed through controlled fault-injection experiments.

**Results Files:**

System B:
`results/repeated_online_retail_system_b_20261117_121309.json`

System C:
`results/repeated_online_retail_system_c_20261117_121822.json`

## Day 27 — Improved Semantic Validation and Online Retail Fault-Injection Experiment (System C V2)

### Objective

Evaluate whether the improved semantic validation agent (System C V2) can detect and recover from semantic SQL errors that System C V1 previously failed to identify.

### Implementation

A new semantic validation agent was created:

- `src/agents/semantic_validation_agent_v2.py`

A separate orchestrator was implemented:

- `src/agents/orchestrator_c_v2.py`

System C V2 introduces deterministic checks for:
- Incorrect aggregation (average versus sum).
- Missing currency conversion (paise to rupees).
- Incorrect date filters.
- Incorrect transaction filters, particularly cancellation exclusion.
- Incorrect sorting direction.

The existing System B and System C V1 implementations were preserved.

### Preliminary validator tests

Five targeted validation tests were conducted:

| Test | Expected behaviour | Result |
|---|---|---|
| Wrong aggregation | Reject | Passed |
| Missing currency conversion | Reject | Passed |
| Wrong sorting | Reject | Passed |
| Correct November date filter | Accept | Passed |
| Correct cancellation exclusion | Accept | Passed |

All five tests passed.

### Fault-Injection Experiment

The experiment used the UCI Online Retail dataset containing 541,909 records.

Configuration:
- Systems compared: System B and System C V2.
- Four fault scenarios.
- Five trials per scenario.
- 20 trials per system.
- Total: 40 system executions.

The four injected faults were:

1. **Wrong database table:** SQL referenced a non-existent `products` table instead of `online_retail`.
2. **Wrong date filter:** October 2011 was used instead of November 2011.
3. **Wrong sorting:** Countries were sorted in ascending rather than descending record-count order.
4. **Wrong transaction filter:** Negative quantities were counted without excluding cancellation records.

### Results

| Fault scenario | System B correct | System C V2 correct |
|---|---:|---:|
| Wrong database table | 0/5 | 5/5 |
| Wrong date filter | 0/5 | 5/5 |
| Wrong sorting | 0/5 | 5/5 |
| Wrong transaction filter | 0/5 | 5/5 |
| **Total** | **0/20** | **20/20** |

### Execution and Recovery Results

| Metric | System B | System C V2 |
|---|---:|---:|
| Total trials | 20 | 20 |
| Successful executions | 15 | 20 |
| Correct results | 0 | 20 |
| Execution success rate | 75% | 100% |
| Correctness rate | 0% | 100% |
| Recovery attempts | 0 | 25 |

System C V2 successfully recovered from all four fault types.

The date-filter scenario required two recovery attempts per trial. The other three scenarios required one recovery attempt per trial.

### Latency Results

| Fault scenario | System B average | System C V2 average |
|---|---:|---:|
| Wrong database table | 0.0006 s | 1.6705 s |
| Wrong date filter | 0.7397 s | 5.0461 s |
| Wrong sorting | 0.1102 s | 3.6559 s |
| Wrong transaction filter | 0.6576 s | 1.7440 s |

Across the four scenario averages:
- System B: approximately 0.377 seconds.
- System C V2: approximately 3.029 seconds.

The results indicate that semantic validation and recovery introduce additional computational latency.

### Comparison with System C V1

In the earlier Online Retail fault-injection experiment, System C V1 recovered from the wrong-table and wrong-sorting faults but failed to detect the wrong-date and wrong-transaction-filter faults.

System C V2 successfully detected and recovered from all four tested fault types.

This provides preliminary evidence that the improved deterministic semantic checks address two weaknesses observed in System C V1.

### Interpretation

Under the tested fault conditions, System C V2 achieved 100% correctness across 20 trials, compared with 0% correctness for System B.

The findings demonstrate the potential benefit of semantic validation and autonomous SQL recovery when a query executes successfully but produces an incorrect result.

However, System C V2 was slower than System B. This illustrates a reliability-versus-latency trade-off.

### Limitations

- Only four predefined fault types were evaluated.
- Each fault scenario was repeated five times.
- Correctness evaluation used expected database results and scenario-specific SQL checks.
- The experiment used the UCI Online Retail dataset and does not establish general reliability across arbitrary databases or natural-language questions.
- The results should be interpreted as preliminary experimental evidence, not proof of universal semantic correctness.

### Result File

`results/repeated_online_retail_fault_injection_20261117_095005.json`

### Conclusion

System C V2 improved fault detection and recovery compared with System C V1 in the tested Online Retail scenarios. It successfully recovered from all 20 injected faults, while System B produced no correct results under the same fault conditions. The improvement comes with additional latency

# Day 28 — Expanded Repeated Fault-Injection Experiment (20 Trials per Scenario)

## 1. Objective

The objective of this experiment was to increase the number of repetitions in the Online Retail fault-injection evaluation from 5 to 20 trials per scenario. This was done to obtain a larger set of observations and examine whether the reliability improvements observed in the initial experiment remained consistent across repeated trials.

The experiment compared:

- **System B:** Multi-agent pipeline without semantic validation or autonomous recovery.
- **System C V2:** Multi-agent pipeline with improved semantic validation and autonomous error detection and recovery.

## 2. Experimental Configuration

- Dataset: UCI Online Retail dataset.
- Database: `data/online_retail.db`.
- Number of fault scenarios: 4.
- Repetitions per scenario: 20.
- Trials per system: 80.
- Total system executions: 160.
- Maximum recovery attempts: 2 per trial.
- Results evaluated against independently verified benchmark answers.

The same predefined faulty SQL queries were injected into both systems to provide a controlled comparison.

## 3. Fault Scenarios

Four types of semantic and execution errors were evaluated:

1. **Wrong database table:** The SQL query referenced a non-existent `products` table instead of the `online_retail` table.
2. **Wrong date filter:** The query selected October 2011 instead of November 2011.
3. **Wrong sorting:** The query sorted country record counts in ascending rather than descending order.
4. **Wrong transaction filter:** The query counted all negative-quantity records without excluding cancellation invoices.

Each scenario was repeated 20 times for both systems.

## 4. Experimental Results

### 4.1 Overall Performance

| Metric | System B | System C V2 |
|---|---:|---:|
| Total trials | 80 | 80 |
| Successful executions | 60 | 80 |
| Correct results | 0 | 80 |
| Execution success rate | 75% | 100% |
| Correctness rate | 0% | 100% |
| Recovery attempts | 0 | 100 |

System B successfully executed 60 of the 80 injected queries. However, none of its outputs matched the expected benchmark results. The remaining 20 queries failed because they referenced a non-existent database table.

System C V2 successfully executed and recovered all 80 trials, producing results that matched the expected benchmark outputs.

### 4.2 Scenario-Level Results

| Fault scenario | System B correct | System C V2 correct |
|---|---:|---:|
| Wrong database table | 0/20 | 20/20 |
| Wrong date filter | 0/20 | 20/20 |
| Wrong sorting | 0/20 | 20/20 |
| Wrong transaction filter | 0/20 | 20/20 |
| **Total** | **0/80** | **80/80** |

System C V2 achieved 100% observed correctness across all four tested scenarios.

### 4.3 Recovery Behaviour

System C V2 performed 100 recovery attempts across the 80 trials.

| Fault scenario | Recovery attempts |
|---|---:|
| Wrong database table | 20 |
| Wrong date filter | 40 |
| Wrong sorting | 20 |
| Wrong transaction filter | 20 |
| **Total** | **100** |

The wrong-date scenario required two recovery attempts in every trial. The first regenerated query used an overly broad date interval ending on 1 January 2012. The deterministic validator rejected this query because the requested November interval should end on 1 December 2011. The second correction used the expected date boundaries and passed validation.

This behaviour demonstrates that the recovery mechanism can detect and correct semantic errors, but also reveals an opportunity to improve the date validator and reduce unnecessary recovery attempts.

## 5. Latency Analysis

Average latency was calculated separately for each fault scenario.

| Fault scenario | System B | System C V2 |
|---|---:|---:|
| Wrong database table | 0.0005 s | 1.1958 s |
| Wrong date filter | 0.7006 s | 4.9205 s |
| Wrong sorting | 0.1094 s | 4.2562 s |
| Wrong transaction filter | 0.8555 s | 2.2317 s |
| **Average of scenario averages** | **0.4165 s** | **3.1511 s** |

System C V2 required approximately 7.56 times the average latency of System B in this fault-injection experiment.

This additional latency is associated with semantic validation, error detection, SQL regeneration, and repeated execution. The results demonstrate a trade-off between reliability and computational efficiency.

## 6. Interpretation

The expanded experiment provides additional evidence that System C V2 can improve the reliability of natural-language database analysis under the four predefined fault conditions.

The most important observations are:

- System B did not autonomously correct any of the injected errors.
- System C V2 successfully recovered from all four fault types.
- The improved validator detected date-filter and transaction-filter errors that the earlier V1 validator had missed in the initial experiment.
- The recovery mechanism successfully handled both SQL execution failures and queries that executed successfully but produced semantically incorrect results.
- The additional validation and recovery stages introduced measurable latency overhead.

Increasing the repetitions from five to twenty per scenario produced consistent results for the tested fault conditions.

## 7. Limitations

The results should be interpreted within the scope of the experimental design.

1. Only four predefined fault types were evaluated.
2. The same injected faulty SQL was repeated across trials; these were not 80 independently generated errors.
3. Correctness evaluation used independently verified expected database results and scenario-specific SQL correctness checks.
4. The experiment used one external dataset, the UCI Online Retail dataset.
5. The observed 100% correctness rate does not establish universal reliability or guarantee performance on arbitrary queries and errors.
6. Latency measurements are dependent on the local execution environment and model runtime.
7. The date validator's rigid boundary checks caused additional recovery attempts, indicating that further refinement is needed.

## 8. Conclusion

The 20-repetition fault-injection experiment strengthens the preliminary evidence supporting the reliability benefits of the proposed System C V2 architecture.

System C V2 achieved 80 correct results out of 80 trials, compared with zero correct results from System B. However, this improvement came with a substantial latency overhead.

These findings suggest that autonomous semantic validation and recovery can improve the reliability of natural-language database analysis under the tested fault conditions. Further experiments are required to evaluate generalisation, false-positive validation, additional error categories, and computational efficiency.

## 9. Result File

The experiment output was saved as:

`results/repeated_online_retail_fault_injection_20261117_201427.json`

**Execution status:** Completed successfully (exit code 0).

# Day 29 — Expanded Semantic Fault-Injection Experiment

## 1. Objective

The objective of Day 29 was to evaluate whether the improved semantic validation and autonomous recovery mechanism in System C V2 could identify and correct SQL queries that execute successfully but produce semantically incorrect results.

The experiment expanded the previous fault-injection evaluation by testing four different semantic fault scenarios, with 20 repetitions per scenario.

The experiment compared:

- **System B:** Multi-agent pipeline without semantic validation or autonomous recovery.
- **System C V2:** Multi-agent pipeline with improved semantic validation, semantic error detection, and bounded SQL recovery.

The primary focus was on measuring correctness, execution success, recovery behaviour, and latency.

## 2. Experimental Configuration

- Dataset: UCI Online Retail dataset.
- Database: `data/online_retail.db`.
- Number of fault scenarios: 4.
- Repetitions per scenario: 20.
- Trials per system: 80.
- Total system executions: 160.
- Maximum recovery attempts: 2 per trial.
- Evaluation: Comparison against independently verified expected results and scenario-specific SQL correctness checks.

The same predefined faulty SQL queries were injected into both systems to maintain a controlled experimental comparison.

## 3. Fault Scenarios

Four semantic fault scenarios were selected.

1. **Incorrect NULL Handling:** The query used `CustomerID = NULL` instead of `CustomerID IS NULL`. This tests whether the system can identify incorrect SQL NULL comparison logic. The expected result was 135,080 records.

2. **Incorrect Invoice Counting:** The query used `COUNT(*)` instead of `COUNT(DISTINCT InvoiceNo)`. This tests the difference between counting individual records and counting unique invoices. The expected result was 25,900 distinct invoices.

3. **Incorrect Monthly Grouping:** The query grouped records by year instead of year and month. This tests whether the system can identify an incorrect time-grouping strategy. The expected result was 12 year-month groups.

4. **Incorrect Product Counting:** The query used `COUNT(*)` instead of `COUNT(DISTINCT StockCode)`. This tests the difference between counting transaction records and counting unique products. The expected result was 4,070 distinct products.

Each fault scenario was repeated 20 times for both systems.

## 4. Experimental Results

### 4.1 Overall Performance

| Metric | System B | System C V2 |
|---|---:|---:|
| Total trials | 80 | 80 |
| Successful SQL executions | 80 | 80 |
| Correct results | 0 | 71 |
| Execution success rate | 100% | 100% |
| Correctness rate | 0% | 88.75% |
| Recovery attempts | 0 | 89 |

Both systems successfully executed all 80 SQL queries. However, successful execution did not guarantee semantic correctness.

System B executed all injected queries but produced no results matching the expected benchmark answers.

System C V2 achieved 71 correct results out of 80 trials, corresponding to an observed correctness rate of 88.75%.

This demonstrates the importance of evaluating the semantic correctness of query results rather than relying only on SQL execution success.

### 4.2 Scenario-Level Results

| Fault scenario | System B correct | System C V2 correct |
|---|---:|---:|
| Incorrect NULL handling | 0/20 | 20/20 |
| Incorrect invoice counting | 0/20 | 20/20 |
| Incorrect monthly grouping | 0/20 | 11/20 |
| Incorrect product counting | 0/20 | 20/20 |
| **Total** | **0/80** | **71/80** |

System C V2 achieved 100% observed correctness in three of the four scenarios.

The monthly grouping scenario remained the main weakness, with 11 successful corrections out of 20 trials.

### 4.3 Recovery Behaviour

System C V2 performed a total of 89 recovery attempts across 80 trials.

| Fault scenario | Recovery attempts |
|---|---:|
| Incorrect NULL handling | 20 |
| Incorrect invoice counting | 20 |
| Incorrect monthly grouping | 29 |
| Incorrect product counting | 20 |
| **Total** | **89** |

The three scenarios with 100% correctness required 20 recovery attempts each.

The monthly grouping scenario required 29 recovery attempts but achieved only 11 correct results.

This indicates that the system attempted to recover from the monthly grouping fault, but the recovery mechanism was not consistently successful in producing the expected year-month grouping.

## 5. Latency Analysis

Average latency was calculated separately for each fault scenario.

| Fault scenario | System B | System C V2 |
|---|---:|---:|
| Incorrect NULL handling | 0.5688 s | 3.5137 s |
| Incorrect invoice counting | 0.3263 s | 3.2792 s |
| Incorrect monthly grouping | 0.1592 s | 13.5742 s |
| Incorrect product counting | 0.3964 s | 4.5149 s |
| **Average of scenario averages** | **0.3627 s** | **6.2205 s** |

System C V2 required approximately 17.1 times the average latency of System B.

The additional latency is associated with semantic validation, error detection, SQL regeneration, and repeated execution.

The monthly grouping scenario had the highest latency in System C V2, with an average of 13.5742 seconds. This is consistent with the additional recovery activity observed in that scenario.

These findings highlight the trade-off between semantic reliability and computational efficiency.

## 6. Comparison with Previous Experiments

The Day 29 experiment extends the earlier fault-injection evaluations.

The previous experiments demonstrated that System C V2 could recover from several predefined SQL faults, including incorrect table references, date filters, sorting, and transaction filters.

Day 29 introduced additional semantic fault types involving NULL handling, distinct counting, and time grouping.

The results show that the system successfully handled incorrect NULL comparisons, invoice counting, and product counting in all 20 repetitions per scenario.

However, monthly grouping remained a weakness.

This suggests that the current semantic validation approach is effective for certain predefined SQL correctness conditions but still requires improvement when validating more complex aggregation and temporal grouping logic.

## 7. Interpretation

The most important observations from this experiment are:

- Both systems achieved a 100% SQL execution success rate.
- System B produced no correct results under the injected semantic faults.
- System C V2 achieved 88.75% overall correctness.
- System C V2 successfully corrected all tested NULL handling, invoice counting, and product counting faults.
- Monthly grouping was the only scenario where System C V2 did not achieve 100% correctness.
- The system performed 89 recovery attempts across 80 trials.
- System C V2 introduced significant latency overhead compared with System B.

The results demonstrate that a query can execute without errors while still producing an incorrect analytical answer.

Therefore, execution-based validation alone is insufficient for reliable natural-language data analysis.

Semantic validation and autonomous recovery provide an additional reliability layer, although their effectiveness depends on the type of SQL error and the quality of the validation rules.

## 8. Limitations

The results should be interpreted within the scope of the experimental design.

1. Only four predefined semantic fault types were evaluated.
2. Each fault scenario was repeated 20 times using the same predefined faulty SQL query.
3. The 80 trials were not 80 independently generated semantic errors.
4. Correctness evaluation used independently verified expected database results and scenario-specific SQL correctness checks.
5. The experiment used one external dataset, the UCI Online Retail dataset.
6. The 88.75% observed correctness rate does not establish universal semantic reliability.
7. Latency measurements depend on the local execution environment and model runtime.
8. The monthly grouping scenario indicates that the current validation and recovery approach requires further refinement for temporal aggregation errors.

## 9. Conclusion

The Day 29 experiment provides further evidence that semantic validation and autonomous SQL recovery can improve the reliability of natural-language database analysis.

System C V2 achieved 71 correct results out of 80 trials, while System B produced zero correct results under the same injected semantic faults.

The system successfully handled three of the four tested fault categories, but its performance on monthly grouping errors remained limited.

The experiment also revealed a substantial latency trade-off, with System C V2 requiring approximately 17.1 times the average latency of System B.

Overall, the findings support the value of semantic validation and autonomous recovery while identifying temporal grouping and computational efficiency as areas requiring further investigation.

## 10. Result File

The experiment output was saved as:

`results/repeated_online_retail_fault_injection_20261117_210534.json`

**Execution status:** Completed successfully (exit code 0).

**Day 29 completed.**

**Next planned experiment — Day 30: Validator Robustness Evaluation.**

The next experiment will investigate two important failure types:

- **False acceptance:** The validator accepts an incorrect SQL query.
- **False rejection:** The validator rejects a correct SQL query.

This will help evaluate not only whether the validator can detect errors, but also whether it can distinguish incorrect queries from valid ones.

## Day 30 — Semantic Validator Robustness Evaluation

### Objective
Evaluate the robustness of System C V2's semantic validator by testing its ability to reject incorrect SQL queries and accept correct SQL queries across multiple validation categories.

### Test Design
Created `experiments/test_validator_robustness_day30.py` containing 12 predefined test cases covering:

1. Date filter validation
2. Cancellation-record exclusion
3. Sorting and ranking
4. Aggregation selection
5. Paise-to-rupees conversion

The LLM response was mocked to return `"VALID"` so that the tests isolated the deterministic validation rules rather than evaluating the LLM-based validation stage.

### Improvements Implemented
- Strengthened date validation to check inclusive start and exclusive end boundaries, including comparison operators.
- Added support for equivalent cancellation-exclusion logic using `SUBSTR(InvoiceNo, 1, 1) <> 'C'` and `!=`.
- Retained existing deterministic checks for aggregation, sorting, ranking, and currency conversion.

### Results

| Metric | Result |
|---|---:|
| Total test cases | 12 |
| Passed | 12 |
| Failed | 0 |
| Test agreement | 100% |

All 12 test cases passed. The validator correctly rejected the predefined incorrect SQL queries and accepted the predefined correct SQL queries.

### Interpretation
The results demonstrate improved deterministic validation coverage across the five tested categories. The date-boundary and cancellation-filter improvements resolved the two failures observed in the earlier robustness evaluation.

### Limitations
- The evaluation contains 12 predefined test cases and does not represent all possible SQL formulations.
- The LLM-based validation response was mocked; real LLM judgement was not evaluated.
- The results demonstrate agreement with the expected outcomes for these test cases, not universal semantic correctness.
- Further testing is required with more SQL variations, equivalent expressions, edge cases, and real LLM responses.

### Conclusion
The updated System C V2 deterministic validator passed all 12 robustness tests. This provides a stronger basis for the subsequent evaluation of autonomous error detection and recovery, while highlighting the need for broader testing.

## Day 31 — Extended Validator Edge Case Testing

### Objective

The objective of Day 31 was to extend the robustness testing of the System C V2 semantic validator. The tests focused on identifying additional cases where the validator might incorrectly accept invalid SQL or reject valid SQL.

### Test Design

A dedicated test script was created:

`experiments/test_validator_edge_cases_day31.py`

The test suite contained 12 predefined test cases covering:

1. Valid November date filtering using an inclusive final day.
2. Incorrect date filtering using an exclusive start boundary.
3. Cancellation exclusion using `NOT LIKE`.
4. Equivalent cancellation exclusion using `SUBSTR` and `!=`.
5. Incorrect cancellation filtering.
6. Missing `LIMIT` when the question requests the top five results.
7. Correct sorting when requesting the lowest five results.
8. Correct average calculation using `AVG`.
9. Correct total quantity calculation using `SUM`.
10. Incorrect distinct invoice counting using `COUNT(*)`.
11. Equivalent paise-to-rupees conversion using multiplication by `0.01`.
12. Incorrect currency conversion using division by `1000.0`.

### Improvements Implemented

The following improvements were made to the validator:

- Added a deterministic check for questions requesting distinct or unique invoice counts. The validator now requires `COUNT(DISTINCT InvoiceNo)` in these cases.
- Improved currency conversion validation to recognize multiplication by `0.01` as an equivalent conversion to division by `100`.
- Corrected the sorting validation pattern so numeric top-N and bottom-N requests are recognized correctly.
- Retained the existing checks for date boundaries, cancellation filtering, aggregation and sorting.

### Results

| Metric | Result |
|---|---:|
| Total test cases | 12 |
| Passed | 12 |
| Failed | 0 |
| Test agreement | 100% |

All 12 predefined test cases passed after the improvements.

### Interpretation

The results demonstrate that the deterministic validation layer successfully handled the specific edge cases represented in this test suite. In particular, it correctly identified an incorrect distinct-invoice count and recognized equivalent SQL expressions for cancellation filtering and currency conversion.

The results provide additional evidence that the validator's rule-based checks can detect several categories of predefined SQL errors.

### Limitations

- The evaluation contained 12 predefined test cases and does not represent exhaustive SQL validation.
- The LLM response was mocked as `VALID` to isolate the deterministic validation rules. Therefore, this experiment did not evaluate the real LLM judge.
- The checks rely on predefined SQL patterns and are not a general-purpose SQL semantic parser.
- Passing these tests does not establish 100% semantic-validation accuracy on unseen queries.

### Conclusion

Day 31 extended the validator's edge-case coverage from the previous robustness evaluation. The final test run achieved 12 out of 12 expected outcomes, with no failed cases. The results support continued testing of the deterministic validation layer while highlighting the need for broader testing with unseen SQL queries and real LLM responses.

## Day 32 — Unseen SQL Formulation Testing

### Objective
Evaluate whether the improved semantic validation agent (System C V2) can recognize alternative SQL formulations and detect incorrect SQL patterns that were not included in the earlier validator test cases.

### Implementation
Created and executed:

`experiments/test_validator_unseen_sql_day32.py`

The test suite contained eight cases covering:

1. November date filtering using `DATE()` and `BETWEEN`.
2. November date filtering using `STRFTIME()`.
3. Cancellation exclusion using `NOT GLOB`.
4. Cancellation exclusion using `LEFT()` — rejected because SQLite does not normally provide LEFT() as a built-in function.
5. Top-five country ranking using an aggregate expression in `ORDER BY`.
6. Incorrect sorting when the question requests the lowest five countries.
7. Correct distinct customer counting using `COUNT(DISTINCT CustomerID)`.
8. Incorrect distinct customer counting using `COUNT(*)`.

### Validator Improvements
Extended `validate_date_filter()` to recognize additional date-filtering formulations, including `STRFTIME('%Y-%m', ...)` and valid monthly `BETWEEN` boundaries.

Extended `validate_transaction_filters()` to recognize cancellation exclusion using `NOT GLOB`.

Extended `validate_aggregation()` to verify that questions requesting distinct customer counts use `COUNT(DISTINCT CustomerID)`.

### Results

| Metric | Result |
|---|---:|
| Total test cases | 8 |
| Passed | 8 |
| Failed | 0 |
| Test agreement | 100% |

All eight predefined test cases produced the expected validator decisions.

### Interpretation
The results indicate that System C V2's deterministic validation rules recognize several additional SQL formulations beyond those tested in earlier days.

The improvements extend coverage for date filtering, cancellation exclusion, sorting, and distinct customer aggregation.

### Limitations
- The evaluation contains only eight predefined test cases.
- The LLM response was mocked as `VALID`, isolating deterministic validation rules rather than evaluating the real LLM judge.
- SQL queries were not independently executed against the database during this test.
- The test suite does not establish general semantic-validation accuracy across arbitrary SQL formulations.
- SQLite-specific compatibility must be considered when evaluating alternative SQL syntax.

### Conclusion
Day 32 expanded the validator's tested SQL formulation coverage. All eight predefined cases passed, providing an additional controlled robustness check for System C V2.

## Day 33 — Executable SQL Equivalence Testing

### Objective
Evaluate whether System C V2 recognizes alternative SQL formulations that produce equivalent results when executed against the UCI Online Retail database.

Unlike previous validator-only tests, this experiment executed the SQL queries against the actual SQLite database and compared their returned results.

### Implementation
Created:

`experiments/test_sql_equivalence_day33.py`

The experiment evaluated four pairs of SQL formulations:

1. **Date filtering:** `DATE()` with `BETWEEN` compared with an inclusive start and exclusive end date boundary.
2. **Cancellation filtering:** `NOT GLOB` compared with `SUBSTR`.
3. **Country sorting:** `ORDER BY COUNT(*)` compared with ordering by an aggregate alias.
4. **Distinct customer counting:** `COUNT(DISTINCT CustomerID)` compared with a `COUNT(*)` over a `SELECT DISTINCT CustomerID` subquery.

Each query was executed against `data/online_retail.db`. Its actual results were then passed to System C V2 for semantic validation.

### Initial Results

All four query pairs executed successfully and returned equivalent database results.

However, System C V2 rejected the second distinct-customer formulation despite its result matching the first formulation.

Both queries returned 4,372 distinct customers.

The validator accepted 7 of 8 queries and rejected 1 equivalent formulation.

### Validator Improvement

Updated `validate_aggregation()` in:

`src/agents/semantic_validation_agent_v2.py`

The distinct-customer validation rule now recognizes two formulations:

- `COUNT(DISTINCT CustomerID)`
- `COUNT(*)` over a subquery beginning with `SELECT DISTINCT CustomerID`.

This addressed the false rejection observed during the initial experiment.

### Final Results

| Metric | Final result |
|---|---:|
| SQL query pairs | 4 |
| Equivalent query pairs | 4 |
| SQL execution failures | 0 |
| Validator acceptances | 8/8 |
| Validator rejections | 0 |
| SQL equivalence rate | 100% |

All four query pairs returned identical results.

### Regression Testing

After modifying the aggregation validator, reran:

`experiments/test_validator_unseen_sql_day32.py`

Results:

- Total test cases: 8
- Passed: 8
- Failed: 0
- Test agreement: 100%

The regression test confirmed that the validator continued to reject the incorrect distinct-customer count using `COUNT(*)` over the entire Online Retail table.

### Interpretation
The experiment demonstrated that equivalent SQL formulations can produce identical database results while differing syntactically.

The initial false rejection revealed that a strict requirement for one SQL formulation can incorrectly reject an alternative formulation that produces the correct result.

The improved validator recognizes the tested distinct-customer subquery formulation while preserving the tested incorrect-count rejection.

### Limitations
- Only four pairs of equivalent SQL formulations were evaluated.
- The experiment used one SQLite database and one public dataset.
- The LLM validation response was mocked as `VALID`, isolating deterministic validation rules.
- The equivalence evaluation covered the specific tested queries, not arbitrary SQL expressions.
- The distinct-customer subquery recognition uses a pattern-based rule and does not establish general equivalence detection.
- The experiment does not establish general semantic correctness across unrestricted SQL queries.

### Conclusion
Day 33 introduced executable SQL equivalence testing and identified a false rejection in System C V2.

After improving the distinct-customer validation rule, all four query pairs were accepted, all returned equivalent results, and all eight Day 32 regression tests passed.

## Day 34 — Complex SQL Equivalence and Validator Robustness Testing

### Objective

Evaluate whether the System C V2 semantic validator can recognize different SQL formulations that produce equivalent database results. The experiments focused on more complex SQL structures and alternative query-writing techniques using the UCI Online Retail dataset.

### Experimental Setup

- Dataset: UCI Online Retail SQLite database.
- Database table: `online_retail`.
- Validator: `semantic_validation_agent_v2.py`.
- LLM response: Mocked as `VALID` to isolate deterministic validation behaviour.
- SQL execution: Queries executed against the actual SQLite database.
- Four pairs of SQL formulations were evaluated.

### Experiment 1 — Nested Subquery vs Common Table Expression (CTE)

Compared two methods of calculating the number of distinct customers:

1. A nested subquery using `SELECT DISTINCT CustomerID`.
2. A Common Table Expression (CTE) followed by `COUNT(*)`.

Both queries returned 4,372.

Initially, the validator rejected the CTE formulation because its deterministic aggregation check did not recognize that particular CTE structure. The validator was extended to recognize the tested DISTINCT CTE pattern.

Final result:
- Both SQL queries executed successfully.
- Both returned identical results.
- Both were accepted by the validator.

### Experiment 2 — Conditional Aggregation vs WHERE Filtering

Compared two approaches to counting cancellation records:

1. Conditional aggregation using `SUM(CASE WHEN ...)`.
2. Direct filtering using `COUNT(*)` and a `WHERE` condition.

Both queries returned 9,288 cancellation records.

Final result:
- Both SQL queries executed successfully.
- Both returned identical results.
- Both were accepted by the validator.

### Experiment 3 — STRFTIME vs SUBSTR Date Extraction

Compared two methods of filtering records from November 2011:

1. Using SQLite `STRFTIME('%Y-%m', InvoiceDate)`.
2. Using `SUBSTR(InvoiceDate, 1, 7)`.

Both queries returned 84,711 records.

Initially, the validator rejected the SUBSTR formulation because it did not recognize this alternative date-filtering pattern. The date validation logic was extended to recognize the tested formulation.

Final result:
- Both SQL queries executed successfully.
- Both returned identical results.
- Both were accepted by the validator.

### Experiment 4 — NOT EXISTS vs NOT GLOB

Compared two approaches to counting return records while excluding cancellation invoices:

1. A correlated `NOT EXISTS` subquery checking cancellation invoice numbers.
2. A direct `InvoiceNo NOT GLOB 'C*'` condition.

Both queries returned 1,336 records.

Initially, the validator rejected the NOT EXISTS formulation because it did not recognize this alternative cancellation-exclusion pattern. The experiment was adjusted to make the cancellation condition explicit within the indexed temporary-table lookup.

Final result:
- Both SQL queries executed successfully.
- Both returned identical results.
- Both were accepted by the validator.

### Day 34 Results

| Metric | Result |
|---|---:|
| SQL equivalence pairs tested | 4 |
| Equivalent result pairs | 4 |
| SQL execution failures | 0 |
| Validator acceptances | 8/8 |
| Validator rejections | 0 |
| Final validator acceptance rate | 100% |

All four tested pairs produced equivalent database results, and all eight individual SQL formulations were accepted by the final validator.

### Regression Testing

After the Day 34 modifications, the earlier validator tests were rerun:

| Test | Result |
|---|---:|
| Day 30 — Validator robustness | 12/12 |
| Day 31 — Validator edge cases | 12/12 |
| Day 32 — Unseen SQL formulations | 8/8 |
| Day 33 — SQL equivalence | 4/4 equivalent pairs; 8/8 validator acceptances |

All four regression tests passed.

### Interpretation

The experiments demonstrate that the deterministic validation rules can recognize several alternative SQL formulations beyond the initial patterns implemented in the validator.

The results also revealed false rejections caused by overly restrictive pattern matching. These were addressed by extending the validator to recognize the specific tested CTE, date-extraction, and cancellation-exclusion formulations.

The findings suggest that supporting alternative SQL structures is important for reducing false rejections in semantic validation.

### Limitations

- Only four predefined SQL equivalence pairs were tested.
- All experiments used one SQLite database derived from the UCI Online Retail dataset.
- The LLM response was mocked as `VALID`; therefore, these experiments do not evaluate the real LLM judge's semantic accuracy.
- The deterministic checks remain pattern-based and do not establish general SQL equivalence.
- Identical results on the tested dataset do not prove equivalence for every possible database state or dataset.
- The temporary cancellation table was constructed specifically for the NOT EXISTS experiment.

### Conclusion

Day 34 successfully completed all four complex SQL equivalence experiments. The final validator accepted all eight tested SQL formulations, and all four pairs returned identical database results.

Regression testing for Days 30–33 also passed, indicating that the Day 34 changes did not break the previously tested validator behaviour.

These findings provide additional evidence of improved robustness across the tested SQL formulations, while broader validation remains necessary.


## Day 35 — False Acceptance Testing

### Objective

The objective of Day 35 was to evaluate whether System C V2's semantic validation component incorrectly accepts SQL queries that contain logical errors.

Previous experiments focused on whether the validator could recognize valid SQL formulations and reject predefined incorrect queries. This experiment specifically investigated false acceptances, where an incorrect SQL query is mistakenly classified as valid.

### Experimental Setup

- Dataset: UCI Online Retail dataset.
- Database: SQLite (`data/online_retail.db`).
- Validator: `semantic_validation_agent_v2.py`.
- Experiment script: `experiments/test_false_acceptance_day35.py`.
- LLM response: Mocked as "VALID" to isolate deterministic validation behaviour.
- Four predefined incorrect SQL scenarios were evaluated.
- SQL queries were executed against the database to inspect their actual results.

### Test Scenarios

Four categories of incorrect SQL queries were tested:

1. Wrong aggregation: Used `COUNT(*)` instead of `COUNT(DISTINCT InvoiceNo)` when the question requested distinct invoices.
2. Wrong date filtering: Retrieved October 2011 records instead of November 2011 records.
3. Incorrect transaction filtering: Counted negative-quantity records without excluding cancelled invoices.
4. Wrong sorting: Retrieved the five countries with the lowest record counts instead of the five highest.

### Initial Findings

The first two incorrect queries were correctly rejected.

The third test revealed a false acceptance. The validator accepted a query that did not exclude cancelled invoices.

Investigation identified two implementation issues:

- The question detector did not recognize the wording "excluding cancelled invoices".
- The experiment helper did not explicitly pass `ONLINE_RETAIL_DATABASE_SCHEMA` to the validator. Consequently, the Online Retail-specific transaction validation could be skipped.

### Corrective Changes

Two changes were implemented:

1. Extended the transaction-filter question detection logic to recognize additional expressions referring to cancelled invoices, including British and American spellings.
2. Updated the Day 35 experiment helper to explicitly pass `ONLINE_RETAIL_DATABASE_SCHEMA` to `semantic_validation_agent_v2()`.

After these changes, the incorrect transaction-filter query was correctly rejected.

### Final False Acceptance Results

| Test scenario | Expected decision | Final decision | Result |
|---|---|---|---|
| Wrong aggregation | Reject | Reject | Pass |
| Wrong date filtering | Reject | Reject | Pass |
| Missing cancellation exclusion | Reject | Reject | Pass |
| Wrong sorting | Reject | Reject | Pass |

- Total incorrect queries tested: 4
- Correctly rejected queries: 4
- False acceptances after correction: 0
- Rejection rate across tested cases: 100%

### Regression Testing

After implementing the corrective changes, five previous experiment suites were rerun to check for regressions.

| Experiment | Test cases / pairs | Result |
|---|---:|---|
| Day 30 — Validator Robustness | 12 tests | 12 passed |
| Day 31 — Validator Edge Cases | 12 tests | 12 passed |
| Day 32 — Unseen SQL Formulations | 8 tests | 8 passed |
| Day 33 — Executable SQL Equivalence | 4 equivalent pairs, 8 validator decisions | All passed |
| Day 34 — Complex SQL Equivalence | 4 equivalent pairs, 8 validator decisions | All passed |

All 48 previous regression test cases passed.

### Interpretation

The experiment demonstrated that the deterministic validation layer could identify four predefined categories of incorrect SQL queries after the corrective changes.

The initial false acceptance also demonstrated that question wording and database schema configuration directly affect whether the appropriate validation rules are activated.

The successful regression tests indicate that the changes did not break the previously tested validation rules or the tested equivalent SQL formulations.

### Limitations

- Only four predefined false-acceptance scenarios were evaluated.
- The LLM response was mocked as "VALID"; therefore, this experiment evaluates deterministic validation behaviour rather than the accuracy of the actual LLM judge.
- The SQL validation logic relies partly on predefined patterns and heuristic checks.
- The results do not establish general SQL semantic correctness or guarantee detection of all incorrect queries.
- Testing was conducted using one public dataset and one SQLite database.
- The regression results apply only to the predefined test cases.

### Conclusion

Day 35 identified and corrected a false-acceptance issue in the transaction-filter validation logic. Following the correction, all four predefined incorrect SQL queries were rejected, and all 48 previous regression test cases passed.

This strengthens the experimental evidence for the reliability of the deterministic validation component within the tested scenarios. Further evaluation with more diverse SQL formulations and independently generated incorrect queries remains necessary.

### Day 36 — Broader SQL Robustness and Performance Evaluation

**Broader SQL robustness testing**
- Evaluated eight predefined valid and invalid SQL cases.
- Tested STRFTIME date filtering, subqueries, correlated NOT EXISTS, CTE-based aggregation, cancellation filtering, sorting, and distinct counting.
- Result: 8/8 validator tests passed.
- SQL execution failures: 0.
- Validator test agreement: 100%.

**Repeated SQL performance comparison**

Compared three equivalent formulations for excluding cancelled invoices from negative-quantity records:

| SQL formulation | Median execution time | Correct result |
|---|---:|---|
| NOT EXISTS | 101.7488 seconds | Yes |
| NOT GLOB | 0.0157 seconds | Yes |
| SUBSTR | 0.0158 seconds | Yes |

- Five executions per formulation.
- All 15 executions returned 1,336.
- NOT GLOB had the lowest median execution time.

**Query plan inspection**
- NOT EXISTS produced an outer table scan and a correlated scalar subquery with an additional inner table scan.
- NOT GLOB and SUBSTR produced single table scans.
- The query plans support the observed performance difference for these tested queries.

**Limitations**
- Eight predefined validator cases, not exhaustive SQL validation.
- LLM response mocked as VALID to isolate deterministic checks.
- Performance results specific to the tested SQLite database and environment.
- Validator agreement is not equivalent to general semantic accuracy.

**Key finding:** Equivalent SQL formulations can have significantly different execution costs. Reliability evaluation should distinguish query correctness from execution efficiency.

## Day 37 — Unseen SQL Pattern Testing

### Objective
Evaluate whether System C V2 can recognise valid and invalid SQL formulations that were not explicitly covered in previous validator tests.

### Experiment
Created and executed `experiments/test_unseen_sql_patterns_day37.py` against the UCI Online Retail SQLite database.

Eight test cases were evaluated:

1. Valid November 2011 date filtering using separate STRFTIME year and month extraction with CAST.
2. Invalid December 2011 date filtering when November was requested.
3. Valid cancellation exclusion using NOT GLOB.
4. Missing cancellation exclusion.
5. Valid distinct invoice counting using a CTE.
6. Incorrect invoice counting using ordinary COUNT(*).
7. Valid distinct customer counting using a GROUP BY subquery.
8. Incorrect customer counting that includes duplicate customer records.

The SQL queries were executed against the read-only Online Retail database. The validator's LLM response was mocked as VALID to isolate deterministic validation behaviour.

### Initial Findings
The first completed validator run achieved 5/8 agreement (62.5%). Three valid SQL formulations were falsely rejected:

- Separate STRFTIME year/month extraction with CAST.
- Distinct invoice counting through a CTE.
- Distinct customer counting through GROUP BY.

### Improvements
The deterministic validator was extended to recognise:

- Separate STRFTIME year and month extraction, including CAST expressions.
- CTE-based distinct invoice counting.
- GROUP BY-based distinct customer counting.

The existing rejection checks were retained.

### Final Results

| Metric | Result |
|---|---:|
| Total test cases | 8 |
| Passed | 8 |
| Failed | 0 |
| SQL execution failures | 0 |
| False acceptances | 0 |
| False rejections | 0 |
| Validator test agreement | 100% |

### Interpretation
System C V2 successfully recognised all eight predefined test cases after the improvements. The experiment demonstrated that the validator could support additional SQL formulations beyond the patterns previously tested.

The initial false rejections also demonstrated that rigid SQL pattern recognition can reject semantically valid queries.

### Limitations
- Only eight predefined test cases were evaluated.
- The LLM response was mocked as VALID, isolating deterministic validation.
- The additional SQL formulations are recognised through targeted regular expressions and are not general SQL equivalence detection.
- Results are specific to the tested Online Retail database and query patterns.
- Further testing with broader and independently generated SQL formulations is required before making generalisation claims.

## Day 38 — Regression Testing and Validation Stability

### Objective
Evaluate whether the semantic validator modifications introduced during Days 30–37 affected previously completed validation, SQL equivalence, and false-acceptance tests.

The objective was to confirm that the existing functionality remained stable without making further code changes.

### Regression Test Results

| Original experiment | Test coverage | Result |
|---|---:|---|
| Day 30 — Validator robustness | 12 tests | 12/12 passed |
| Day 31 — Validator edge cases | 12 tests | 12/12 passed |
| Day 32 — Unseen SQL formulations | 8 tests | 8/8 passed |
| Day 33 — Executable SQL equivalence | 4 query pairs | 4/4 equivalent |
| Day 34 — Complex SQL equivalence | 4 query pairs | 4/4 equivalent |
| Day 35 — False acceptance testing | 4 incorrect queries | 4/4 rejected |
| Day 36 — Broader SQL robustness | 8 tests | 8/8 passed |

Across the regression suite, all 60 recorded test checks passed.

### Additional Query Plan Verification

The SQLite query plans from the Day 36 performance experiment were inspected again.

**NOT EXISTS**
- Full scan of the outer table (`o`).
- Correlated scalar subquery.
- Full scan of the inner table (`c`).

**NOT GLOB**
- Single table scan of `online_retail`.

**SUBSTR**
- Single table scan of `online_retail`.

These query plans remain consistent with the earlier performance observations. The correlated subquery in the tested NOT EXISTS formulation introduces substantially more work than the other two formulations.

### Interpretation

The regression tests indicate that the validator modifications introduced during Days 30–37 did not break the previously tested functionality.

The validator continued to:
- Recognize previously tested valid SQL formulations.
- Reject predefined incorrect aggregation, date, transaction-filtering, and sorting patterns.
- Accept equivalent SQL formulations tested against the Online Retail database.
- Recognize tested CTEs, nested subqueries, conditional aggregation, and alternative date and transaction-filtering expressions.

No additional validator code changes were required during this regression cycle.

### Limitations

- The tests cover predefined SQL cases rather than all possible SQL formulations.
- The LLM response was mocked as `VALID` in deterministic validator tests. Therefore, these results do not measure real LLM semantic judgement.
- SQL equivalence was evaluated using execution results on the Online Retail SQLite database.
- Query-plan findings are specific to the tested queries, dataset, and SQLite environment.
- Passing regression tests does not establish general SQL semantic equivalence or guarantee correctness for unseen queries.

### Conclusion

The Day 38 regression cycle was completed successfully. All 60 recorded regression checks passed, and the separate SQLite query-plan inspection completed without errors.

The current validator implementation was retained as a stable experimental checkpoint. No code modifications were made during this regression cycle.

## Day 39 — Validator Freeze

### Objective
Freeze the semantic validator before the main evaluation, so that the final test results are not influenced by further validator tuning.

### Actions
- Confirmed the working tree was clean and synchronised with GitHub.
- Created the Git tag `validator-v2-freeze` on the Day 38 commit and pushed it to GitHub.

### Decision
From this point, `semantic_validation_agent_v2.py` will not be modified unless a bug is found. Any change will be recorded in this log with its reason.

### Next step
Expand the Online Retail benchmark with new, unseen test questions.









## Day 39 (continued) — Benchmark v2, Unified Runner, Experiments 1 and 2

### 1. Benchmark v2
- File: `experiments/online_retail_benchmark_v2.py`.
- 30 new test questions (IDs 11–40), written after the validator freeze (`split = "test"`).
- Categories: revenue, customers, products, invoices, time, data quality, cancellations, net revenue, and two deliberately ambiguous questions (35, 36) with documented resolutions.
- Revenue definition: gross revenue = SUM(Quantity × UnitPrice) over rows with InvoiceNo NOT LIKE 'C%', Quantity > 0 and UnitPrice > 0.
- Every reference answer was verified by an independent second SQL formulation. All top-N questions were checked for ties at the cut-off (none found).

### 2. Unified experiment runner
- `experiments/run_experiment.py` runs System A, B or C on the same questions with the same LLM settings (qwen2.5:7b via Ollama, seed = 42 + repetition − 1).
- The frozen system code is not modified. LLM calls are routed through a wrapper that controls temperature/seed and records LLM calls and tokens.
- `src/scoring.py` is used for all systems. Numbers are compared with an absolute tolerance of 0.01. Two verdicts are recorded: strict (exact columns) and lenient (extra columns allowed). In both experiments, strict and lenient accuracy were identical.
- `tests/test_scoring.py`: 6 tests, all passing.
- A mock mode (`--mock`) feeds each system the reference SQL to test the pipeline without the LLM.

### 3. Experimental configuration
- 30 questions × 3 repetitions = 90 evaluations per system.
- Temperature 0.3, seeds 42, 43, 44.
- Experiment 1 (`--schema base`): original Online Retail schema description.
- Experiment 2 (`--schema definitions`): the same description plus five business definitions (normal sale, gross revenue, net revenue, purchase, customers), given identically to all three systems. This simulates a "semantic layer". The validator was not changed.

### 4. Results

| Metric | Exp 1 A | Exp 1 B | Exp 1 C | Exp 2 A | Exp 2 B | Exp 2 C |
|---|---:|---:|---:|---:|---:|---:|
| Correct answers (of 90) | 33 (36.7%) | 33 (36.7%) | 32 (35.6%) | 61 (67.8%) | 61 (67.8%) | 59 (65.6%) |
| Answers returned | 90 | 90 | 75 | 87 | 87 | 76 |
| Accuracy of returned answers | 36.7% | 36.7% | 42.7% | 70.1% | 70.1% | 77.6% |
| Wrong answers returned without warning | 57 (63.3%) | 57 (63.3%) | 43 (47.8%) | 26 (28.9%) | 26 (28.9%) | 17 (18.9%) |
| Average latency (s) | 1.89 | 3.21 | 4.89 | 2.57 | 3.71 | 5.71 |
| LLM calls per question | 1.00 | 1.60 | 2.61 | 1.00 | 1.56 | 2.68 |
| Prompt tokens per question | 541 | 618 | 1374 | 676 | 747 | 1716 |

Result files:
- Exp 1: `experiment_system_{A,B,C}_20261122_151901/152152/152641.json`
- Exp 2: `experiment_definitions_system_{A,B,C}_20261122_153911/154303/154837.json`

### 5. System C error detection and recovery (System A's answer with the same seed used as the initial attempt)

| | Exp 1 | Exp 2 |
|---|---:|---:|
| Initial attempts that were wrong | 57 | 29 |
| Wrong attempts detected (recall) | 14 (24.6%) | 13 (44.8%) |
| Wrong attempts corrected | 0 | 4 (13.8%) |
| Correct attempts falsely rejected | 3 of 33 (2 later recovered) | 6 of 61 (9.8%), none recovered |

Paired comparison, Exp 2, A vs C: C correct where A wrong = 4; A correct where C wrong = 6. McNemar exact p = 0.754, so there is no significant accuracy difference. Repetitions are not independent (identical per-question outcomes), so this test is indicative only.

### 6. Interpretation
1. Business definitions roughly doubled accuracy for every system (36.7% → 67.8% for A). Missing domain definitions were the largest source of error, larger than any effect of the multi-agent architecture.
2. System C did not improve overall accuracy, but it reduced wrong answers returned without warning (Exp 2: 28.9% → 18.9%) by abstaining. Its value is selective answering, not correction.
3. All false rejections came from the rule-based checks of the frozen validator:
   - "at least" matched the keyword "least" and was read as a ranking request (Q21, Q36).
   - A correct BETWEEN '2011-11-01 00:00:00' AND '2011-11-30 23:59:59' filter was rejected because it did not match the expected boundary pattern (Q15).
   Correct detections of real errors (Q25, Q26, Q31) came mainly from the LLM-based check.
4. Recovery rarely succeeded. Most failed recoveries ended because the regenerated SQL was identical to the previous SQL, and the orchestrator stops immediately in that case.
5. System B produced identical SQL to System A in all 180 evaluations because both use the same SQL-generation prompt and seed. B only adds a natural-language answer step, which does not affect result correctness.
6. Every question was either correct in all 3 repetitions or wrong in all 3 (except Q25 and Q35), showing low run-to-run variation at temperature 0.3.

### 7. Remaining genuine reasoning errors (Exp 2, System A)
- Q18: missing the UnitPrice > 0 filter for quantity totals.
- Q25, Q31: GROUP BY with COUNT returns one row per group instead of a single count.
- Q26, Q36, Q37: missing or wrong filters for customers and invoices.
- Q27: weekday number returned instead of weekday name.
- Q33: missing the UnitPrice > 0 filter.
- Q39: invalid nested aggregate (execution error) or integer division.

### 8. Limitations
- One model (qwen2.5:7b), one database, 30 test questions.
- Repetitions showed almost no variation, so the effective sample size is closer to 30 than 90.
- The validator and the orchestrator weaknesses were found on the test set and were deliberately not fixed, to avoid tuning on test data.
- The mock-mode test confirmed the pipeline, but mock results are not experimental evidence.

### 9. Next steps
- Produce result figures (accuracy, wrong-answer rate, latency per system and experiment).
- Update README status and write the results chapter.


## Day 39 (continued) — System C v3 and Final Hold-Out Evaluation

### 1. Procedure (order verified by Git tags)
1. `holdout-frozen`: 20 new hold-out questions (IDs 41–60) written, verified with independent second SQL formulations, and committed BEFORE System C v3 was designed.
2. System C v3 (`src/agents/orchestrator_c_v3.py`) was designed using only benchmark v2 (IDs 11–40):
   - 3 SQL candidates (candidate 0 = System A's generation; 2 more at temperature 0.8) with result-based majority voting.
   - Result-based checks only (execution error, empty/NULL result, multiple rows for a single-value question). No keyword rules.
   - An LLM judge that sees the question, SQL and result preview.
   - Up to 3 repairs; an identical SQL or identical result triggers a retry with a new seed instead of stopping.
   - Abstain only if checks still fail after repairs and fewer than 2 candidates agree.
   - Unit tests: `tests/test_orchestrator_c_v3.py` (4 tests, scripted fake LLM).
3. Two development runs on v2 questions (63/90 correct both times). Agreement-based abstention thresholds were analysed on development data only and rejected (see section 2). v3 was frozen with tag `c3-frozen`.
4. A one-time hold-out run: Systems A, C (v2) and C3 (v3), 20 questions × 3 repetitions, temperature 0.3, seeds 42–44, schema with business definitions. System B was omitted because it produced SQL identical to System A in all 180 earlier evaluations.

### 2. Development-set findings for v3 (questions 11–40)

| Policy | Answered | Correct | Wrong answers returned |
|---|---:|---:|---:|
| v3 as built | 87 | 63 | 24 |
| Answer only if ≥2 of 3 candidates agree | 79 | 58 | 21 |
| Answer only if all 3 agree | 61 | 46 | 15 |

In 15 cases all three candidates agreed on the same wrong result. The model's errors are systematic rather than random, so candidate agreement is a weak correctness signal.

### 3. Hold-out results (questions 41–60, 60 evaluations per system)

| Metric | System A | System C (v2) | System C v3 |
|---|---:|---:|---:|
| Correct answers | 27 (45.0%) | 24 (40.0%) | 28 (46.7%) |
| Answers returned | 57 | 44 | 55 |
| Accuracy of returned answers | 47.4% | 54.5% | 50.9% |
| Wrong answers returned without warning | 30 (50.0%) | 20 (33.3%) | 27 (45.0%) |
| Wrong attempts corrected (vs A, same seed) | — | 2 | 3 |
| Correct attempts lost (vs A, same seed) | — | 5 | 2 |
| Average latency (s) | 2.73 | 9.66 | 14.41 |
| LLM calls per question | 1.00 | 3.10 | 4.85 |
| Prompt tokens per question | 675 | 2151 | 3049 |

McNemar exact tests vs System A: C v2 p = 0.453, C v3 p = 1.000. Neither difference is statistically significant.

Result files: `experiment_holdout_definitions_system_{A,C,C3}_20261122_165209/165453/170432.json`.

### 4. Hold-out error analysis (System A, repetition 1)
All failures were checked manually and are genuine errors, not scoring artefacts:
- Missing UnitPrice > 0 even though the business definitions were provided: Q45, Q46, Q49, Q50, Q55, Q59.
- `BETWEEN '…' AND '2011-03-31'` on timestamp values silently excludes the last day: Q44, Q59.
- GROUP BY returning one row per group instead of a single number: Q57, Q60.
- Wrong denominator (invoices instead of customers): Q54.
- Self-join overcounting: Q47.

### 5. Conclusions
1. Neither recovery design produced a statistically significant accuracy improvement over the single-agent baseline on the hold-out set.
2. v3 was the most accurate system on both question sets and had the best balance of corrections to losses (development +4/−2, hold-out +3/−2), compared with v2 (development +4/−6, hold-out +2/−5).
3. v2 reduced wrong answers returned without warning the most (50.0% → 33.3% on hold-out), but mainly by abstaining, at the cost of correct answers.
4. Self-checking with the same 7B model can repair errors that have visible symptoms (execution errors, multi-row results for single-value questions). It cannot detect errors the model makes consistently (ignored filters, timestamp boundary mistakes), because the generator, judge and repairer share the same misunderstanding.
5. Domain definitions had the largest single effect (Experiment 1 → 2: 36.7% → 67.8%), but the model still ignored them in many hold-out questions.
6. Reliability mechanisms increased latency 3.5–5× and prompt tokens 3–4.5×.

### 6. Limitations
- One model (qwen2.5:7b), one database, 20 hold-out questions. Repetitions were highly correlated, so the effective sample size is close to the number of questions.
- The hold-out questions were harder than the development questions (System A: 67.8% vs 45.0%).
- The hold-out questions, v3 and the benchmark answers were produced with AI assistance and verified by independent SQL formulations. The chronology is recorded by Git tags.


## Day 39 (continued) — Experiment 3: Larger Reviewer Model and Model-Size Control

### 1. Design (fixed before results were seen)
- System C v3 unchanged, except that the judge and repair steps use qwen2.5:14b (`--review-model qwen2.5:14b`). SQL generation remains qwen2.5:7b.
- Hypothesis: v3 failed with a 7B reviewer because generator and reviewer share the same blind spots; an independent, stronger reviewer should detect and repair more errors.
- The hold-out set was reused because no design decision was tuned on it.
- Control (added after Experiment 3, before interpretation): System A with qwen2.5:14b as the generator (`--gen-model qwen2.5:14b`), to separate the effect of the recovery design from the effect of model size.

### 2. Results — development questions 11–40 (90 evaluations)

| System | Correct | Fixed / lost vs A | Latency (s) |
|---|---:|---:|---:|
| A (7B) | 61 (67.8%) | — | 2.6 |
| C3, 7B reviewer | 63 (70.0%) | 4 / 2 | 11.7 |
| C3, 14B reviewer | 68 (75.6%) | 9 / 2 | 25.8 |

### 3. Results — hold-out questions 41–60 (60 evaluations)

| System | Correct | Wrong answers returned without warning | Latency (s) | LLM calls | Prompt tokens |
|---|---:|---:|---:|---:|---:|
| A (7B) | 27 (45.0%) | 30 (50.0%) | 2.7 | 1.00 | 675 |
| C (v2, 7B) | 24 (40.0%) | 20 (33.3%) | 9.7 | 3.10 | 2151 |
| C3, 7B reviewer | 28 (46.7%) | 27 (45.0%) | 14.4 | 4.85 | 3049 |
| C3, 14B reviewer | 35 (58.3%) | 20 (33.3%) | 30.7 | 5.08 | 3225 |
| **A (14B generator, control)** | **49 (81.7%)** | **11 (18.3%)** | **8.0** | **1.00** | **675** |

Paired comparisons (McNemar exact; per evaluation, and per question as a sign test on the 3-repetition totals):

| Comparison | Per evaluation (gains/losses, p) | Per question (gains/losses, p) |
|---|---|---|
| C3-14B reviewer vs A-7B | 9 / 1, p = 0.021 | 5 / 1, p = 0.219 |
| A-14B vs A-7B | 22 / 0, p < 0.001 | 10 / 0, p = 0.002 |
| C3-14B reviewer vs A-14B | 4 / 18, p = 0.004 | 2 / 9, p = 0.065 |

Result files:
- `experiment_v2_definitions_system_C3_review-qwen2.5-14b_20261122_180031.json`
- `experiment_holdout_definitions_system_C3_review-qwen2.5-14b_20261122_183912.json`
- `experiment_holdout_definitions_system_A_gen-qwen2.5-14b_20261122_191324.json`

### 4. Interpretation
1. A stronger, independent reviewer made recovery effective: on hold-out it fixed 9 wrong answers and broke 1 (+13.3 percentage points over A-7B), consistent with the development set (+7.8 points).
2. However, using the 14B model directly as a single-agent generator was far better: 81.7% correct, 18.3% wrong answers returned without warning, about 4× faster and with about 5× fewer prompt tokens than C3 with the 14B reviewer.
3. Therefore most of the improvement comes from model capability, not from the multi-agent recovery architecture. Pairing a weak generator with a strong reviewer is worse than using the strong model to generate.
4. The 14B-reviewer configuration solved two questions the 14B generator alone never solved (Q54 in 3/3, Q60 in 1/3). This suggests recovery may still add value on top of a strong generator, which has not yet been tested.
5. Errors shared by all configurations remain: timestamp `BETWEEN` boundary errors (Q44, Q59).

### 5. Limitations
- 20 hold-out questions; repetitions highly correlated; per-question tests have low power.
- One model family (Qwen 2.5), one database.
- The hold-out set has now been used for four configurations; further design changes must not be tuned on it.


## Day 39 (continued) — Experiment 4: Recovery on Top of the Stronger Model (final experiment)

### 1. Design
- System C v3 unchanged, with qwen2.5:14b used for every step: generation, candidates, judge and repair (`--system C3 --gen-model qwen2.5:14b`).
- Compared with System A using qwen2.5:14b (the control from Experiment 3), on the hold-out set with the same seeds.
- Question: does autonomous detection and recovery add value once the base model is capable?

### 2. Results — hold-out questions 41–60 (60 evaluations)

| System (all steps qwen2.5:14b) | Correct | Wrong answers returned without warning | Latency (s) | LLM calls | Prompt tokens |
|---|---:|---:|---:|---:|---:|
| A — single agent | 49 (81.7%) | 11 (18.3%) | 8.0 | 1.00 | 675 |
| C3 — detection and recovery | 53 (88.3%) | 7 (11.7%) | 27.5 | 4.80 | 2914 |

- Paired comparison: C3 fixed 4 answers and broke 0 (McNemar exact p = 0.125). Per question: 2 improved, 0 worse (sign test p = 0.50).
- Fixed cases: Q54 (2 of 3 runs, wrong denominator for "average revenue per customer") and Q60 (2 of 3 runs, GROUP BY returning one row per customer). Each was fixed by one repair after a deterministic or judge check flagged the first answer.
- Unsolved by both: Q44 and Q59 (timestamp `BETWEEN` boundary), where the model and its reviewer consistently accept the wrong filter.

Result file: `experiment_holdout_definitions_system_C3_gen-qwen2.5-14b_20261122_192412.json`.

### 3. Interpretation
- With a capable model, recovery improved accuracy (+6.7 points) and reduced wrong answers returned without warning (18.3% → 11.7%) without breaking any correct answer, at about 3.4× latency and 4.3× prompt tokens.
- The improvement is consistent but not statistically significant with 20 questions.

---

## Overall Conclusions of the Experimental Programme (Experiments 1–4)

1. **Domain definitions matter most.** Adding business definitions to the schema prompt raised 7B accuracy from 36.7% to 67.8% on the development set.
2. **Model capability matters next.** Replacing the 7B generator with 14B raised hold-out accuracy from 45.0% to 81.7% (10 questions improved, 0 worse, p = 0.002).
3. **Self-recovery with a weak model does not work.** With the 7B model as generator and reviewer, neither recovery design improved accuracy significantly. The model's errors are systematic, so the generator, judge and repairer share the same blind spots. Keyword-based validation (v2) also caused false rejections.
4. **Recovery helps once the reviewer is capable.** A 14B reviewer improved the 7B pipeline (+13.3 points), and a full 14B recovery pipeline improved the 14B baseline (+6.7 points, 4 fixed / 0 broken). Neither beat simply using the stronger model for generation, which has the best accuracy for the cost.
5. **Reliability costs.** Recovery pipelines cost about 3.4–5× the latency and 3–5× the prompt tokens of a single call.
6. **Design lessons for System C v3:** result-based checks instead of keyword rules, self-consistency voting, a judge that sees results, and retrying with variation instead of stopping on identical SQL. Candidate agreement alone was a weak correctness signal for a small model.

Overall: autonomous error detection and recovery is not a substitute for model capability or domain knowledge. It provides a modest, non-harmful reliability gain when the underlying model is strong enough to recognise its own errors. Confirming this with statistical significance requires a larger benchmark.
