# Reliability-Aware Multi-Agent LLM System

## Research Title

**Design and Evaluation of a Reliability-Aware Multi-Agent LLM System with Autonomous Error Detection and Recovery for Natural Language Data Analysis**

## 1. Project Overview

This project investigates the design and evaluation of a reliability-aware multi-agent system that uses Large Language Models (LLMs) to answer natural-language questions about structured databases.

The primary research focus is improving the reliability of natural-language database analysis through autonomous error detection, semantic validation, and bounded recovery.

The research compares three system configurations to investigate whether autonomous error detection and recovery improves query and answer correctness, and evaluates the computational overhead introduced by these mechanisms.

## 2. Research Objective

To investigate whether adding autonomous error detection and recovery to a multi-agent LLM system improves reliability in natural-language database analysis, and to evaluate the computational cost of this improvement.

## 3. System Architecture

The research evaluates three system configurations.

### System A — Single-Agent Baseline

A single-agent workflow that:
- Converts natural-language questions into SQL.
- Executes generated SQL against a database.
- Uses query results to generate a natural-language answer.

### System B — Multi-Agent Without Autonomous Recovery

A multi-agent workflow involving specialised agents:
- SQL Agent
- SQL Executor
- Analysis Agent

The system generates and executes SQL but does not use an autonomous recovery loop.

### System C — Multi-Agent With Autonomous Error Detection and Recovery

An extended multi-agent workflow that includes:
- SQL Agent
- SQL Executor
- Error Detection Agent
- Semantic Validation Agent
- Analysis Agent
- Bounded recovery mechanism

The system detects execution and semantic validation failures and attempts to regenerate incorrect SQL within a predefined recovery limit.

The current recovery implementation permits a maximum of two recovery attempts.

## 4. Main Components

| Component | Responsibility |
|---|---|
| SQL Agent | Converts natural-language questions into SQL |
| SQL Executor | Validates and executes SQL queries |
| Error Detection Agent | Detects SQL execution failures |
| Semantic Validation Agent | Checks generated SQL against the question and domain rules |
| Recovery Mechanism | Regenerates SQL following detected failures |
| Analysis Agent | Converts query results into natural-language responses |
| Orchestrator | Coordinates agent execution and system workflow |
| Evaluation Utilities | Compare generated results against expected benchmark results |

## 5. Technology Stack

### Implemented Technologies

- Python 3.12.16
- SQLite
- Ollama
- Qwen2.5 7B
- Python sqlite3
- Pandas
- OpenPyXL
- Python unittest

### Development Environment

- macOS
- PyCharm
- Anaconda / Conda
- Local LLM inference through Ollama

No paid LLM API is currently required. The project uses a locally hosted Qwen2.5 7B model.

## 6. Databases and Datasets

The project uses two datasets for development and evaluation.

### 6.1 NovaRetail — Synthetic Development Dataset

Database engine: SQLite

Database file: `data/novaretail.db`

NovaRetail is a synthetic retail database used for system development, initial benchmarking, and controlled fault-injection experiments.

| Table | Records |
|---|---:|
| Customers | 30 |
| Products | 20 |
| Orders | 100 |
| Order Items | 257 |
| **Total** | **407** |

The dataset contains four tables:
- customers
- products
- orders
- order_items

It provides a controlled environment for developing and testing the three system configurations.

### 6.2 UCI Online Retail — External Validation Dataset

Source dataset: `data/Online Retail.xlsx`

SQLite database: `data/online_retail.db`

The UCI Online Retail dataset is being used for external validation beyond the synthetic NovaRetail database.

Dataset characteristics:

| Attribute | Value |
|---|---:|
| Total records | 541,909 |
| Original columns | 8 |
| Unique invoice numbers | 25,900 |
| Unique non-null customer IDs | 4,372 |
| Unique countries | 38 |
| Unique product codes | 4,070 |

Original columns:
- InvoiceNo
- StockCode
- Description
- Quantity
- InvoiceDate
- UnitPrice
- CustomerID
- Country

The dataset contains missing customer identifiers, cancellations, negative quantities, and non-positive prices.

The original records have been preserved. Missing CustomerID values remain NULL.

The SQLite database includes the following views:

- `cancellations`
- `positive_quantity_records`
- `returns`

These views support separate analysis of cancellation records, positive-quantity records, and non-cancellation returns.

Classification rules are based on invoice identifiers and quantity values. Positive-quantity records should not automatically be interpreted as completed sales.

## 7. Evaluation Methodology

The research evaluates the systems using benchmark questions with reference SQL and expected database results.

### Evaluation Metrics

- SQL execution accuracy
- Final database result correctness
- Natural-language answer correctness
- Task completion rate
- Error detection precision and recall
- Recovery success rate
- Execution latency
- LLM calls and token usage
- Estimated computational cost

SQL execution success and semantic correctness are evaluated separately. A query that executes successfully is not necessarily correct.

Repeated trials are used where applicable to investigate the consistency of experimental outcomes.

## 8. Experimental Progress

### 8.1 System A — Initial Baseline

The initial single-agent baseline was evaluated using ten NovaRetail benchmark questions.

| Metric | Result |
|---|---:|
| Benchmark questions | 10 |
| Successful SQL executions | 10/10 |
| Correct final answers | 10/10 |
| SQL execution success rate | 100% |
| Answer correctness rate | 100% |

These results represent an initial run with one execution per benchmark question on a synthetic dataset. They do not establish general reliability or real-world generalisation.

### 8.2 System B vs System C — Repeated Fault-Injection Experiment

A controlled repeated fault-injection experiment was conducted to compare Systems B and C.

Experimental setup:
- Four predefined SQL fault scenarios.
- Five trials per scenario.
- Twenty total trials.
- Both systems received the same initial faulty SQL for each scenario.

Fault scenarios:
1. Incorrect database table.
2. Incorrect date filter.
3. Incorrect aggregation.
4. Missing unit conversion.

Preliminary results:

| Metric | System B | System C |
|---|---:|---:|
| Successful SQL executions | 20/20 | 20/20 |
| Strict correctness | 0/20 | 20/20 |
| Total recovery attempts | 0 | 20 |

Average latency:

| System | Average latency |
|---|---:|
| System B | 0.1194 seconds |
| System C | 2.9753 seconds |

System C recovered from the four predefined injected fault types in all twenty trials, while System B executed the initially faulty queries without recovery.

The results indicate a reliability improvement under the tested fault conditions, accompanied by increased latency.

**Experimental limitations:** These results are based on four predefined fault types, five trials per type, and a synthetic database. SQL semantic checks include scenario-specific heuristics. They should therefore be interpreted as preliminary controlled experimental evidence, not proof of general semantic correctness.

Detailed results are stored in the `results/` directory.

### 8.3 External Dataset Preparation

The UCI Online Retail dataset has been imported into SQLite.

Completed preparation activities:
- Inspected the original dataset.
- Examined missing values and data types.
- Preserved all original records.
- Created the SQLite database.
- Created transaction classification views.
- Verified the imported record count.
- Inspected date ranges, countries, products, and monthly distributions.
- Verified that the monthly transaction classifications reconcile with total records.

External benchmark design and system evaluation on this dataset remain in progress.

## 9. Project Structure

The project currently follows this structure:

```text
ReliabilityAwareMultiAgentSystem/
│
├── data/
│   ├── novaretail.db
│   ├── online_retail.db
│   ├── Online Retail.xlsx
│   └── schema.sql
│
├── docs/
│   ├── database_design.md
│   └── research_log.md
│
├── experiments/
│   ├── benchmark_questions.py
│   ├── create_online_retail_db.py
│   ├── inspect_online_retail.py
│   ├── inspect_online_retail_sqlite.py
│   ├── evaluate_baseline.py
│   ├── evaluate_multi_agent.py
│   ├── evaluate_system_c.py
│   ├── fault_injection_test.py
│   ├── repeated_fault_injection_test.py
│   └── ...
│
├── results/
│   └── Experimental JSON results
│
├── src/
│   ├── agents/
│   │   ├── analysis_agent.py
│   │   ├── error_detection_agent.py
│   │   ├── orchestrator.py
│   │   ├── orchestrator_c.py
│   │   ├── result_formatter.py
│   │   ├── semantic_validation_agent.py
│   │   └── sql_agent.py
│   │
│   ├── database.py
│   ├── evaluation_utils.py
│   ├── llm_client.py
│   ├── nl_to_sql.py
│   ├── sql_executor.py
│   └── ...
│
├── tests/
│   ├── test_evaluation.py
│   ├── test_natural_language_evaluation.py
│   └── test_sql_security.py
│
├── README.md
└── ...
```

The structure may evolve as external validation and additional experiments are implemented.

## 10. Current Implementation Status

| Research activity | Status |
|---|---|
| NovaRetail database creation | Completed |
| SQL execution safeguards | Implemented |
| Local LLM integration | Implemented |
| System A baseline | Implemented |
| System B multi-agent pipeline | Implemented |
| System C recovery mechanism | Implemented |
| Initial benchmark evaluation | Completed |
| Repeated fault-injection experiment | Completed |
| Online Retail database preparation | Completed |
| External benchmark design | Pending |
| External dataset evaluation | Pending |
| Repeated evaluation across all systems | Pending |
| Comprehensive statistical analysis | Pending |
| Final thesis writing | Pending |

## 11. Limitations and Research Considerations

The following limitations are considered during evaluation:

- Successful SQL execution does not guarantee semantic correctness.
- LLM-generated SQL and semantic validation can produce incorrect outputs.
- The current fault-injection experiment covers only four predefined fault types.
- The external dataset contains missing identifiers and transaction records requiring careful interpretation.
- Synthetic dataset results cannot establish performance on unrelated real-world databases.
- Increased validation and recovery introduce additional latency and computational overhead.
- The current SQL safeguards should not be interpreted as a complete SQL sandbox.

These limitations will be considered when interpreting the final experimental findings.

## 12. Future Work

1. Design and independently verify an external Online Retail benchmark.
2. Adapt the shared architecture to support both databases.
3. Evaluate Systems A, B and C under consistent experimental conditions.
4. Conduct repeated trials on the external dataset.
5. Measure latency and computational overhead.
6. Record LLM calls, token usage, and estimated computational cost where measurable.
7. Evaluate error detection and recovery performance.
8. Analyse experimental results and limitations.
9. Prepare the final Master's thesis and viva presentation.

## 13. Research Documentation

Research decisions, implementation details, experimental observations, results, and limitations are maintained in:

`docs/research_log.md`

The research log serves as the chronological record of the project's development and experimental progress.

### External Dataset Evaluation — UCI Online Retail

System C was evaluated on a separate real-world dataset from the UCI Machine Learning Repository to test its ability to handle a database beyond the synthetic NovaRetail dataset.

**Benchmark results:**

| Metric | System C |
|---|---:|
| Benchmark questions | 10 |
| Successful SQL executions | 10/10 |
| Correct answers | 10/10 |
| Execution success rate | 100% |
| Answer accuracy | 100% |
| Recovery attempts | 0 |
| Average latency | 2.9182 seconds |

The benchmark covered distinct counts, missing values, cancellations, returns, date filtering, aggregations, sorting, and product-code counts.

**Interpretation:** System C answered all ten benchmark questions correctly on its initial attempts. No recovery was required.

**Limitations:** This was a single run with ten predefined questions. Question 8 used semantic comparison of labelled aggregate results. These preliminary results do not establish general accuracy or recovery effectiveness.

Detailed results: `results/online_retail_system_c_20261117_022105.json`

### System B — Online Retail Benchmark

System B was evaluated on the UCI Online Retail dataset using 10 predefined benchmark questions.

| Metric | Result |
|---|---:|
| Questions evaluated | 10 |
| Successful executions | 10/10 |
| Correct answers | 10/10 |
| Answer accuracy | 100% |
| Recovery attempts | 0 |
| Average latency | 1.6662 seconds |

System B achieved 100% accuracy in this initial evaluation without autonomous recovery or semantic validation.

Compared with System C, which also achieved 100% accuracy in its initial evaluation, System B had lower average latency (1.6662 s vs. 2.9182 s).

These are preliminary single-run results. Repeated experiments are required to evaluate performance variability.

**Results:** `results/online_retail_system_b_20261117_120718.json`

### Repeated Benchmark Evaluation — Systems B and C

Both systems were evaluated using five repetitions of the ten-question UCI Online Retail benchmark.

| Metric | System B | System C |
|---|---:|---:|
| Total evaluations | 50 | 50 |
| Correct answers | 50 | 50 |
| Accuracy | 100% | 100% |
| Recovery attempts | 0 | 0 |
| Average latency | 1.6714 s | 3.1534 s |

Both systems achieved 100% accuracy during normal operation. System C had approximately 88.7% higher average latency than System B.

These results demonstrate consistent performance on the tested benchmark but do not establish a normal-operation accuracy advantage for System C. Its recovery capabilities are evaluated separately through fault-injection experiments.

## Latest Research Progress — Day 27

### System C V2: Improved Semantic Validation and Autonomous Recovery

Implemented an improved semantic validation agent and a separate System C V2 orchestrator.

**New components:**
- `src/agents/semantic_validation_agent_v2.py`
- `src/agents/orchestrator_c_v2.py`

**Validation capabilities tested:**
- Incorrect aggregation detection.
- Missing currency conversion detection.
- Incorrect date-filter detection.
- Incorrect transaction-filter detection.
- Incorrect sorting detection.

**Online Retail Fault-Injection Experiment**

Evaluated System B against System C V2 using four injected SQL fault scenarios, with five trials per scenario.

| Metric | System B | System C V2 |
|---|---:|---:|
| Total trials | 20 | 20 |
| Correct results | 0/20 | 20/20 |
| Execution success rate | 75% | 100% |
| Correctness rate | 0% | 100% |
| Recovery attempts | 0 | 25 |

System C V2 successfully recovered from all four tested fault types.

**Average latency across scenario averages:**
- System B: 0.377 seconds.
- System C V2: 3.029 seconds.

**Key finding:** Improved semantic validation enabled System C V2 to detect and recover from faults that System C V1 previously missed, with additional computational latency.

*These results represent preliminary evidence from four predefined fault types and five repetitions per scenario using the UCI Online Retail dataset.*

### Day 29 — Expanded Semantic Fault-Injection Experiment

**Objective:** Evaluate the ability of System C V2 to detect and recover from SQL queries that execute successfully but produce semantically incorrect results.

**Dataset:** UCI Online Retail  
**Database:** `data/online_retail.db`  
**Systems compared:** System B and System C V2  
**Fault scenarios:** 4  
**Repetitions:** 20 per scenario  
**Total trials:** 80 per system (160 executions)

**Fault scenarios tested:**
1. Incorrect NULL handling (`= NULL` instead of `IS NULL`).
2. Counting records instead of distinct invoices.
3. Incorrect monthly grouping.
4. Counting records instead of distinct products.

**Results:**

| Metric | System B | System C V2 |
|---|---:|---:|
| Successful executions | 80/80 | 80/80 |
| Correct results | 0/80 | 71/80 |
| Execution success rate | 100% | 100% |
| Correctness rate | 0% | 88.75% |
| Recovery attempts | 0 | 89 |
| Average of scenario latencies | 0.3627 s | 6.2205 s |

System C V2 achieved 100% correctness in three scenarios but achieved only 55% correctness in the monthly grouping scenario (11/20 trials).

**Key Findings:**
- Successful SQL execution does not necessarily indicate a correct analytical result.
- Semantic validation and autonomous recovery improved correctness across the tested fault scenarios.
- Monthly grouping remains a weakness in the current validation and recovery approach.
- System C V2 introduced approximately 17.1 times the average latency of System B.

**Result file:** `results/repeated_online_retail_fault_injection_20261117_210534.json`

**Conclusion:** System C V2 achieved 88.75% observed correctness under the four tested semantic fault scenarios. The experiment highlights the benefits of semantic validation while identifying temporal grouping and computational overhead as areas for improvement.

**Status:** Completed.

### Day 30 — Semantic Validator Robustness Evaluation

Evaluated the deterministic validation rules in System C V2 using 12 predefined test cases.

**Test coverage:**
- Date filter validation
- Cancellation-record exclusion
- Sorting and ranking
- Aggregation selection
- Paise-to-rupees conversion

**Results:**
- Total test cases: 12
- Passed: 12
- Failed: 0
- Test agreement: 100%

**Improvements:**
- Strengthened date-boundary and comparison-operator validation.
- Added support for equivalent cancellation exclusion using `SUBSTR(InvoiceNo, 1, 1) <> 'C'`.
- Retained aggregation, sorting, ranking, and currency-conversion checks.

**Test script:** `experiments/test_validator_robustness_day30.py`

**Limitation:** The LLM validation response was mocked as `"VALID"` to isolate deterministic checks. The result represents agreement across the 12 predefined test cases, not general semantic-validation accuracy.

### Day 31 — Extended Validator Edge Case Testing

Extended the System C V2 semantic validator test suite with 12 predefined edge cases.

**Test results:**
- Total test cases: 12
- Passed: 12
- Failed: 0
- Test agreement: 100%

**Areas tested:**
- Date boundary validation
- Cancellation filtering
- Equivalent SQL expressions
- Top-N and bottom-N sorting
- SUM and AVG aggregation
- Distinct invoice counting
- Currency conversion

**Improvements:**
- Added validation for `COUNT(DISTINCT InvoiceNo)` when distinct invoices are requested.
- Recognized multiplication by `0.01` as an equivalent paise-to-rupees conversion.
- Corrected numeric top-N and bottom-N sorting detection.

**Limitation:** The test suite used a mocked LLM response to isolate deterministic checks. The 100% result represents agreement with 12 predefined test expectations, not general semantic-validation accuracy.

### Day 32 — Unseen SQL Formulation Testing

Evaluated System C V2 against eight additional SQL formulation cases.

**Results:**
- Test cases: 8
- Passed: 8
- Failed: 0
- Test agreement: 100%

**Improvements:**
- Recognized alternative monthly date filters using `BETWEEN` and `STRFTIME`.
- Added cancellation exclusion support for `NOT GLOB`.
- Extended aggregation validation to detect incorrect distinct customer counts.
- Tested aggregate sorting and ascending/descending ranking behavior.

**Evaluation limitation:** The LLM validator response was mocked as `VALID`, and SQL was not independently executed during these tests. The results represent agreement on eight predefined validator cases, not general semantic-validation accuracy.

### Day 33 — Executable SQL Equivalence Testing

Evaluated four pairs of alternative SQL formulations against the UCI Online Retail SQLite database.

**Final results:**
- Equivalent SQL pairs: 4/4
- SQL execution failures: 0
- Validator acceptances: 8/8
- Validator rejections: 0
- SQL equivalence rate: 100%

**Tested formulations:**
- `BETWEEN` versus inclusive-start/exclusive-end date filtering.
- `NOT GLOB` versus `SUBSTR` cancellation filtering.
- Aggregate expression versus aggregate alias sorting.
- `COUNT(DISTINCT CustomerID)` versus a distinct subquery.

**Improvement:** Fixed a false rejection in distinct-customer validation by recognizing the tested `COUNT(*)` over `SELECT DISTINCT CustomerID` subquery formulation.

**Regression testing:** All eight Day 32 unseen SQL formulation tests passed after the change.

**Limitations:** The experiment evaluated four predefined query pairs using one SQLite database. The LLM response was mocked, and the deterministic subquery recognition remains pattern-based rather than a general SQL equivalence mechanism.

### Day 34 — Complex SQL Equivalence Testing

Evaluated whether the System C V2 semantic validator recognizes different SQL formulations that produce equivalent database results on the UCI Online Retail dataset.

**Four SQL equivalence experiments:**

1. Nested subquery vs Common Table Expression (CTE).
2. Conditional aggregation using CASE WHEN vs WHERE filtering.
3. STRFTIME vs SUBSTR date extraction.
4. Correlated NOT EXISTS vs NOT GLOB cancellation exclusion.

**Final results:**

| Metric | Result |
|---|---:|
| Equivalent query pairs | 4/4 |
| Validator acceptances | 8/8 |
| SQL execution failures | 0 |
| Final acceptance rate | 100% |

The experiments identified and addressed false rejections involving CTEs, alternative date extraction, and cancellation filtering.

**Regression testing:**
- Day 30: 12/12 passed.
- Day 31: 12/12 passed.
- Day 32: 8/8 passed.
- Day 33: 4/4 equivalent pairs; 8/8 validator acceptances.

**Research limitation:** These results represent predefined tests on one SQLite dataset. The LLM response was mocked as `VALID`, and the deterministic validator remains pattern-based. The results do not establish general SQL equivalence or 100% semantic-validation accuracy.

**Conclusion:** Day 34 improved the tested validator's ability to recognize alternative SQL formulations while preserving all previously tested behaviours.


### Day 35 — False Acceptance Testing

Evaluated whether System C V2 incorrectly accepts logically incorrect SQL queries.

**Four incorrect SQL scenarios tested:**
1. Incorrect aggregation (`COUNT(*)` instead of `COUNT(DISTINCT InvoiceNo)`).
2. Incorrect date filtering (October instead of November 2011).
3. Missing cancellation exclusion for negative-quantity records.
4. Incorrect sorting (lowest five instead of highest five countries).

**Final results:**
- Incorrect queries tested: 4
- Correctly rejected: 4/4
- False acceptances after correction: 0
- Rejection rate across tested cases: 100%

An initial false acceptance was identified in the cancellation-exclusion scenario. The question-pattern detection was extended to recognize additional cancellation wording, and the Online Retail schema was explicitly passed to the validator.

**Regression testing after the changes:**
- Day 30: 12/12 passed.
- Day 31: 12/12 passed.
- Day 32: 8/8 passed.
- Day 33: 4/4 SQL equivalence pairs passed; 8/8 validator decisions accepted.
- Day 34: 4/4 complex SQL equivalence pairs passed; 8/8 validator decisions accepted.

All 48 previous regression test cases passed.

**Limitations:** The false-acceptance experiment used four predefined incorrect queries. The LLM response was mocked as `VALID`, isolating deterministic validation behaviour. These results do not establish general SQL semantic correctness or guarantee detection of all incorrect queries.

### Day 36 — Broader SQL Robustness and Performance Evaluation

#### 1. Broader SQL Robustness Testing

Evaluated eight predefined valid and invalid SQL cases using System C V2.

Test coverage:
- STRFTIME-based date filtering.
- Incorrect distinct invoice aggregation using a subquery.
- Cancellation exclusion using NOT EXISTS.
- Incorrect cancellation filtering.
- CTE-based top-five country aggregation.
- Incorrect ascending sorting.
- CTE-based distinct customer counting.
- Incorrect whole-table customer counting.

**Results:**
- Total tests: 8
- Passed: 8
- Failed: 0
- SQL execution failures: 0
- Validator test agreement: 100%

#### 2. Repeated SQL Performance Comparison

Compared three equivalent SQL formulations for identifying negative-quantity records while excluding cancelled invoices.

Expected result: 1,336 records.

| SQL formulation | Median execution time | Correct result |
|---|---:|---|
| NOT EXISTS | 101.7488 seconds | Yes |
| NOT GLOB | 0.0157 seconds | Yes |
| SUBSTR | 0.0158 seconds | Yes |

- Five executions per formulation.
- Total executions: 15.
- All 15 executions returned the expected result.
- NOT GLOB recorded the lowest median execution time.

The NOT EXISTS formulation was approximately 6,480 times slower than NOT GLOB in this experiment.

#### 3. SQLite Query Plan Inspection

Used SQLite `EXPLAIN QUERY PLAN` to investigate the execution-time differences.

- **NOT EXISTS:** Outer table scan, correlated scalar subquery, and additional inner table scan.
- **NOT GLOB:** Single table scan.
- **SUBSTR:** Single table scan.

The query plans support the observed performance difference for the tested SQL statements.

#### 4. Key Findings

- System C V2 correctly handled all eight predefined robustness cases.
- CTE-based aggregation and distinct customer counting were accepted.
- Incorrect aggregation, cancellation filtering, and sorting were rejected.
- Equivalent SQL formulations produced substantially different execution times.
- Query-plan inspection identified the correlated subquery in the slower formulation.

#### 5. Limitations

- Eight predefined validator cases do not represent exhaustive SQL coverage.
- The LLM response was mocked as `VALID` to isolate deterministic validation.
- Performance measurements were conducted on one SQLite database and computing environment.
- Results should not be generalized to all SQL engines or query structures.
- Validator agreement does not establish general semantic accuracy.

**Day 36 conclusion:** Broader SQL robustness testing and repeated performance evaluation extended the assessment of System C V2. The experiments demonstrated successful handling of the tested SQL structures and highlighted the importance of evaluating execution efficiency separately from query correctness.

### Day 37 — Unseen SQL Pattern Testing

**Objective:** Evaluate System C V2 against alternative SQL formulations not explicitly covered in earlier validator tests.

**Experiment:** `experiments/test_unseen_sql_patterns_day37.py`

Eight test cases covered date extraction, cancellation filtering, distinct invoice counting, and distinct customer counting.

**Improvements implemented:**
- Recognised separate STRFTIME year/month extraction with CAST.
- Added recognition of CTE-based distinct invoice counting.
- Added recognition of GROUP BY-based distinct customer counting.

**Final results:**

| Metric | Result |
|---|---:|
| Test cases | 8 |
| Passed | 8 |
| Failed | 0 |
| SQL execution failures | 0 |
| False acceptances | 0 |
| False rejections | 0 |
| Validator agreement | 100% |

**Interpretation:** All eight predefined test cases passed after targeted improvements to deterministic SQL pattern recognition.

**Limitations:** The LLM response was mocked as VALID. The experiment evaluates a small predefined test set and does not establish general semantic SQL validation or generalisation to arbitrary SQL formulations.

## Day 38 — Regression Testing

### Overview
Completed regression testing to verify that the semantic validator improvements introduced during Days 30–37 did not break previously implemented functionality.

### Regression Results

| Experiment | Tests | Result |
|---|---:|---|
| Day 30 — Validator robustness | 12 | 12/12 passed |
| Day 31 — Validator edge cases | 12 | 12/12 passed |
| Day 32 — Unseen SQL formulations | 8 | 8/8 passed |
| Day 33 — SQL equivalence | 4 pairs | 4/4 equivalent |
| Day 34 — Complex SQL equivalence | 4 pairs | 4/4 equivalent |
| Day 35 — False acceptance testing | 4 | 4/4 incorrect queries rejected |
| Day 36 — Broader SQL robustness | 8 | 8/8 passed |

**Overall: 60/60 recorded regression checks passed.**

### Query Plan Verification

The Day 36 SQLite query-plan inspection was repeated.

- `NOT EXISTS`: outer table scan, correlated scalar subquery, and inner table scan.
- `NOT GLOB`: single table scan.
- `SUBSTR`: single table scan.

These findings are consistent with the earlier performance experiment, in which the tested `NOT EXISTS` formulation was substantially slower than the other two formulations.

### Key Findings
- Previously tested valid SQL formulations continued to be accepted.
- Previously tested incorrect SQL patterns continued to be rejected.
- No regression failures were observed.
- No validator code modifications were required during this testing cycle.

### Limitations
- Tests use predefined SQL cases and do not establish general SQL semantic correctness.
- Deterministic validator tests used a mocked LLM response of `VALID`.
- SQL equivalence was assessed using execution results on the Online Retail SQLite database.
- Query-plan and performance findings are specific to the tested queries and environment.

**Status:** Day 38 regression testing completed successfully. The current implementation was retained as a stable experimental checkpoint.



