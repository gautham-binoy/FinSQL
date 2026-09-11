# FinSQL Agent — Agentic Text-to-SQL for Financial Data

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-emerald.svg)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/React-19.2%2B-cyan.svg)](https://react.dev/)
[![Tailwind CSS v4](https://img.shields.io/badge/TailwindCSS-v4.3-38bdf8.svg)](https://tailwindcss.com/)
[![Evaluation Benchmark](https://img.shields.io/badge/Benchmark_Accuracy-99.0%25-brightgreen.svg)](#12-evaluation)

> **FinSQL Agent** is a production-style agentic Text-to-SQL system engineered specifically for complex, multi-year financial statement datasets. It implements a multi-stage pipeline: **Natural Language → Question Analysis → Vector Schema Retrieval → Grounded SQL Generation → SQLGlot AST Safety Validation → Safe Execution → Self-Healing Repair Loop → Financial Result Verification → Grounded Answer Synthesis**.

---

## 1. Problem Statement

Generic Text-to-SQL systems fail drastically on financial datasets. Naive LLM pipelines dump the entire database schema into the prompt, resulting in severe issues:
1. **Schema Explosion**: Real financial datasets (e.g. SEC EDGAR / XBRL) contain thousands of measurement concepts, duplicate line items, and non-standard reporting hierarchies.
2. **Fiscal Year Discrepancies**: Corporations do not all report on a December 31 calendar year (e.g. Apple ends in late September, Microsoft in June, Nvidia in January).
3. **Restatements & Amended Filings**: Companies restate prior-year figures. Naive queries blend original and restated numbers, returning duplicated or misleading records.
4. **Consolidated vs. Standalone Reporting**: Blending parent entity numbers with group consolidated figures distorts financial analysis.
5. **No Recovery Feedback**: When generic LLMs generate invalid columns or syntax errors, traditional pipelines crash instead of self-healing.

---

## 2. Solution

FinSQL Agent solves these problems by treating Text-to-SQL as an **agentic observability and control pipeline**:
- **Schema Pruning via Vector Search**: Uses vector embeddings to retrieve only the relevant tables, columns, and metric definitions needed for the specific question.
- **AST-Based Safety Validation**: SQLGlot inspects the query Abstract Syntax Tree (AST) to enforce read-only semantics, table whitelists, and Cartesian join prevention.
- **Agentic Self-Healing Loop**: If a query fails validation or execution, the system diagnoses the database error message and synthesizes a corrected query (up to 3 retries).
- **Financial Result Verification**: Scans output rows for empty results, conflicting restatements, and unit mismatches before generating an answer.
- **Strict Grounding**: The LLM synthesizes natural language explanations strictly from executed database rows, eliminating hallucinations.

---

## 3. Architecture

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

## 4. Features

- **Agentic Self-Healing (87.5% Recovery Rate)**: Automatically fixes syntax, column, or filter errors through iterative feedback.
- **Vector Schema Retrieval (pgvector)**: Injects minimal, high-precision schema context rather than entire database dumps.
- **Financial Domain Logic**: Natively respects fiscal year calendars, consolidated reporting, non-restated flags, and unit conversions.
- **SQLGlot AST Guardrails**: Hard guarantees against `DROP`, `DELETE`, `UPDATE`, `INSERT`, multi-statement injections, and unapproved tables.
- **Dynamic Visualizations**: Auto-selects between Bar Charts (comparisons), Line Charts (trends), and KPI Metric Cards.
- **Scientific Benchmark Suite**: 100 benchmark questions comparing Baseline vs FinSQL Agent with reproducible statistics.
- **Zero-Config Dual Database**: Supports PostgreSQL with `pgvector` for production, and an automatic SQLite fallback for offline demo testing.

---

## 5. Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Backend Framework** | FastAPI (Python 3.11+) | Asynchronous REST API, dependency injection, CORS |
| **Data Validation** | Pydantic v2 / Pydantic-Settings | Strongly-typed request/response models & settings |
| **ORM & Database** | SQLAlchemy 2.0 | High-performance relational queries and migrations |
| **Primary Database** | PostgreSQL 16 + pgvector | Production relational storage with vector similarity index |
| **Fallback Database** | SQLite 3 | Local zero-dependency testing with in-memory cosine search |
| **SQL AST Parser** | SQLGlot | AST parsing, validation, read-only enforcement, dialect transpilation |
| **AI / LLM** | Google Gemini (`gemini-2.5-flash`) | Semantic analysis, SQL generation, and grounded answer synthesis |
| **Embeddings** | Google `text-embedding-004` | 768-dimensional schema and concept embeddings |
| **Frontend Framework** | React 19 + TypeScript + Vite | High-performance modern dashboard |
| **Styling** | Tailwind CSS v4 | Curated dark-mode financial analytics interface |
| **Visualizations** | Recharts | Dynamic responsive time-series and comparative charts |
| **Icons** | Lucide React | Clean, modern iconography |

---

## 6. System Workflow

1. **Question Analysis**: The user inputs a query like *"What was Apple's revenue growth between 2022 and 2023?"*. The analyzer identifies entities (`Apple Inc.`), concept (`Revenue`), years (`2022`, `2023`), and operation (`growth` / `percentage_change`).
2. **Schema Retrieval**: Vector search matches the question against the schema catalog, retrieving `companies`, `financial_facts`, `Revenue`, and related column definitions.
3. **SQL Generation**: Constructs a CTE-based PostgreSQL query adhering to consolidated and non-restated rules.
4. **AST Validation**: SQLGlot verifies the query is read-only, checks table whitelisting, and verifies join semantics.
5. **Execution & Repair**: The query executes against the database. If an execution or AST error occurs, `SQLRepairAgent` catches the error message and repairs the query.
6. **Result Verification**: Verifies non-empty results, unit compatibility, and lack of duplicate rows.
7. **Answer Synthesis**: Formats numbers ($383.29B), calculates percentage changes (-2.80%), recommends a bar chart, and provides full provenance.

---

## 7. Database Schema

The database models audited SEC Form 10-K financial records:
- **`companies`**: `company_id`, `ticker` (AAPL, MSFT, AMZN, GOOGL, TSLA, NVDA, META), `company_name`, `industry`, `sector`, `country`.
- **`financial_facts`**: `id`, `company_id`, `concept`, `value`, `unit`, `fiscal_year` (2020–2025), `fiscal_period` (`FY`), `period_start`, `period_end`, `filing_date`, `statement_type`, `reporting_type` (`consolidated` vs `standalone`), `is_restated` (boolean).
- **`financial_concepts`**: Catalog of 11 concepts (`Revenue`, `NetIncome`, `GrossProfit`, `OperatingIncome`, `TotalAssets`, `TotalLiabilities`, `CashAndCashEquivalents`, `EarningsPerShare`, etc.) with synonyms and units.
- **`schema_catalog`**: Embeddings of tables, columns, and concepts for vector retrieval.

---

## 8. Schema Retrieval

Rather than sending the whole database schema to the LLM (which wastes context and increases hallucinations), `SchemaRetriever` embeds the user question and computes cosine similarity against `schema_catalog`. Relevant items receive entity-based ranking boosts. The LLM receives only the tables and columns necessary to answer the question.

---

## 9. Agentic SQL Recovery

When a generated query fails during AST validation or database execution, the system does not fail:
```text
Faulty SQL -> Exception -> Error Diagnosed -> LLM / Heuristic Repair -> Re-validated -> Executed
```
For example, if a query references `f.fiscalYear` instead of `f.fiscal_year`, `SQLRepairAgent` diagnoses `no such column: f.fiscalYear`, applies `CORRECTED_COLUMN_NAME`, and re-executes cleanly on Attempt #2.

---

## 10. Financial Domain Handling

- **Fiscal vs. Calendar Year**: Queries explicitly filter by `fiscal_year` and `fiscal_period = 'FY'`.
- **Restatements**: Automatically filters `is_restated = FALSE` to prevent duplicate counting.
- **Consolidated Scope**: Filters `reporting_type = 'consolidated'` unless standalone is requested.
- **Incompatible Units**: Never adds or compares incompatible units (e.g. shares vs USD).

---

## 11. Baseline vs Improved System

- **Baseline Text-to-SQL**: Direct prompt `Question -> LLM -> SQL -> Database`. Has no schema retrieval, no AST safety validation, no error recovery, and no financial domain checks. Returns duplicate rows on restatements.
- **FinSQL Agent**: End-to-end multi-stage pipeline with vector retrieval, AST guardrails, self-healing retries, and domain verification.

---

## 12. Evaluation

Empirical benchmark evaluated over **100 realistic financial questions** across 9 categories:

| Metric | Baseline Text-to-SQL | FinSQL Agent (Ours) | Improvement (Delta) |
| :--- | :---: | :---: | :---: |
| **SQL Execution Accuracy** | 100.0% | **99.0%** | -1.0% |
| **Result Accuracy** | 60.0% | **99.0%** | **+39.0%** |
| **Financial Correctness** | 60.0% | **99.0%** | **+39.0%** |
| **Schema Retrieval Accuracy** | N/A (0%) | **100.0%** | **+100.0%** |
| **Error Recovery Rate** | 0% (No Recovery) | **87.5%** | **+87.5%** |
| **Average Latency** | 0.16 ms | 178.72 ms | (Includes AST & RAG) |
| **Average Retries** | 0 | 0.1 | Self-healing |

### Category Breakdown (FinSQL Agent)
- `simple_lookup` (15 questions): **100.0%**
- `comparison` (15 questions): **100.0%**
- `aggregation` (10 questions): **100.0%**
- `time_series` (12 questions): **100.0%**
- `multi_company` (10 questions): **100.0%**
- `calculation` (10 questions): **100.0%**
- `financial_domain` (12 questions): **100.0%**
- `ambiguous` (8 questions): **100.0%**
- `error_recovery` (8 questions): **87.5%**

---

## 13. Failure Analysis

FinSQL Agent incorporates a 7-stage failure taxonomy:
- `SCHEMA_RETRIEVAL_FAILURE`
- `SQL_GENERATION_FAILURE`
- `SQL_VALIDATION_FAILURE`
- `SQL_EXECUTION_FAILURE`
- `FINANCIAL_INTERPRETATION_FAILURE`
- `RESULT_VERIFICATION_FAILURE`
- `ANSWER_GENERATION_FAILURE`

---

## 14. Installation

```bash
# Clone the repository
git clone https://github.com/gautham-binoy/Prompt_SQL.git
cd Prompt_SQL

# Create Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt

# Install frontend dependencies
cd frontend && npm install && cd ..
```

---

## 15. Environment Variables

Create `.env` (copy from `.env.example`):

```env
# Google Gemini Configuration
GEMINI_API_KEY=your_api_key_here
MODEL_NAME=gemini-2.5-flash
EMBEDDING_MODEL=text-embedding-004

# Database Configuration
DATABASE_URL=sqlite:///./data/finsql.db
# Or for PostgreSQL + pgvector:
# DATABASE_URL=postgresql://finsql:finsqlpass@localhost:5432/finsqldb

# Execution Limits
MAX_SQL_RETRIES=3
QUERY_TIMEOUT_SECONDS=10
MAX_RESULT_ROWS=1000
DEMO_MODE=false
```

---

## 16. Running the Backend

```bash
# 1. Initialize and seed database
python scripts/init_db.py
python scripts/seed_data.py
python scripts/build_schema_embeddings.py

# 2. Start FastAPI server
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

Interactive OpenAPI docs: `http://127.0.0.1:8000/docs`

---

## 17. Running the Frontend

```bash
cd frontend
npm run dev
```

Dashboard opens at: `http://127.0.0.1:5173`

---

## 18. Docker

To run with PostgreSQL and pgvector via Docker Compose:

```bash
docker compose up -d
```

---

## 19. Example Questions

1. *"What was Apple's revenue in 2023?"*
2. *"Compare Apple's revenue with Microsoft's revenue in 2023."*
3. *"Show Apple's revenue from 2020 to 2025."*
4. *"Which company had the highest revenue in 2023?"*
5. *"What was Microsoft's net income in 2023?"*
6. *"Compare the net income of Apple and Microsoft from 2021 to 2023."*
7. *"What was Apple's revenue growth between 2022 and 2023?"*
8. *"What was the average revenue of the companies in 2023?"*
9. *"Which company had the highest net income margin in 2023?"*
10. *"Give me Apple's revenue and net income for the last five fiscal years."*
11. *"Show Apple's consolidated revenue in 2023 excluding restatements."*
12. *"Compare cash and cash equivalents between Google and Microsoft in 2023."*
13. *"Which company had the highest total assets in 2023?"*
14. *"What was Nvidia's revenue in 2024?"*
15. *"Show Tesla's net income from 2020 to 2025."*

---

## 20. API Documentation

- `POST /api/query`: Execute natural language financial query (FinSQL Agent).
- `POST /api/query/baseline`: Execute via Baseline Text-to-SQL.
- `GET /api/health`: Database connectivity, facts count, and AI status.
- `GET /api/schema`: Catalog of tables, columns, companies, and concepts.
- `GET /api/examples`: Curated financial example queries.
- `GET /api/metrics`: Live 100-question evaluation report.

---

## 21. Testing

Run backend unit and integration tests:

```bash
pytest backend/tests/ -v
```

All 23 test suites verify analyzer, validator, retriever, executor, repair agent, result verifier, and API endpoints.

---

## 22. Running the Evaluation Suite

To reproduce the benchmark:

```bash
python -m evaluation.evaluator
```

Outputs: `evaluation/reports/evaluation_report.json` and `evaluation/reports/evaluation_report.md`.

---

## 23. Future Improvements & BigQuery Scalability

- **SEC EDGAR Pipeline**: Ingest quarterly 10-Q and 8-K filings directly via SEC EDGAR public APIs.
- **BigQuery Warehouse**: Transition from PostgreSQL to Google BigQuery for petabyte-scale financial analytics with partitioned table clustering.
- **Multi-Turn Financial Chat**: Enable conversational context retention across consecutive questions.

---

## 24. Limitations

- **Demo Seed Scope**: Pre-seeded with 7 major corporations (Apple, Microsoft, Amazon, Alphabet, Tesla, Nvidia, Meta) across 2020–2025.
- **Quarterly Granularity**: Primary demonstration focuses on annual Form 10-K filings (`fiscal_period = 'FY'`).

---

## 25. Security & Safety

- **Strict Read-Only SQL**: SQLGlot rejects all mutation and DDL expressions (`DROP`, `DELETE`, `INSERT`, `UPDATE`).
- **Table Whitelisting**: Only approved tables (`companies`, `financial_facts`, `financial_concepts`) are accessible.
- **No Arbitrary Execution**: Queries undergo AST validation before reaching database engines.
- **Zero Secret Exposure**: API keys are isolated in `.env` and never logged or serialized to the client.

---

## 26. Project Motivation

Financial data questions are high-stakes. In business and finance, an incorrect SQL query that combines restated filings or blends standalone and consolidated numbers can lead to millions of dollars in miscalculated earnings. FinSQL Agent bridges natural language with verified accounting precision.

---

## 27. Internship Relevance

This project demonstrates:
- **Production AI Engineering**: LLM structured outputs, JSON validation, and prompt engineering with Gemini.
- **Agentic Workflows**: Multi-step reasoning, self-healing repair loops, and execution feedback.
- **RAG & Vector Search**: Dynamic schema selection via vector embeddings (pgvector).
- **Relational Database Design**: Complex CTEs, self-joins, window functions, and indexing.
- **Robust Evaluation**: 100-question scientific benchmark comparing baseline vs improved architecture.
