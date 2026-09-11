# Agent Workflow & Error Recovery Feedback Loop

## 1. Request Lifecycle Overview

```text
User Question
    │
    ▼
[Stage 1: Question Analysis]
    │ Extracts {entities, tickers, metrics, time_period, operation, filters}
    ▼
[Stage 2: Schema Retrieval]
    │ Queries SchemaCatalog using cosine similarity & entity boosting
    │ Returns only relevant tables, columns, and metric definitions
    ▼
[Stage 3: SQL Generation & AST Validation Loop]
    │ LLM / Deterministic Generator produces candidate SQL
    │ SQLGlot parses AST:
    │   ├─ If AST invalid or mutation detected -> Send to SQLRepairAgent
    │   └─ If Valid -> Execute query against DB
    │ Execution Result:
    │   ├─ If DB syntax/column error -> Send to SQLRepairAgent (Max 3 Retries)
    │   └─ If DB succeeds -> Pass rows to ResultVerifier
    ▼
[Stage 4: Financial Result Verification]
    │ Checks for 0 rows, duplicate filings, restatement conflicts, incompatible units
    │   ├─ If critical anomaly -> Send to SQLRepairAgent to relax filters
    │   └─ If verified -> Proceed to Answer Generation
    ▼
[Stage 5: Grounded Answer Generation]
    │ Produces executive summary, KPI badges, chart recommendation, and provenance
```

---

## 2. The Agentic Feedback Repair Loop

Unlike standard single-shot Text-to-SQL demonstrations that fail when a database query errors, FinSQL Agent features an active repair loop:

```python
attempt_count = 0
while attempt_count <= MAX_SQL_RETRIES:
    attempt_count += 1
    
    # 1. AST Validation
    val = SQLValidator.validate(current_sql)
    if not val["valid"]:
        current_sql = SQLRepairAgent.repair(question, current_sql, val["reason"], schema)["sql"]
        continue
        
    # 2. Database Execution
    exec_res = SQLExecutor.execute_query(current_sql)
    if not exec_res["success"]:
        current_sql = SQLRepairAgent.repair(question, current_sql, exec_res["message"], schema)["sql"]
        continue
        
    # 3. Financial Domain Verification
    verif = ResultVerifier.verify(exec_res["rows"], exec_res["columns"], analysis)
    if verif["needs_repair"]:
        current_sql = SQLRepairAgent.repair(question, current_sql, verif["repair_reason"], schema)["sql"]
        continue
        
    break
```

### Repair Strategies
1. **`CORRECTED_COLUMN_NAME`**: Repairs case mismatches or non-existent columns (e.g. `fiscalYear` -> `fiscal_year`).
2. **`CORRECTED_TABLE_NAME`**: Fixes pluralization or alias mistakes (e.g. `FROM company` -> `FROM companies`).
3. **`FIXED_SYNTAX_QUOTES`**: Replaces improper double quotes on string literals with single quotes.
4. **`RELAXED_RESTATEMENT_FILTER`**: Automatically adjusts filters when over-filtering causes 0 rows.
