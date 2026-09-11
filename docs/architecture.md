# FinSQL Agent: Architecture Overview

## 1. System Philosophy

Financial Text-to-SQL is fundamentally different from generic Text-to-SQL. Financial datasets (such as SEC EDGAR 10-K/10-Q filings, XBRL taxonomies, or corporate data warehouses) present unique engineering traps:
- Schema explosion (thousands of concepts, conflicting tags, varying fiscal years).
- Ambiguous reporting types (`consolidated` vs `standalone`).
- Restatements (`is_restated = TRUE` vs `is_restated = FALSE`).
- Accounting arithmetic across years (growth rates, margins) that require multi-table CTE joins.

FinSQL Agent rejects the naive "Prompt-to-SQL" approach in favor of an **agentic, multi-stage pipeline**:

```text
               ┌───────────────────────────┐
               │   Natural Language Query  │
               └─────────────┬─────────────┘
                             │
                             ▼
               ┌───────────────────────────┐
               │     Question Analyzer     │
               │  Entity/Metric/Period/Op  │
               └─────────────┬─────────────┘
                             │
                             ▼
               ┌───────────────────────────┐
               │    Schema Retriever       │
               │  pgvector / Hybrid Search │
               └─────────────┬─────────────┘
                             │
                             ▼
               ┌───────────────────────────┐
               │    Gemini SQL Generator   │
               │  Constrained JSON Output  │
               └─────────────┬─────────────┘
                             │
                             ▼
               ┌───────────────────────────┐
               │      SQL AST Validator    │
               │     SQLGlot AST Parsing   │
               └─────────────┬─────────────┘
                             │
                       Valid & Safe?
                       /           \
                     No             Yes
                     │               │
                     ▼               ▼
               ┌───────────┐  ┌─────────────┐
               │ Repair    │  │ PostgreSQL  │
               │ Agent     │  │ / SQLite    │
               └─────┬─────┘  └──────┬──────┘
                     │               │
                     └───────────────┤ (On DB Error)
                                     ▼
                              ┌─────────────┐
                              │ Result      │
                              │ Verifier    │
                              │ (Fin Checks)│
                              └──────┬──────┘
                                     │
                                     ▼
                              ┌─────────────┐
                              │ Grounded    │
                              │ Answer &    │
                              │ Provenance  │
                              └─────────────┘
```

---

## 2. Component Breakdown

### 2.1 Question Analyzer (`backend/app/agents/question_analyzer.py`)
Extracts structured intent before touching the database or generating code:
- **Entities**: Resolves company names to tickers (`Apple` -> `AAPL`, `Alphabet` -> `GOOGL`).
- **Metrics**: Maps natural language accounting synonyms to standardized concept tags (`sales` / `turnover` -> `Revenue`, `profit` -> `NetIncome`).
- **Time Periods**: Disambiguates single years (`2023`), ranges (`2020-2025`), or relative historical periods (`last five fiscal years`).
- **Operations**: Categorizes intent into `lookup`, `comparison`, `ranking`, `aggregation`, `trend`, or `growth` / `margin` calculations.

### 2.2 Schema Retriever (`backend/app/retrieval/schema_retriever.py`)
Prevents token-window pollution and hallucinations by dynamically retrieving only the relevant tables, columns, and concepts needed for the question:
- Stores 768-dimensional embeddings of all tables, columns, synonyms, and financial concepts in PostgreSQL (`pgvector`) or SQLite fallback.
- Computes cosine similarity combined with question entity/metric boosting.
- Injects a compact schema summary containing only approved tables (`companies`, `financial_facts`, `financial_concepts`).

### 2.3 SQL Generator (`backend/app/agents/sql_generator.py`)
Constructs parameterized read-only queries adhering to strict financial conventions:
- Enforces `f.reporting_type = 'consolidated'` unless standalone is explicitly requested.
- Enforces `f.is_restated = FALSE` unless historical amendments are queried.
- Employs Common Table Expressions (CTEs) for period growth and margin rankings.

### 2.4 SQL Validator (`backend/app/validation/sql_validator.py`)
Uses SQLGlot AST inspection:
- Enforces read-only statements (`SELECT`, `WITH`).
- Automatically rejects any DDL/DML mutations (`INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `TRUNCATE`).
- Enforces table whitelisting and detects Cartesian products.

### 2.5 SQL Repair Agent (`backend/app/agents/sql_repair.py`)
Implements an agentic self-healing loop:
- Catches database errors (e.g. `no such column: f.fiscalYear`) or AST validation failures.
- Synthesizes corrected queries using diagnostic feedback up to `MAX_SQL_RETRIES = 3`.

### 2.6 Result Verifier (`backend/app/validation/result_verifier.py`)
Performs domain-specific sanity checks on executed records:
- Flags empty result sets.
- Detects duplicate records arising from mixed restatement filings or reporting scopes.
- Asserts unit compatibility (USD vs shares vs ratios).

### 2.7 Answer Generator (`backend/app/agents/answer_generator.py`)
Translates structured database records into executive-grade financial summaries, KPI callouts, and chart recommendations without fabricating data.

---

## 3. Extensibility to SEC EDGAR on BigQuery

In enterprise cloud deployments:
```text
React Dashboard
      │
      ▼
FastAPI (Google Cloud Run)
      │
      ▼
Schema Retrieval (Vertex AI Vector Search / Cloud SQL pgvector)
      │
      ▼
SQL Generation (Gemini 2.5)
      │
      ▼
Google BigQuery (SEC EDGAR / XBRL Public Dataset)
```
BigQuery natively supports petabyte-scale financial facts with partitioned tables by `filing_date` and `fiscal_year`.
