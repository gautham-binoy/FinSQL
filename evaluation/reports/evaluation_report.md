# FinSQL Agent vs. Baseline Evaluation Report

**Date**: 2026-09-11T17:35:11Z  
**Total Questions Evaluated**: 100

## Executive Benchmark Summary

| Metric | Baseline Text-to-SQL | FinSQL Agent (Ours) | Improvement (Delta) |
| :--- | :---: | :---: | :---: |
| **SQL Execution Accuracy** | 100.0% | **99.0%** | **+-1.0%** |
| **Result Accuracy** | 60.0% | **99.0%** | **+39.0%** |
| **Financial Correctness** | 60.0% | **99.0%** | **+39.0%** |
| **Schema Retrieval Accuracy** | N/A (0%) | **100.0%** | **+100.0%** |
| **Error Recovery Rate** | 0% (No Recovery) | **87.5%** | **+87.5%** |
| **Average Latency** | 0.16 ms | 178.72 ms | (Includes AST & RAG) |
| **Average Retries** | 0 | 0.1 | Self-healing |

## Performance by Category (FinSQL Agent)

| Category | Questions | SQL Execution | Result Accuracy |
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
