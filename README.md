# FinSQL Agent

> **Agentic Text-to-SQL for Financial Data**

[![Live Demo](https://img.shields.io/badge/Live_Demo-Render.com-00c7b7?style=for-the-badge&logo=render&logoColor=white)](https://prompt-sql-1kuq.onrender.com/)
[![Documentation](https://img.shields.io/badge/Architecture_Docs-docs%2F-blue?style=for-the-badge&logo=googledocs&logoColor=white)](docs/architecture.md)
[![API Docs](https://img.shields.io/badge/API_Docs-FastAPI_Swagger-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://prompt-sql-1kuq.onrender.com/docs)
[![License](https://img.shields.io/badge/License-MIT-amber?style=for-the-badge)](LICENSE)

[Live Demo](https://prompt-sql-1kuq.onrender.com/) • [Documentation](docs/architecture.md) • [API Docs](https://prompt-sql-1kuq.onrender.com/docs) • [License](LICENSE)

---

## 1. Overview

**FinSQL Agent** is a production-oriented, agentic Text-to-SQL engineering project built by a Computer Engineering student to solve the problem of querying complex corporate financial statement datasets using natural language.

### Quick Pitch
> Most Text-to-SQL projects are single-shot wrappers: they feed an entire database schema to an LLM, hope the generated query is valid, and crash when an error occurs. **FinSQL Agent treats Text-to-SQL as an autonomous reasoning, retrieval, validation, execution, and verification loop.** It extracts structured financial intent, retrieves only relevant schema elements using vector search, verifies SQL Abstract Syntax Trees (AST) for safety, executes queries with timeout guardrails, automatically repairs errors via a self-healing diagnostic loop, verifies financial domain rules (restatements, reporting scope, units), and synthesizes grounded, hallucination-free answers.

```text
Natural Language ──► Question Analysis ──► Vector Schema RAG ──► SQL Generation ──► AST Guardrails
                                                                                           │
Grounded Answer ◄── Financial Verification ◄── Error Repair Loop ◄── Execution Engine ◄────┘
```

### Quick Q&A for Recruiters & Engineers

1. **What is this?**  
   An end-to-end agentic Text-to-SQL pipeline designed specifically for corporate financial statement analysis (Form 10-K filings).
2. **What problem does it solve?**  
   It enables non-technical business stakeholders, investors, and analysts to ask complex quantitative questions across multiple companies and fiscal years without writing manual SQL joins, CTEs, or restatement filters.
3. **Why is financial Text-to-SQL difficult?**  
   Corporate accounting involves non-standard fiscal year-ends, historical restatements, consolidated vs. standalone accounts, multi-table arithmetic, and thousands of taxonomy tags.
4. **What makes this different from simply asking an LLM to generate SQL?**  
   Raw LLMs hallucinate column names, fail on syntax errors, combine duplicate restated rows, and cannot verify financial correctness. FinSQL Agent surrounds the LLM with vector schema pruning, SQLGlot AST guardrails, self-healing diagnostic recovery, and accounting result verification.
5. **What did I actually build?**  
   A complete full-stack agentic architecture: an asynchronous FastAPI backend, modular agent orchestration, vector retrieval with `text-embedding-004`, an AST security validator, a self-healing repair agent, a 100-question empirical evaluation framework, and an interactive React 19 + TypeScript analytics dashboard.

### Technical Highlights
- **Agentic Architecture**: Closed-loop execution with self-healing feedback (**87.5% error recovery rate** on benchmark error cases).
- **RAG-Driven Schema Pruning**: 768-dimensional vector embeddings (`text-embedding-004`) select only relevant tables and columns, eliminating prompt context bloat.
- **Structural AST Security**: SQLGlot Abstract Syntax Tree analysis strictly blocks destructive operations (`DROP`, `DELETE`, `UPDATE`, `INSERT`) and enforces table whitelists.
- **Financial Domain Intelligence**: Resolves fiscal calendars (e.g. Apple September vs. Microsoft June), isolates restated filings (`is_restated`), and separates consolidated from standalone accounts.
- **Empirical 100-Question Benchmark**: Tested against 100 curated financial queries across 9 categories, achieving **99.0% result accuracy** (a **+39.0% improvement** over a baseline LLM-to-SQL prompt).
- **Full-Stack Implementation**: FastAPI asynchronous backend paired with a modern React 19 + TypeScript + Tailwind CSS v4 analytics dashboard.

### What I Built (Engineering Ownership)

To demonstrate practical agentic AI and software engineering skills, I designed and implemented every tier of this system:
- **Backend REST API**: Asynchronous endpoints built in FastAPI (`/api/query`, `/api/query/baseline`, `/api/schema`, `/api/examples`, `/api/metrics`, `/api/health`) with Pydantic request/response validation.
- **Agent Orchestration**: Controller (`FinSQLOrchestrator`) coordinating multi-stage state transitions, execution timing, and structured trace telemetry.
- **Schema Retrieval Engine**: Hybrid cosine similarity retriever indexing tables, columns, and financial concepts to prune prompt context by >80%.
- **Constrained SQL Generator**: Gemini prompt engineering enforcing strict join relationships, fiscal year rules, and consolidated reporting defaults.
- **AST Validation Guardrails**: Parser utilizing SQLGlot to structurally enforce read-only `SELECT`/`WITH` statements and reject SQL mutations.
- **Execution Sandbox**: Parameterized database executor with statement timeouts (`QUERY_TIMEOUT_SECONDS = 10`) and maximum row caps (`MAX_RESULT_ROWS = 1000`).
- **Self-Healing Repair Loop**: Autonomous diagnostic handler that catches runtime database exceptions, classifies error types, and synthesizes corrected SQL.
- **Result Verification Engine**: Post-execution accounting validator that checks for empty sets, duplicate filing records, and unit mismatches.
- **Frontend Visualization & Observability**: Interactive single-page dashboard built in React 19, TypeScript, and Vite, featuring dynamic Recharts visualizations and a live step-by-step agent execution trace.
- **Evaluation Framework**: Automated evaluation suite (`evaluation/evaluator.py`) running 100 curated financial questions across 9 categories against both Baseline and Agent pipelines.
- **Automated Testing**: 23 unit and integration tests (`pytest backend/tests/`) covering API endpoints, AST validation, schema retrieval, error repair, and result verification.
- **Deployment & Packaging**: Docker Compose configuration for PostgreSQL 16 + pgvector, plus a one-click deployment blueprint for Render.com.

### Engineering Decisions

- **Why Schema Retrieval?** Feeding an entire database schema to an LLM wastes token context, introduces irrelevant tables, and increases hallucination rates. Vector retrieval injects only the specific tables, columns, and concept tags needed for the query.
- **Why AST Validation?** Regular expressions are brittle and easily bypassed. Parsing the SQL into an Abstract Syntax Tree (AST) via SQLGlot ensures deterministic rejection of mutations (`DROP`, `DELETE`, `UPDATE`) and unauthorized tables before execution.
- **Why Execution Feedback?** Syntactically valid queries can still fail at runtime due to column name discrepancies or filter errors. Passing the exact database error back to the model enables autonomous self-correction without user intervention.
- **Why Result Verification?** A query can execute successfully with exit code 0 while producing an incorrect financial answer (e.g. summing restated and non-restated filings). Post-execution validation guarantees accounting integrity.
- **Why a Calibrated Local Dataset?** Developing on a calibrated, reproducible dataset (7 major enterprises, 2020–2025 Form 10-K data) enables deterministic evaluation and fast local experimentation, while strictly adhering to the schema needed for future large-scale SEC EDGAR/BigQuery integration.

### Skills Demonstrated

- **Languages & Frameworks**: Python 3.11+, TypeScript, SQL, React 19, FastAPI, Vite, Node.js.
- **AI & Agent Engineering**: Agentic workflows, self-healing diagnostic loops, Google Gemini API, prompt engineering, evaluation benchmarking.
- **RAG & Vector Retrieval**: Embedding generation (`text-embedding-004`), vector similarity search, pgvector, in-memory cosine ranking.
- **Database & Data Modeling**: PostgreSQL 16, SQLite 3, SQLAlchemy ORM, relational schema design, Common Table Expressions (CTEs), Form 10-K accounting taxonomy.
- **Security & Code Analysis**: SQLGlot Abstract Syntax Tree (AST) validation, read-only guardrails, safe parameterized execution.
- **Frontend & Visualization**: Tailwind CSS v4, Recharts, Lucide React, responsive UI design, agent execution tracing.
- **Software Engineering & DevOps**: REST API design, Pydantic validation, Pytest unit/integration testing, Docker, Docker Compose, Render cloud deployment.

---

## 2. Problem Statement

Financial analysts, executives, auditors, and investors frequently need answers to quantitative questions:
- *"What was Apple's revenue growth between 2022 and 2023?"*
- *"Which company had the highest net income margin in 2023?"*
- *"Compare Microsoft and Alphabet operating income over the last five fiscal years."*

Non-technical stakeholders cannot write complex SQL queries involving Common Table Expressions (CTEs), multi-year period joins, and restatement exclusions. Meanwhile, ordinary LLM chat assistants cannot reliably answer these questions directly because:
1. They lack direct access to verified database records.
2. They hallucinate numbers and growth percentages.
3. When prompted to write SQL, they invent non-existent column names, confuse fiscal and calendar years, and combine restated filings.

---

## 3. Why Financial Text-to-SQL Is Difficult

Financial statement databases present domain-specific obstacles that break conventional Text-to-SQL systems:

1. **Schema & Tag Explosion**: Corporate reporting taxonomies (e.g., US-GAAP on SEC EDGAR) contain thousands of overlapping measurement concepts (e.g., `Revenues`, `SalesRevenueNet`, `TotalRevenuesAndOtherIncome`). Sending the whole schema to an LLM degrades reasoning.
2. **Fiscal Year vs. Calendar Year**: Corporate fiscal years often do not end on December 31. Apple's fiscal year ends on the last Saturday of September; Microsoft's ends June 30; Nvidia's ends in late January. Naive calendar date filtering returns incomplete or wrong periods.
3. **Restatements & Amended Filings**: Companies restate prior-year figures in subsequent Form 10-K filings. Queries that fail to filter `is_restated` retrieve duplicate rows for the same year, corrupting sums and averages.
4. **Consolidated vs. Standalone Reporting**: Corporations report consolidated group accounts alongside unconsolidated parent legal entity accounts (`reporting_type = 'consolidated'` vs. `'standalone'`). Blending them distorts corporate comparisons.
5. **Multi-Step Accounting Arithmetic**: Computing financial metrics (e.g., Net Income Margin = Net Income / Revenue × 100, or Year-over-Year Growth = (Val₂ - Val₁) / Val₁ × 100) requires complex SQL CTEs and multi-table self-joins.
6. **Zero Tolerance for Hallucination**: An invented dollar value or incorrect margin percentage is unacceptable in corporate decision-making. Answers must be 100% grounded in verified execution results.

### Why This Project Matters

Standard Text-to-SQL benchmarks (like Spider or BIRD) evaluate general databases (e.g. music stores, flights, university courses) where schemas are relatively clean and values are simple scalars. In corporate finance, naive Text-to-SQL fails silently: a query might run without errors, but return duplicate restated numbers, blend unconsolidated parent entities with consolidated group figures, or misalign fiscal years.

FinSQL Agent addresses these challenges directly:
- **Pruning Schema Context**: Vector schema retrieval selects only relevant tables and concepts, preventing prompt overflow and hallucinated column names.
- **Enforcing Accounting Disambiguation**: Prompt guardrails explicitly differentiate fiscal periods (`fiscal_period = 'FY'`), reporting types (`reporting_type = 'consolidated'`), and amendment flags (`is_restated = FALSE`).
- **Validating Structure with ASTs**: SQLGlot ensures queries are strictly read-only prior to execution.
- **Autonomous Error Recovery**: Instead of failing when a syntax or column error occurs, the agentic repair loop uses execution feedback to diagnose and self-correct queries.
- **Verifying Numerical Results**: Post-execution sanity checks ensure the returned data is logically and financially sound before generating the final answer.

---

## 4. Solution

FinSQL Agent addresses these issues through a disciplined, multi-stage engineering pipeline:

- **Implemented Prototype**: A fully functional, locally reproducible agent running on FastAPI, SQLite / PostgreSQL (`pgvector`), and a React dashboard seeded with calibrated Form 10-K financial records (2020–2025) for 7 major enterprises.
- **Dynamic Context Retrieval**: Injects only the relevant table schemas, column descriptions, and concept tags needed for the specific question.
- **Deterministic Guardrails**: Enforces read-only execution constraints via AST inspection before SQL reaches the database engine.
- **Diagnostic Feedback Loop**: Captures runtime SQL execution exceptions and passes structured error context to the repair agent to synthesize corrected queries.
- **Accounting Verification**: Inspects execution result sets for duplicate filings, incompatible units (e.g., summing USD with per-share data), or empty results before generating the final user-facing response.

---

## 5. Key Features

- **Automated Self-Healing Loop**: Automatically corrects syntax, column, or filter errors through iterative feedback (tested up to `MAX_SQL_RETRIES = 3`).
- **Vector Schema Pruning**: Embeds table metadata and accounting concepts with `text-embedding-004`, reducing injected prompt tokens by over 80%.
- **AST Security Guardrails**: Uses SQLGlot to parse query syntax trees, enforcing read-only permissions and table whitelisting.
- **Domain-Specific Accounting Rules**: Built-in logic for fiscal calendars, consolidated scopes, and restatement deduplication.
- **Interactive Financial Visualizations**: Auto-selects between Bar Charts (comparisons), Line Charts (multi-year trends), and KPI Metric Cards using Recharts.
- **Agent Observability Trace**: Real-time frontend timeline displaying execution duration, extracted entities, and retrieval similarity scores for every stage.
- **Dual Database Compatibility**: Runs out-of-the-box on zero-config SQLite with in-memory cosine vector search, with native PostgreSQL 16 + `pgvector` support via Docker.
- **Empirical Evaluation Suite**: 100-question benchmark with reproducible accuracy, latency, and recovery statistics.

---

## 6. Architecture

### System Architecture Diagram

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

## 7. End-to-End Workflow

1. **User Question**: User asks: *"What was Apple's revenue growth between 2022 and 2023?"*
2. **Analysis Stage**: The Question Analyzer extracts:
   - Entity: `Apple Inc.` (`AAPL`)
   - Concept: `Revenue`
   - Time Period: `2022` to `2023` (Range)
   - Operation: `growth` (`percentage_change`)
3. **Retrieval Stage**: `SchemaRetriever` computes question vector similarity against `schema_catalog`. It selects `companies.ticker`, `companies.company_name`, `financial_facts.value`, `financial_facts.fiscal_year`, and the `Revenue` concept definition.
4. **SQL Generation Stage**: Gemini (or deterministic template fallback) synthesizes a CTE-based query joining fiscal year 2022 with fiscal year 2023, filtering for `f.reporting_type = 'consolidated'` and `f.is_restated = FALSE`.
5. **AST Validation Stage**: SQLGlot inspects the query tree, confirming that all referenced tables belong to the approved whitelist and that no mutation commands exist.
6. **Execution & Feedback**: The query executes against the database. If an error occurs (e.g. unknown column), `SQLRepairAgent` catches the diagnostic message, repairs the query, and re-executes.
7. **Result Verification Stage**: `ResultVerifier` confirms that rows were returned, no duplicate filings were blended, and values are plausible.
8. **Answer & Provenance**: `AnswerGenerator` computes the exact change (`-2.80%`, from `$394.33B` to `$383.29B`), renders an executive summary, recommends a comparative bar chart, and provides full filing provenance.

---

## 8. Agent Architecture

The agent subsystem is organized into modular Python classes under `backend/app/agents/`:

| Module | Class | Responsibility |
| :--- | :--- | :--- |
| `question_analyzer.py` | `QuestionAnalyzer` | Extracts entities, tickers, accounting concepts, periods, and analytical operations using Gemini with heuristic regex fallback. |
| `sql_generator.py` | `SQLGenerator` | Generates read-only SQL constrained by retrieved schema context and financial conventions. |
| `sql_repair.py` | `SQLRepairAgent` | Diagnoses runtime exceptions and AST validation failures, applying repair strategies (`CORRECTED_COLUMN_NAME`, `FIXED_SYNTAX_QUOTES`). |
| `answer_generator.py` | `AnswerGenerator` | Translates database rows into executive summaries, KPI highlight cards, and chart recommendations. |
| `orchestrator.py` | `FinSQLOrchestrator` | Master pipeline controller managing state transitions, execution timing, and trace telemetry. |
| `baseline.py` | `BaselineAgent` | Unconstrained single-shot baseline implementation for scientific comparison. |

---

## 9. Schema Retrieval

Sending a complete database schema to an LLM increases token costs, latency, and hallucination rates.

FinSQL Agent implements a **vector-based schema pruning module** (`backend/app/retrieval/schema_retriever.py`):
- All database tables, columns, sample values, and financial concepts are pre-embedded into 768-dimensional vectors using Google's `text-embedding-004` (with deterministic local vector fallback for offline testing).
- When a query arrives, it is embedded and compared against `schema_catalog` using cosine similarity.
- Items receive relevance boosts based on extracted entities and metrics.
- Only the top-K relevant schema items are formatted as markdown and injected into the generation prompt.

---

## 10. SQL Generation

SQL generation (`backend/app/agents/sql_generator.py`) enforces strict prompt engineering rules:
- **Zero Hallucination**: Use only the tables and columns present in the retrieved schema context.
- **Relational Integrity**: Join `companies` on `companies.company_id = financial_facts.company_id`.
- **Reporting Scope**: Enforce `financial_facts.reporting_type = 'consolidated'` unless standalone parent company reporting is explicitly requested.
- **Restatement Isolation**: Enforce `financial_facts.is_restated = FALSE` unless historical amendments are queried.
- **Period Alignment**: Filter for `financial_facts.fiscal_period = 'FY'` for full annual fiscal years.
- **Complex Analytical Queries**: Use Common Table Expressions (CTEs) for year-over-year growth and margin rankings.

---

## 11. SQL Validation & Security

FinSQL Agent never trusts raw LLM output to execute directly. Every query must pass AST inspection (`backend/app/validation/sql_validator.py`) using **SQLGlot**:

1. **Read-Only Enforcement**: Top-level AST node must be `exp.Select` or `exp.Union`.
2. **Mutation Rejection**: Disallows `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `TRUNCATE`, `CREATE`, `GRANT`, `REVOKE`.
3. **Table Whitelist Check**: Only approved tables (`companies`, `financial_facts`, `financial_concepts`, `schema_catalog`) and declared CTE aliases are permitted.
4. **Cartesian Join Detection**: Identifies unconstrained joins missing matching `ON` or `WHERE` clauses.
5. **Multi-Statement Blocking**: Prevents semicolon-separated command chaining.

---

## 12. SQL Error Recovery

A central innovation of the project is the **agentic self-healing feedback loop** (`backend/app/agents/sql_repair.py`):

```text
Attempt 1 (Faulty Query) ──► DB Exception: "no such column: f.fiscalYear"
                                     │
                                     ▼
Diagnostic Feedback ──────► Identify error: column naming typo
                                     │
                                     ▼
SQL Repair Agent ─────────► Apply strategy: CORRECTED_COLUMN_NAME
                                     │
                                     ▼
Attempt 2 (Repaired Query) ─► Re-validate AST ──► Clean DB Execution ──► Verified Result
```

Every attempt is recorded in the agent trace. If an attempt fails, the error message, previous SQL, and retrieved schema are passed back to the model to synthesize a repair (capped at `MAX_SQL_RETRIES = 3`).

---

## 13. Financial Domain Intelligence

Generic Text-to-SQL benchmarks (e.g. Spider) typically evaluate simple single-table lookups. FinSQL Agent incorporates financial domain rules:

- **Fiscal Year Discrepancies**: Apple's FY2023 ended September 30, 2023; Microsoft's FY2023 ended June 30, 2023. Queries filter explicitly by `f.fiscal_year` and `f.fiscal_period = 'FY'`.
- **Restatements**: Prior-year figures are frequently restated in comparative 10-K filings. The system filters `is_restated = FALSE` by default to prevent duplicate row counts.
- **Consolidated vs. Standalone**: Queries default to `reporting_type = 'consolidated'` to reflect full corporate entity results.
- **Unit Invariance**: Arithmetic operations assert unit compatibility (preventing meaningless operations like adding shares to USD).

---

## 14. Result Verification

Execution results pass through `ResultVerifier` (`backend/app/validation/result_verifier.py`) before answer synthesis:
- **Empty Result Detection**: Flags queries that returned 0 rows, allowing the agent to relax overly restrictive filters or notify the user.
- **Duplicate Detection**: Flags multiple rows for the same `(company, fiscal_year, concept)` tuple.
- **Plausibility Audits**: Asserts that metrics such as `Revenue` are not negative.

---

## 15. Answer Generation

The Answer Generator (`backend/app/agents/answer_generator.py`) produces user-facing explanations strictly grounded in the database results:
- **Executive Summaries**: One-to-two sentence clear answers (e.g. *"Apple Inc.'s reported Revenue for fiscal year 2023 was $383.29B."*).
- **Number Formatting**: Formats raw values into human-readable currency ($B, $M, $K) and percentages.
- **KPI Badges**: Generates structured metric cards for key figures.
- **Chart Selection**: Auto-selects between Bar Charts, Line Charts, or KPI Cards based on query shape.
- **Audit Provenance**: Attaches metadata detailing the source filing, reporting scope, and execution status.

---

## 16. Database Design

The relational database is designed around SEC Form 10-K reporting standards:

### `companies`
Master table containing public company identifiers and corporate taxonomy.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `company_id` | `INTEGER` | `PRIMARY KEY`, `AUTOINCREMENT` | Unique identifier |
| `ticker` | `VARCHAR(20)` | `UNIQUE`, `NOT NULL`, `INDEX` | Stock symbol (AAPL, MSFT, etc.) |
| `company_name` | `TEXT` | `NOT NULL`, `INDEX` | Full registered corporate name |
| `industry` | `TEXT` | `NULL` | Industry classification |
| `sector` | `TEXT` | `NULL` | Economic sector |
| `country` | `TEXT` | `DEFAULT 'USA'` | Country of incorporation |

### `financial_facts`
Fact table storing multi-year financial measurements.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `BIGINT` | `PRIMARY KEY`, `AUTOINCREMENT` | Record identifier |
| `company_id` | `INTEGER` | `FOREIGN KEY (companies.company_id)` | Company reference |
| `concept` | `TEXT` | `NOT NULL`, `INDEX` | Standard concept tag (Revenue, NetIncome) |
| `concept_description` | `TEXT` | `NULL` | Detailed line item description |
| `value` | `NUMERIC(20,4)` | `NULL` | Financial amount in USD or per-share |
| `unit` | `TEXT` | `NOT NULL`, `DEFAULT 'USD'` | Measurement unit |
| `period_start` | `DATE` | `NULL` | Accounting period start |
| `period_end` | `DATE` | `NULL` | Accounting period end |
| `filing_date` | `DATE` | `NULL` | Official SEC filing submission date |
| `fiscal_year` | `INTEGER` | `NOT NULL`, `INDEX` | Fiscal year (2020–2025) |
| `fiscal_period` | `TEXT` | `NOT NULL`, `DEFAULT 'FY'` | Period duration ('FY', 'Q1', etc.) |
| `form` | `TEXT` | `DEFAULT '10-K'` | SEC filing form |
| `statement_type` | `TEXT` | `NULL` | IncomeStatement, BalanceSheet, CashFlow |
| `reporting_type` | `TEXT` | `DEFAULT 'consolidated'` | 'consolidated' vs. 'standalone' |
| `is_restated` | `BOOLEAN` | `DEFAULT FALSE` | Flag for amended restatements |
| `source` | `TEXT` | `NULL` | Filing source documentation |

### `financial_concepts`
Accounting taxonomy mapping concepts, synonyms, and categories.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `INTEGER PRIMARY KEY` | Concept identifier |
| `concept` | `TEXT UNIQUE` | Concept name (e.g. `GrossProfit`) |
| `description` | `TEXT` | Business definition |
| `category` | `TEXT` | Financial statement category |
| `synonyms` | `JSON` | Natural language synonyms |
| `unit` | `TEXT` | Standard denomination |

### `schema_catalog`
Vector catalog for schema retrieval.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `INTEGER PRIMARY KEY` | Catalog entry ID |
| `item_type` | `VARCHAR(50)` | 'table', 'column', or 'concept' |
| `table_name` | `VARCHAR(100)` | Target database table |
| `column_name` | `VARCHAR(100)` | Target column name |
| `concept_name` | `VARCHAR(100)` | Target concept tag |
| `display_name` | `TEXT` | Human-readable identifier |
| `description` | `TEXT` | Semantic business definition |
| `synonyms` | `JSON` | Associated search keywords |
| `sample_values` | `TEXT` | Sample data values |
| `embedding_json` | `TEXT / VECTOR(768)` | 768-dimensional float embedding vector |

### Current Demonstration Dataset

The repository comes pre-seeded with a calibrated financial demonstration dataset (`scripts/seed_data.py`):
- **7 Public Corporations**: Apple Inc. (`AAPL`), Microsoft Corporation (`MSFT`), Alphabet Inc. (`GOOGL`), Amazon.com, Inc. (`AMZN`), Nvidia Corporation (`NVDA`), Tesla, Inc. (`TSLA`), and Meta Platforms, Inc. (`META`).
- **11 Standard Accounting Concepts**: `Revenue`, `NetIncome`, `GrossProfit`, `OperatingIncome`, `TotalAssets`, `TotalLiabilities`, `StockholdersEquity`, `OperatingCashFlow`, `Capex`, `CashAndCashEquivalents`, and `EarningsPerShareDiluted`.
- **380 Financial Facts**: Spanning fiscal years **2020 through 2025**, calibrated from actual SEC Form 10-K filings.
- **Accounting Edge Cases Included**: Explicitly models prior-year restatements (`is_restated = TRUE`), consolidated vs. standalone reporting entities (`reporting_type`), and varying fiscal year-ends (e.g. September for AAPL, June for MSFT, January for NVDA).

### Planned / Future Data Sources (Large-Scale Architecture)

To maintain rapid local execution and deterministic benchmark reproducibility, the current codebase queries this local demonstration SQLite / PostgreSQL database. The data schema was specifically modeled after official regulatory taxonomies to enable seamless future migration to large-scale external sources:
- **SEC EDGAR / XBRL Public Datasets**: Automated ingestion pipelines for Form 10-K and 10-Q XBRL filings across all US public companies.
- **SEC DERA Financial Statement Data Sets**: Bulk historical quarterly and annual balance sheet, income statement, and cash flow dumps.
- **Google BigQuery Financial Tables**: Direct serverless analytical querying across billions of public financial fact rows.
- **Macroeconomic & Global Datasets**: Planned integration with Federal Reserve Economic Data (FRED), World Bank World Development Indicators (WDI), and Reserve Bank of India (RBI DBIE) for multi-currency, macro-adjusted financial modeling.

> [!NOTE]
> The current working repository executes against the verified local Form 10-K demonstration dataset. Large-scale external APIs (SEC EDGAR, BigQuery) represent future architectural scaling paths as detailed in [Section 33](#33-large-scale--sec-architecture).

---

## 17. Technology Stack

| Layer | Technology | Version | Purpose in Project |
| :--- | :--- | :--- | :--- |
| **Backend Framework** | FastAPI | 0.115+ | Asynchronous REST API, CORS middleware, auto-generated OpenAPI docs |
| **Data Validation** | Pydantic | 2.13+ | Strongly-typed request/response validation and settings management |
| **ORM & Database** | SQLAlchemy | 2.0+ | Relational modeling, connection pooling, SQLite/PostgreSQL abstraction |
| **SQL AST Parser** | SQLGlot | 30.18+ | Structural AST parsing, read-only safety checks, table whitelisting |
| **Primary Database** | PostgreSQL 16 + pgvector | 16 / 0.5+ | Production relational database with vector distance indexing |
| **Fallback Database** | SQLite 3 | Built-in | Local zero-dependency database with in-memory cosine search |
| **LLM Provider** | Google Gemini | 2.5 Flash | Semantic query analysis, SQL synthesis, and diagnostic error repair |
| **Embeddings** | Google GenAI | text-embedding-004 | 768-dimensional schema and concept embeddings |
| **Frontend Framework** | React | 19.2+ | Modern reactive single-page user interface |
| **Language** | TypeScript | 6.0+ | End-to-end type safety for data contracts and UI state |
| **Bundler** | Vite | 8.3+ | Fast ES module frontend dev server and production builder |
| **CSS Framework** | Tailwind CSS | v4.3+ | Theme tokens, dark mode palette, and responsive layout utilities |
| **Charts** | Recharts | 3.10+ | Responsive SVG Bar and Line charts |
| **Icons** | Lucide React | 1.45+ | Clean UI iconography |

---

## 18. Project Structure

```text
Prompt_SQL/
├── backend/
│   ├── app/
│   │   ├── api/                # REST endpoints: query, health, schema, examples, metrics
│   │   ├── agents/             # Analyzer, SQL generator, repair agent, answer generator
│   │   ├── retrieval/          # Schema retriever and embedding services
│   │   ├── database/           # SQLAlchemy models, connection pool, safe executor
│   │   ├── validation/         # SQLGlot AST validator, financial result verifier
│   │   ├── prompts/            # Constrained prompt templates for Gemini
│   │   ├── config.py           # Application settings and environment configuration
│   │   └── main.py             # FastAPI entry point & static frontend mounting
│   ├── tests/                  # 23 Pytest unit and integration tests
│   └── requirements.txt        # Backend dependencies
├── frontend/
│   ├── src/
│   │   ├── components/         # Header, Input, Answer, Visualizer, SQL, Trace, Provenance
│   │   ├── services/           # API fetch client
│   │   ├── types/              # TypeScript data contracts
│   │   ├── App.tsx             # Main dashboard layout
│   │   └── index.css           # Tailwind v4 theme styling
│   ├── package.json
│   ├── tsconfig.app.json
│   └── vite.config.ts
├── scripts/
│   ├── init_db.py              # Database table initializer
│   ├── seed_data.py            # Financial fact seeder (7 companies, 380 facts)
│   └── build_schema_embeddings.py # Schema vector embedding generator
├── evaluation/
│   ├── questions.json          # 100 benchmark financial evaluation questions
│   ├── evaluator.py            # Automated evaluation runner
│   ├── metrics.py              # Metrics calculator & failure taxonomy
│   └── reports/                # Measured evaluation reports (JSON & Markdown)
├── docs/                       # Architectural & domain documentation
├── docker-compose.yml          # PostgreSQL 16 + pgvector container definition
├── render.yaml                 # 1-click cloud deployment blueprint
├── .env.example                # Environment variable template
├── LICENSE                     # MIT License
└── README.md                   # Project documentation
```

---

## 19. Installation

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- Git

```bash
# 1. Clone the repository
git clone https://github.com/gautham-binoy/Prompt_SQL.git
cd Prompt_SQL

# 2. Create Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install backend dependencies
pip install -r backend/requirements.txt

# 4. Install frontend dependencies
cd frontend && npm install && cd ..
```

---

## 20. Environment Variables

Create `.env` in the root directory:

```env
# Google Gemini Configuration
GEMINI_API_KEY=your_gemini_api_key_here
MODEL_NAME=gemini-2.5-flash
EMBEDDING_MODEL=text-embedding-004

# Database Configuration
# Local zero-dependency SQLite (default):
DATABASE_URL=sqlite:///./data/finsql.db
# Or PostgreSQL + pgvector:
# DATABASE_URL=postgresql://finsql:finsqlpass@localhost:5432/finsqldb

# Execution Safety Limits
MAX_SQL_RETRIES=3
QUERY_TIMEOUT_SECONDS=10
MAX_RESULT_ROWS=1000

# Set to false when a real GEMINI_API_KEY is configured
DEMO_MODE=false
```

---

## 21. Database Setup

Run the initialization scripts to create tables, load seed data, and generate schema embeddings:

```bash
# 1. Initialize database tables
python scripts/init_db.py

# 2. Seed 7 companies, 11 concepts, and 380 financial facts (2020-2025)
python scripts/seed_data.py

# 3. Build and store schema vector embeddings
python scripts/build_schema_embeddings.py
```

---

## 22. Running the Application

### Option A: Local Development (Separate Terminals)

**Terminal 1 (Backend):**
```bash
source .venv/bin/activate
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```
Open `http://127.0.0.1:5173` in your browser.

### Option B: Single-Command Full-Stack (Built Bundle)
```bash
cd frontend && npm run build && cd ..
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```
FastAPI automatically serves both the dashboard and API on `http://127.0.0.1:8000`.

---

## 23. Example Queries

The system handles diverse financial questions across multiple categories:

1. *"What was Apple's revenue in 2023?"* → `$383.29B` (Scalar lookup)
2. *"Compare Apple's revenue with Microsoft's revenue in 2023."* → `Apple $383.29B vs. Microsoft $211.92B` (Bar chart)
3. *"Show Apple's revenue from 2020 to 2025."* → `$274.51B (2020) to $412.00B (2025)` (Line chart)
4. *"Which company had the highest revenue in 2023?"* → `Amazon.com, Inc. ($574.78B)` (Ranking)
5. *"What was Microsoft's net income in 2023?"* → `$72.36B` (Scalar lookup)
6. *"Compare the net income of Apple and Microsoft from 2021 to 2023."* → 6 comparative rows
7. *"What was Apple's revenue growth between 2022 and 2023?"* → `-2.80% (from $394.33B to $383.29B)` (CTE calculation)
8. *"What was the average revenue of the companies in 2023?"* → `$248.00B across 7 companies` (Aggregation)
9. *"Which company had the highest net income margin in 2023?"* → `Microsoft Corporation (34.15%)` (Ratio ranking)
10. *"Give me Apple's revenue and net income for the last five fiscal years."* → 10 records tracking both metrics
11. *"Show Apple's consolidated revenue in 2023 excluding restatements."* → Filters `is_restated = FALSE`
12. *"Compare cash and cash equivalents between Google and Microsoft in 2023."* → Balance sheet comparison
13. *"Which company had the highest total assets in 2023?"* → Asset base comparison
14. *"What was Nvidia's revenue in 2024?"* → `$60.92B`
15. *"Show Tesla's net income from 2020 to 2025."* → Multi-year trajectory

---

## 24. Screenshots / Demo

The live web application can be tested directly at:  
👉 **[https://prompt-sql-1kuq.onrender.com/](https://prompt-sql-1kuq.onrender.com/)**

<!-- TODO: Add application screenshots to docs/images/ -->
> **Demo Screenshots Placeholder**:
> - `docs/images/dashboard_main.png` — Main dashboard layout with prompt chips.
> - `docs/images/query_comparison.png` — Multi-company revenue comparison with dynamic bar chart.
> - `docs/images/sql_trace.png` — Generated SQL code block with AST validation badge and execution trace timeline.
> - `docs/images/benchmark_modal.png` — Evaluation benchmark report modal comparing Baseline vs FinSQL Agent.

---

## 25. API Documentation

Interactive OpenAPI (Swagger) documentation is available at `http://127.0.0.1:8000/docs` (or on the live demo at `https://prompt-sql-1kuq.onrender.com/docs`).

- `POST /api/query`: Execute natural language financial query through the full agentic pipeline.
- `POST /api/query/baseline`: Execute via unconstrained Baseline Text-to-SQL for comparison.
- `GET /api/health`: Check system status, database facts count, and model configuration.
- `GET /api/schema`: Inspect relational tables, columns, companies, and financial concepts.
- `GET /api/examples`: Fetch 15+ curated example questions.
- `GET /api/metrics`: Retrieve the 100-question evaluation benchmark results.

---

## 26. Evaluation Methodology

To rigorously measure system reliability, an automated benchmarking framework was built under `evaluation/`:
- **Benchmark Suite** (`evaluation/questions.json`): 100 realistic financial questions categorized across 9 distinct types (`simple_lookup`, `comparison`, `aggregation`, `time_series`, `multi_company`, `calculation`, `financial_domain`, `ambiguous`, `error_recovery`).
- **Automated Runner** (`evaluation/evaluator.py`): Executes each question through both the Baseline and FinSQL Agent pipelines.
- **Metrics Calculator** (`evaluation/metrics.py`): Computes execution accuracy, result accuracy, financial correctness, retrieval precision, error recovery rate, and latency.

---

## 27. Baseline vs FinSQL Agent

- **Baseline Text-to-SQL**: Simulates a standard single-shot prompt (`Question -> LLM -> SQL -> Execution`). It lacks schema retrieval, AST validation, repair feedback, and financial verification. When prior-year restatements exist in the dataset, it consistently returns duplicate records.
- **FinSQL Agent**: Employs vector schema retrieval, SQLGlot AST guardrails, an agentic repair loop, and financial domain sanity checks.
- **Engineering Trade-off**: The agent introduces additional processing latency (~178ms vs ~0.2ms) in exchange for a dramatic jump in result accuracy (**99.0% vs 60.0%**). For financial decision-making, reliability outweighs sub-millisecond execution.

---

## 28. Evaluation Results

*Measured results from the 100-question benchmark run (`evaluation/reports/evaluation_report.json`):*

| Benchmark Metric | Baseline Text-to-SQL | FinSQL Agent (Ours) | Delta Improvement |
| :--- | :---: | :---: | :---: |
| **SQL Execution Accuracy** | 100.0% | **99.0%** | -1.0% |
| **Result Accuracy** | 60.0% | **99.0%** | **+39.0%** |
| **Financial Correctness** | 60.0% | **99.0%** | **+39.0%** |
| **Schema Retrieval Accuracy** | 0.0% (No Retrieval) | **100.0%** | **+100.0%** |
| **Error Recovery Rate** | 0.0% (No Recovery) | **87.5%** | **+87.5%** |
| **Average Latency** | 0.16 ms | 178.72 ms | (Includes AST & RAG) |
| **Average Retries** | 0 | 0.1 | Self-healing |

### Category Performance Breakdown (FinSQL Agent)
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

## 29. Failure Analysis

FinSQL Agent incorporates a 7-stage failure taxonomy to diagnose anomalies:
1. `SCHEMA_RETRIEVAL_FAILURE`: Failed to retrieve relevant tables or concepts.
2. `SQL_GENERATION_FAILURE`: Model output failed JSON schema parsing.
3. `SQL_VALIDATION_FAILURE`: Rejected by AST inspection (unapproved tables, mutations).
4. `SQL_EXECUTION_FAILURE`: Runtime database syntax or execution error.
5. `FINANCIAL_INTERPRETATION_FAILURE`: Unhandled restatements or missing consolidated filters resulting in duplicate rows.
6. `RESULT_VERIFICATION_FAILURE`: Incompatible unit operations or empty rows.
7. `ANSWER_GENERATION_FAILURE`: Failure to synthesize grounded explanation.

---

## 30. Security Considerations

- **AST Read-Only Guardrails**: Parses queries into Abstract Syntax Trees with SQLGlot, ensuring only `SELECT` and `WITH` statements execute.
- **Table Whitelisting**: Access is strictly limited to approved tables (`companies`, `financial_facts`, `financial_concepts`, `schema_catalog`).
- **Safe Execution Sandbox**: Queries execute with strict row limits (`MAX_RESULT_ROWS = 1000`) and statement timeouts (`QUERY_TIMEOUT_SECONDS = 10`).
- **Zero API Key Leakage**: Keys remain server-side in `.env` and are never exposed in browser bundles or client responses.

---

## 31. Limitations

- **Dataset Size**: The current prototype dataset is pre-seeded with 7 major technology corporations across fiscal years 2020–2025.
- **Reporting Period Focus**: Pre-seeded records emphasize annual Form 10-K filings (`fiscal_period = 'FY'`); quarterly 10-Q figures require expanded seed data.
- **Single-Turn Architecture**: The current implementation treats queries independently rather than maintaining multi-turn conversational session context.

---

## 32. Future Improvements

### Data
- Ingest live SEC Form 10-K and 10-Q filings directly via public SEC EDGAR APIs.
- Transition data storage to Google BigQuery for petabyte-scale historical financial statement analytics.

### Agent Architecture
- Implement multi-turn conversational memory for follow-up questions (*"What about the previous year?"*).
- Add semantic query caching to deliver sub-millisecond responses on repeated queries.

### Financial Intelligence
- Expand support for balance sheet ratios (Current Ratio, Debt-to-Equity) and cash flow metrics (Free Cash Flow).
- Support automatic currency conversions for international filings (EUR, GBP, JPY to USD).

### Evaluation
- Benchmark against Spider2-style financial datasets and adversarial prompt injection benchmarks.

### Product
- Support one-click PDF export of generated financial reports and charts.
- Add user workspaces and saved query collections.

---

## 33. Large-Scale / SEC Architecture

> **Note**: The current repository uses a local demonstration dataset. The diagram below outlines how the architecture is designed to scale to enterprise SEC EDGAR data on Google Cloud:

```text
┌────────────────────────────┐
│      React Dashboard       │
└─────────────┬──────────────┘
              │ HTTPS
              ▼
┌────────────────────────────┐
│ FastAPI on Google Cloud Run│
└──────┬──────────────┬──────┘
       │              │
       ▼              ▼
┌──────────────┐ ┌───────────────────────────────────────────────┐
│ Cloud SQL    │ │ Google BigQuery                               │
│ PostgreSQL   │ │ (SEC EDGAR / XBRL Public Dataset)             │
│ + pgvector   │ │ - Partitioned by fiscal_year & filing_date    │
│ (Metadata)   │ │ - Billions of historical fact records         │
└──────────────┘ └───────────────────────────────────────────────┘
```

---

## 34. Deployment

### Render.com (1-Click Free Deployment)
The repository includes a ready-to-deploy [`render.yaml`](render.yaml) blueprint:
1. Connect the repository to [Render.com](https://render.com/).
2. Select **Web Service**.
3. Set environment variables: `GEMINI_API_KEY`, `DEMO_MODE=false`.
4. Deploy: Render builds the React frontend, runs database migrations, and serves the application on a free HTTPS URL.

### Docker Compose
```bash
docker compose up -d
```

---

## 35. Testing

Run the automated test suite:

```bash
pytest backend/tests/ -v
```

All 23 test suites pass:
- `test_api.py`: Tests `/`, `/api/health`, `/api/schema`, `/api/examples`, `/api/metrics`, `/api/query`.
- `test_executor.py`: Tests query execution and error mapping.
- `test_question_analyzer.py`: Tests entity extraction, metrics, and periods.
- `test_result_verifier.py`: Tests empty sets, duplicate records, and restatement checks.
- `test_schema_retriever.py`: Tests vector schema retrieval.
- `test_sql_repair.py`: Tests self-healing column and table repair strategies.
- `test_sql_validator.py`: Tests AST read-only enforcement and mutation rejection.

---

## 36. Internship Relevance

This project demonstrates my ability to design and implement an end-to-end AI system rather than only integrating an LLM API. As a Computer Engineering student targeting **AI/ML, Agent Engineering, and Software Engineering Internships**, this repository highlights:
- **Agent Architecture**: Designing closed-loop systems with execution feedback, automated error recovery, and observability.
- **Database Reasoning**: Navigating relational schemas, Common Table Expressions (CTEs), and multi-year accounting joins.
- **RAG & Schema Retrieval**: Implementing vector embeddings (`text-embedding-004`) to prune schemas and eliminate prompt context bloat.
- **LLM Structured Generation**: Constraining Gemini outputs using strict system prompts, JSON schemas, and domain conventions.
- **Security & Defensive Engineering**: Using SQLGlot AST inspection to structurally enforce read-only execution guardrails.
- **Evaluation & Benchmarking**: Building an automated 100-question testing framework to measure empirical reliability rather than relying on anecdotal examples.
- **Debugging & Error Handling**: Diagnosing runtime SQL execution errors and engineering self-healing repair strategies.
- **Full-Stack Integration**: Developing an asynchronous FastAPI backend and connecting it to an interactive React 19 + TypeScript dashboard.

---

## 37. Key Learning Outcomes & Lessons Learned

1. **LLMs Need Structured Context Rather than Entire Database Schemas**: Dumping raw DDL into prompts wastes tokens and confuses the model. High-precision vector retrieval with relevance boosting significantly improves SQL accuracy.
2. **SQL Generation Requires Validation Before Execution**: Regex-based keyword checks are easily bypassed. Parsing queries into Abstract Syntax Trees (AST) with SQLGlot is essential to structurally block destructive mutations and verify table permissions.
3. **Execution Errors Can Be Useful Feedback for an Agent**: Rather than treating database syntax or schema errors as fatal exceptions, feeding error diagnostics back to the LLM enables autonomous, self-healing query repair.
4. **Correct Execution Does Not Guarantee Correct Financial Reasoning**: A query can execute with status 200 OK while producing a completely invalid answer (e.g. failing to filter prior-year restatements or mixing unconsolidated parents with consolidated groups). Domain-specific verification is mandatory.
5. **Evaluation Is Necessary to Measure Agent Reliability**: Anecdotal chat testing masks failure modes. An automated 100-question benchmark with failure taxonomy was critical to uncover blind spots and quantitatively prove agent effectiveness.
6. **Agentic Systems Trade Additional Latency for Reliability**: The agent introduces ~178ms of latency (vector search + AST validation + self-healing retry), but delivers a dramatic jump in accuracy (99.0% vs. 60.0%). For financial analytics, correctness outweighs sub-millisecond execution.

---

## 38. Contributors

### Author

**Gautham Binoy**  
Computer Engineering Student | AI/ML & Agent Engineering  
[GitHub](https://github.com/gautham-binoy) • [Live Demo](https://prompt-sql-1kuq.onrender.com/)

---

## 39. License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
