# Evaluation Methodology & Benchmark Results

FinSQL Agent incorporates an automated benchmarking framework evaluating 100 realistic financial questions across 9 distinct categories.

## 1. Measured Benchmark Results

The following metrics reflect actual empirical execution:

| Metric | Baseline Text-to-SQL | FinSQL Agent (Ours) | Delta Improvement |
| :--- | :---: | :---: | :---: |
| **SQL Execution Accuracy** | 100.0% | **99.0%** | -1.0% |
| **Result Accuracy** | 60.0% | **99.0%** | **+39.0%** |
| **Financial Correctness** | 60.0% | **99.0%** | **+39.0%** |
| **Schema Retrieval Accuracy** | 0.0% (No Retrieval) | **100.0%** | **+100.0%** |
| **Error Recovery Rate** | 0.0% (No Recovery) | **87.5%** | **+87.5%** |
| **Average Latency** | 0.16 ms | 178.72 ms | Includes RAG & AST |
| **Average Retries** | 0 | 0.1 | Self-healing |

---

## 2. Category Performance Breakdown

| Category | Sample Size | SQL Execution | Result Accuracy |
| :--- | :---: | :---: | :---: |
| `simple_lookup` | 15 | 100.0% | 100.0% |
| `comparison` | 15 | 100.0% | 100.0% |
| `aggregation` | 10 | 100.0% | 100.0% |
| `time_series` | 12 | 100.0% | 100.0% |
| `multi_company` | 10 | 100.0% | 100.0% |
| `calculation` | 10 | 100.0% | 100.0% |
| `financial_domain` | 12 | 100.0% | 100.0% |
| `ambiguous` | 8 | 100.0% | 100.0% |
| `error_recovery` | 8 | 87.5% | 87.5% |

---

## 3. Failure Taxonomy

The framework categorizes potential failure modes into 7 standard buckets:
1. `SCHEMA_RETRIEVAL_FAILURE`: Failed to retrieve relevant tables or concepts.
2. `SQL_GENERATION_FAILURE`: Failed to generate candidate SQL.
3. `SQL_VALIDATION_FAILURE`: Rejected by SQLGlot AST (dangerous statement, Cartesian join, unapproved table).
4. `SQL_EXECUTION_FAILURE`: Runtime database execution error.
5. `FINANCIAL_INTERPRETATION_FAILURE`: Mixed reporting types, unhandled restatements, duplicate rows.
6. `RESULT_VERIFICATION_FAILURE`: Inconsistent units or empty result sets.
7. `ANSWER_GENERATION_FAILURE`: Failure to synthesize grounded explanation.

---

## 4. How to Reproduce Evaluation

To run the automated benchmark locally:

```bash
python -m evaluation.evaluator
```

This updates `evaluation/reports/evaluation_report.json` and `evaluation/reports/evaluation_report.md`.
