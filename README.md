# FinSQL Agent

> **Agentic Text-to-SQL for Financial Data**

[![Live Demo](https://img.shields.io/badge/Live_Demo-Render.com-00c7b7?style=for-the-badge&logo=render&logoColor=white)](https://prompt-sql-1kuq.onrender.com/)
[![Documentation](https://img.shields.io/badge/Architecture_Docs-docs%2F-blue?style=for-the-badge&logo=googledocs&logoColor=white)](docs/architecture.md)
[![API Docs](https://img.shields.io/badge/API_Docs-FastAPI_Swagger-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://prompt-sql-1kuq.onrender.com/docs)
[![License](https://img.shields.io/badge/License-MIT-amber?style=for-the-badge)](LICENSE)

[Live Demo](https://prompt-sql-1kuq.onrender.com/) • [Documentation](docs/architecture.md) • [API Docs](https://prompt-sql-1kuq.onrender.com/docs) • [License](LICENSE)

---

## 1. Overview

**FinSQL Agent** is a production-grade, agentic Text-to-SQL platform built to answer quantitative and analytical questions over complex corporate financial statement datasets using natural language.

Unlike naive "LLM-to-SQL" wrappers that prompt an LLM with raw schema strings and execute unchecked code, FinSQL Agent treats Text-to-SQL as an **agentic observability, validation, execution, and verification loop**:

$$\text{Natural Language} \longrightarrow \text{Analysis} \longrightarrow \text{Vector Schema RAG} \longrightarrow \text{SQL Generation} \longrightarrow \text{AST Guardrails} \longrightarrow \text{Execution} \longrightarrow \text{Self-Healing Feedback} \longrightarrow \text{Accounting Verification} \longrightarrow \text{Grounded Answer}$$

The system is tested against audited SEC Form 10-K financial records across 2020–2025 and evaluated against an empirical 100-question benchmark where it achieves **99.0% result accuracy** and an **87.5% self-healing error recovery rate**.

---

## 2. Problem Statement

Financial analysts, executives, auditors, and investors spend thousands of hours navigating relational databases and SEC filings to answer straightforward analytical questions:
- *"What was Apple's revenue growth between 2022 and 2023?"*
- *"Which technology company recorded the highest net income margin in 2023?"*
- *"Compare Microsoft and Alphabet operating income over the last five fiscal years."*

Non-technical stakeholders cannot write complex SQL involving Common Table Expressions (CTEs), multi-year period joins, and restatement exclusions. Meanwhile, generic LLMs hallucinate schema columns, invent non-existent financial tags, blend parent and subsidiary data, and fail when database errors occur.

---

## 3. Why Financial Text-to-SQL Is Difficult

Financial data presents unique engineering obstacles that break conventional Text-to-SQL systems:

1. **Schema & Tag Explosion**: Real financial datasets (such as SEC EDGAR / US-GAAP taxonomies) feature thousands of unique line item measurement concepts with duplicate and overlapping names (e.g. `Revenues`, `SalesRevenueNet`, `TotalRevenuesAndOtherIncome`).
2. **Fiscal Year vs. Calendar Year**: Corporate fiscal calendars do not align with December 31. Apple's fiscal year ends in late September, Microsoft's in late June, and Nvidia's in late January. Naive date arithmetic yields incorrect records.
3. **Restatements & Prior Period Adjustments**: Companies restate prior-year figures in comparative 10-K disclosures. Queries that fail to filter `is_restated` produce duplicate records and double-counted earnings.
4. **Consolidated vs. Standalone Reporting**: Corporations report consolidated group accounts alongside unconsolidated parent company figures (`reporting_type = 'consolidated'` vs. `'standalone'`). Mixing them corrupts calculations.
5. **Multi-Step Accounting Logic**: Questions asking for "margin rankings" or "revenue growth" require dynamic multi-table self-joins or CTE arithmetic across fiscal periods.
6. **Zero-Tolerance for Hallucination**: In finance, an invented dollar value or miscalculated margin can lead to catastrophic business decisions. Answers must be 100% grounded in verified database facts.

---

## 4. Solution

FinSQL Agent solves these challenges through modular agentic design:
- **Vector Schema Pruning**: Embeds schema metadata and concept definitions into 768-dimensional vector embeddings, selecting only the necessary tables, columns, and metric concepts for the question.
- **SQLGlot AST Safety Parser**: Validates SQL Abstract Syntax Trees to guarantee read-only analytical execution and reject mutation queries (`DROP`, `DELETE`, `UPDATE`, `INSERT`).
- **Agentic Self-Healing Loop**: Intercepts syntax, table, column, or filter errors, provides diagnostics back to the repair agent, and re-executes corrected queries up to `MAX_SQL_RETRIES = 3`.
- **Financial Result Verifier**: Performs accounting sanity checks (empty sets, restatement conflicts, duplicate rows, unit compatibility).
- **Strict Grounded Answer Synthesis**: Formats results ($383.29B, percentages) and attaches provenance badges strictly derived from executed database facts.

---

## 5. Key Features

- **99.0% Result Accuracy**: Outperforms naive Baseline Text-to-SQL (60.0%) by **+39.0%** on benchmark questions.
- **87.5% Self-Healing Error Recovery**: Automatically repairs faulty queries without user intervention.
- **pgvector Semantic Search**: Retrieves relevant schema context in under 15ms.
- **AST Security Guardrails**: Guarantees zero SQL injection, blocks multi-statement attacks, and enforces table whitelisting.
- **Dynamic Visualizations**: Auto-selects between Bar Charts (comparisons), Line Charts (trends), and KPI Cards.
- **Agent Observability Trace**: Complete visibility into pipeline stage latencies, extracted entities, and retrieved schema scores.
- **Dual Database Architecture**: Zero-config local SQLite engine + production PostgreSQL 16 with `pgvector` extension.
- **SEC EDGAR & BigQuery Extensibility**: Architecture ready for migration to petabyte-scale cloud data warehouses.

---

## 6. Architecture

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

1. **User Request**: User inputs a query such as: *"Compare Apple's revenue with Microsoft's revenue in 2023."*
2. **Analysis Stage**: The Question Analyzer maps `"Apple"` → `AAPL`, `"Microsoft"` → `MSFT`, `"revenue"` → `Revenue`, year `2023`, operation `comparison`.
3. **Retrieval Stage**: Vector search retrieves relevant column definitions for `companies.ticker`, `companies.company_name`, `financial_facts.value`, `financial_facts.fiscal_year`, and concept `Revenue`.
4. **Generation Stage**: Synthesizes a PostgreSQL-compatible query joining `companies` and `financial_facts`, filtering for `reporting_type = 'consolidated'`, `is_restated = FALSE`, and `fiscal_period = 'FY'`.
5. **AST Validation Stage**: SQLGlot inspects the Abstract Syntax Tree, verifying read-only access and table whitelisting.
6. **Execution & Feedback**: Executes safely with query timeout and row limits. If any database exception occurs, the error feedback loop repairs it.
7. **Verification Stage**: Asserts no duplicate rows exist, confirms unit consistency (`USD`), and validates entity matches.
8. **Answer & Visuals**: Generates the executive explanation, KPI highlights, a comparative bar chart, and full provenance metadata.

---

## 8. Agent Architecture

The agent subsystem is split into modular components located in `backend/app/agents/`:

| Agent Module | Responsibility |
| :--- | :--- |
| **`QuestionAnalyzer`** | Semantic entity extraction, ticker resolution, accounting concept normalization, and operation classification. |
| **`SQLGenerator`** | Constrained SQL synthesis incorporating retrieved schema context, domain constraints, and CTE templates. |
| **`SQLRepairAgent`** | Diagnostic engine analyzing database stack traces, column errors, and AST violations to synthesize repairs. |
| **`AnswerGenerator`** | Financial analyst synthesizer formatting currency, calculating variances, and recommending chart formats. |
| **`FinSQLOrchestrator`** | Master pipeline controller managing state transitions, attempt logging, and timing observability. |
| **`BaselineAgent`** | Unconstrained baseline implementation used for scientific benchmark comparison. |

---

## 9. Schema Retrieval

Rather than overwhelming the LLM's context window with the complete relational schema, `SchemaRetriever` utilizes vector embeddings:
- Schema tables, columns, accounting concepts, and synonyms are pre-embedded into 768-dimensional vectors.
- On query arrival, the question vector is compared against `schema_catalog` using cosine distance with entity-boosting.
- The prompt receives only the top-K relevant schema elements, guaranteeing zero prompt bloat and reducing hallucinations.

---

## 10. SQL Generation

The SQL Generator uses Google Gemini (`gemini-2.5-flash`) with structured JSON schema constraints:

```json
{
  "sql": "SELECT c.company_name, c.ticker, f.fiscal_year, f.concept, f.value, f.unit FROM companies c JOIN financial_facts f ON c.company_id = f.company_id WHERE c.ticker = 'AAPL' AND f.concept = 'Revenue' AND f.fiscal_year = 2023 AND f.fiscal_period = 'FY' AND f.reporting_type = 'consolidated' AND f.is_restated = FALSE;",
  "explanation": "Looked up Apple FY2023 consolidated revenue excluding restatements.",
  "assumptions": ["Consolidated reporting", "Full fiscal year (FY)", "Audited 10-K"],
  "confidence": 0.98
}
```

---

## 11. SQL Validation & Security

Before any SQL query reaches the database, it must pass inspection by `SQLValidator` powered by **SQLGlot**:
- **Read-Only Enforcement**: Root AST node must be `exp.Select` or `exp.Union`.
- **Destructive Query Rejection**: Strictly rejects `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `TRUNCATE`, `CREATE`, `GRANT`, `REVOKE`.
- **Table Whitelisting**: Tables must strictly belong to `{'companies', 'financial_facts', 'financial_concepts', 'schema_catalog'}` or declared CTE aliases.
- **Cartesian Join Detection**: Detects unconstrained joins missing `ON` or `WHERE` clauses.
- **Injection Prevention**: Blocks multi-statement semicolon chaining.

---

## 12. SQL Error Recovery

FinSQL Agent incorporates an active self-healing feedback loop:

```text
Attempt 1 (Faulty SQL) ──► DB Exception: "no such column: f.fiscalYear"
                                    │
                                    ▼
Diagnostic Analysis ──────► Diagnosis: Misspelled fiscal_year column
                                    │
                                    ▼
Repair Synthesis ─────────► Apply CORRECTED_COLUMN_NAME strategy
                                    │
                                    ▼
Attempt 2 (Repaired SQL) ─► Clean Execution ──► Verified Results ($383.29B)
```

The system logs every attempt in the observability trace and caps retries at `MAX_SQL_RETRIES = 3`.

---

## 13. Financial Domain Intelligence

FinSQL Agent natively incorporates corporate accounting rules:

- **Fiscal vs Calendar Periods**: Filters by `f.fiscal_year` and `f.fiscal_period = 'FY'`.
- **Restatement Deduplication**: Enforces `f.is_restated = FALSE` to prevent prior-year restatements from colliding with current filings.
- **Consolidated vs Standalone**: Defaults to `f.reporting_type = 'consolidated'`.
- **Unit Separation**: Ensures currency amounts (`USD`) are not summed with per-share values (`per-share`).

---

## 14. Result Verification

Executed results pass through `ResultVerifier` before user presentation:
- **Empty Set Detection**: Identifies 0-row queries to trigger filter relaxation or alert the user.
- **Duplicate Detection**: Flags multiple rows for the same `(company, fiscal_year, concept)` tuple.
- **Value Plausibility**: Verifies that metrics like `Revenue` are not negative.

---

## 15. Answer Generation

The Answer Generator converts database rows into executive summaries:
- **Number Formatting**: Converts raw numbers like `383285000000` into `$383.29B`.
- **Growth & Variance**: Calculates relative percentage changes (e.g. `-2.80%`).
- **Visualization Selection**: Recommends chart types:
  - Time-series queries → **Line Chart**
  - Company comparisons & rankings → **Bar Chart**
  - Single metrics → **KPI Metric Card**

---

## 16. Database Design

The database schema models SEC Form 10-K financial records:

### `companies`
```sql
CREATE TABLE companies (
    company_id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) UNIQUE NOT NULL,
    company_name TEXT NOT NULL,
    industry TEXT,
    sector TEXT,
    country TEXT DEFAULT 'USA'
);
```

### `financial_facts`
```sql
CREATE TABLE financial_facts (
    id BIGSERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(company_id),
    concept TEXT NOT NULL,
    concept_description TEXT,
    value NUMERIC(20,4),
    unit TEXT DEFAULT 'USD',
    period_start DATE,
    period_end DATE,
    filing_date DATE,
    fiscal_year INTEGER NOT NULL,
    fiscal_period TEXT DEFAULT 'FY',
    form TEXT DEFAULT '10-K',
    statement_type TEXT,
    reporting_type TEXT DEFAULT 'consolidated',
    is_restated BOOLEAN DEFAULT FALSE,
    source TEXT
);
```

### `financial_concepts`
```sql
CREATE TABLE financial_concepts (
    id SERIAL PRIMARY KEY,
    concept TEXT UNIQUE NOT NULL,
    description TEXT,
    category TEXT,
    synonyms JSON NOT NULL,
    unit TEXT DEFAULT 'USD'
);
```

### `schema_catalog`
```sql
CREATE TABLE schema_catalog (
    id SERIAL PRIMARY KEY,
    item_type VARCHAR(50) NOT NULL,
    table_name VARCHAR(100),
    column_name VARCHAR(100),
    concept_name VARCHAR(100),
    display_name TEXT NOT NULL,
    description TEXT NOT NULL,
    synonyms JSON NOT NULL,
    sample_values TEXT,
    embedding_json TEXT
);
```

---

## 17. Technology Stack

| Component | Technology | Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Backend API** | FastAPI | 0.115+ | High-performance asynchronous REST API |
| **Data Validation** | Pydantic | 2.13+ | Strongly-typed schemas and configuration |
| **ORM** | SQLAlchemy | 2.0+ | Relational mappings and session lifecycle |
| **SQL Parser** | SQLGlot | 30.18+ | AST validation, safety checks, and transpilation |
| **Vector DB** | pgvector / SQLite | 16 / 3 | Semantic vector distance retrieval |
| **LLM Provider** | Google Gemini | 2.5 Flash | Semantic reasoning, SQL generation & repair |
| **Embeddings** | Google GenAI | text-embedding-004 | 768-dim schema embeddings |
| **Frontend** | React + TypeScript | 19.2+ / 6.0+ | Modern analytical user dashboard |
| **Build Tool** | Vite | 8.3+ | Fast ES module bundler |
| **Styling** | Tailwind CSS | v4.3+ | Curated dark-mode financial styling |
| **Charts** | Recharts | 3.10+ | Responsive interactive visualizations |
| **Icons** | Lucide React | 1.45+ | Crisp modern icons |

---

## 18. Project Structure

```text
Prompt_SQL/
├── backend/
│   ├── app/
│   │   ├── api/                # REST route endpoints (query, health, schema, metrics)
│   │   ├── agents/             # Analyzer, SQL generator, repair agent, answer generator
│   │   ├── retrieval/          # Schema retriever and embedding services
│   │   ├── database/           # SQLAlchemy models, connection pool, safe executor
│   │   ├── validation/         # SQLGlot AST validator, financial result verifier
│   │   ├── prompts/            # Constrained prompt engineering templates
│   │   ├── config.py           # Application settings and environment variables
│   │   └── main.py             # FastAPI entry point & static frontend mounting
│   ├── tests/                  # 23 Pytest unit and integration tests
│   └── requirements.txt        # Backend dependencies
├── frontend/
│   ├── src/
│   │   ├── components/         # Header, Input, Answer, Visualizer, SQL, Trace, Provenance
│   │   ├── services/           # API fetch client
│   │   ├── types/              # TypeScript data contracts
│   │   ├── App.tsx             # Main dashboard layout
│   │   └── index.css           # Tailwind v4 theme tokens
│   ├── package.json
│   └── vite.config.ts
├── scripts/
│   ├── init_db.py              # Schema table initializer
│   ├── seed_data.py            # Financial fact seeder (7 companies, 380 facts)
│   └── build_schema_embeddings.py # Vector embedding generator
├── evaluation/
│   ├── questions.json          # 100 benchmark financial evaluation questions
│   ├── evaluator.py            # Automated evaluation runner
│   ├── metrics.py              # Metric calculator & failure taxonomy
│   └── reports/                # Measured evaluation reports (JSON & Markdown)
├── docs/                       # Architectural & domain specifications
├── docker-compose.yml          # PostgreSQL 16 + pgvector container definition
├── render.yaml                 # 1-click cloud deployment blueprint
├── .env.example                # Environment variable template
├── LICENSE                     # MIT License
└── README.md                   # Project documentation
```

---

## 19. Installation

```bash
# 1. Clone repository
git clone https://github.com/gautham-binoy/Prompt_SQL.git
cd Prompt_SQL

# 2. Set up Python virtual environment
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

# Database Configuration (SQLite local fallback or PostgreSQL pgvector)
DATABASE_URL=sqlite:///./data/finsql.db
# DATABASE_URL=postgresql://finsql:finsqlpass@localhost:5432/finsqldb

# Execution Safety Limits
MAX_SQL_RETRIES=3
QUERY_TIMEOUT_SECONDS=10
MAX_RESULT_ROWS=1000

# Set to false when GEMINI_API_KEY is supplied
DEMO_MODE=false
```

---

## 21. Database Setup

```bash
# Initialize schema tables
python scripts/init_db.py

# Seed 7 companies, 11 concepts, and 380 financial facts (2020-2025)
python scripts/seed_data.py

# Build and store schema vector embeddings
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

## 24. Screenshots / Demo

The live web application can be explored directly at:  
👉 **[https://prompt-sql-1kuq.onrender.com/](https://prompt-sql-1kuq.onrender.com/)**

### Interactive UI Features:
- **Header**: Live system health, database record counter, mode selector (FinSQL Agent vs Baseline).
- **Search Bar**: Keyboard-ready input with 9 curated quick-prompt chips.
- **Executive Card**: Clean financial summaries with KPI highlight boxes.
- **Visualizer**: Responsive Recharts bar charts, multi-year trend lines, and KPI cards.
- **SQL Section**: Syntax-highlighted code block with AST read-only validation badge and copy button.
- **Data Table**: Paginated financial data grid with formatted currency and units.
- **Agent Trace**: Interactive execution timeline displaying stage-by-stage latencies and retrieval scores.
- **Provenance**: Audit trail detailing data sources and consolidation scope.

---

## 25. API Documentation

Interactive Swagger documentation is available at `http://127.0.0.1:8000/docs` (or `https://prompt-sql-1kuq.onrender.com/docs`).

- `POST /api/query`: Submits natural language question through FinSQL Agent.
- `POST /api/query/baseline`: Submits question through Baseline Text-to-SQL.
- `GET /api/health`: System health, database connection, and record counts.
- `GET /api/schema`: Relational schema catalog, supported companies, and concepts.
- `GET /api/examples`: Curated financial questions categorized by analysis type.
- `GET /api/metrics`: Evaluation benchmark report comparing Baseline vs FinSQL Agent.

---

## 26. Evaluation Methodology

The evaluation framework benchmarked **100 realistic financial questions** across 9 categories:
- `simple_lookup` (15 questions)
- `comparison` (15 questions)
- `aggregation` (10 questions)
- `time_series` (12 questions)
- `multi_company` (10 questions)
- `calculation` (10 questions)
- `financial_domain` (12 questions)
- `ambiguous` (8 questions)
- `error_recovery` (8 questions)

Every question is executed through both the **Baseline Text-to-SQL** and **FinSQL Agent** pipelines to compare:
1. SQL execution success.
2. Result accuracy (non-empty, correct entities/metrics).
3. Financial correctness (absence of duplicate filings, proper consolidated scope, non-restated flags).
4. Error recovery rate (repairing initial execution exceptions).
5. End-to-end latency.

---

## 27. Baseline vs FinSQL Agent

- **Baseline Text-to-SQL**: Direct single-shot prompt `User Question -> Gemini -> SQL -> Database`. It lacks schema retrieval, AST validation, repair feedback, and financial verification. It consistently returns duplicate rows when prior-year restatements exist in the dataset.
- **FinSQL Agent**: Multi-stage agentic system featuring vector schema retrieval, SQLGlot AST inspection, self-healing retries, and financial domain verification.

---

## 28. Evaluation Results

*Actual measured figures from the 100-question automated benchmark run:*

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
- `simple_lookup`: **100.0%**
- `comparison`: **100.0%**
- `aggregation`: **100.0%**
- `time_series`: **100.0%**
- `multi_company`: **100.0%**
- `calculation`: **100.0%**
- `financial_domain`: **100.0%**
- `ambiguous`: **100.0%**
- `error_recovery`: **87.5%**

---

## 29. Failure Analysis

FinSQL Agent incorporates a failure taxonomy to diagnose anomalies:
- `SCHEMA_RETRIEVAL_FAILURE`: Zero schema elements retrieved.
- `SQL_GENERATION_FAILURE`: Model output fails JSON schema formatting.
- `SQL_VALIDATION_FAILURE`: Query rejected by AST inspection (unapproved tables, mutations).
- `SQL_EXECUTION_FAILURE`: Runtime database exception.
- `FINANCIAL_INTERPRETATION_FAILURE`: Missing restatement or consolidation filters resulting in duplicate rows.
- `RESULT_VERIFICATION_FAILURE`: Incompatible unit operations or empty rows.
- `ANSWER_GENERATION_FAILURE`: Explanation generation failure.

---

## 30. Security Considerations

- **Strict Read-Only Enforcement**: Rejects any state-changing statements via AST inspection.
- **Table Whitelisting**: Disallows querying arbitrary tables (e.g. `users`, `sqlite_master`).
- **No Free-Form Prompt Execution**: LLM output is parsed into structured JSON and validated before execution.
- **Execution Limits**: Hard timeouts (`QUERY_TIMEOUT_SECONDS = 10`) and row limits (`MAX_RESULT_ROWS = 1000`).
- **Zero API Key Leakage**: Keys remain server-side in `.env` and are never exposed in browser bundles or logs.

---

## 31. Limitations

- **Dataset Scope**: Calibrated for 7 prominent corporations (Apple, Microsoft, Amazon, Alphabet, Tesla, Nvidia, Meta) across 2020–2025.
- **Annual Focus**: Pre-seeded facts emphasize annual 10-K filings (`fiscal_period = 'FY'`); quarterly 10-Q figures are supported in the database schema but require expanded seed data.
- **Single-Turn Architecture**: The current implementation treats queries independently rather than maintaining conversational chat sessions.

---

## 32. Future Improvements

1. **Live SEC EDGAR Ingestion**: Automatically ingest and parse newly published 10-K and 10-Q filings from the SEC EDGAR public API.
2. **Multi-Turn Conversational Memory**: Enable conversational follow-up questions (*"What was it the year before?"*).
3. **Semantic Query Caching**: Cache verified SQL queries using semantic vector similarity to achieve sub-millisecond responses.
4. **Natural Language Chart Customization**: Allow users to toggle chart styles or export PDF financial decks directly.

---

## 33. Large-Scale / SEC Architecture

In enterprise production, FinSQL Agent scales to petabyte-scale financial warehouses:

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

BigQuery handles petabyte-scale analytical queries over decades of SEC filings with columnar storage and distributed execution.

---

## 34. Deployment

### Render.com (1-Click Deployment)
The repository includes a ready-to-deploy [`render.yaml`](render.yaml) specification:
1. Connect your repository to [Render.com](https://render.com/).
2. Select **Web Service**.
3. Set environment variables: `GEMINI_API_KEY`, `DEMO_MODE=false`.
4. Deploy: Render builds the React frontend, runs database migrations, and serves the full-stack app.

### Docker Compose
```bash
docker compose up -d
```

---

## 35. Testing

Run the full automated test suite:

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

This project demonstrates skills essential for senior AI/agentic engineering internships:
- **Production LLM Engineering**: Moving beyond naive prompting to structured JSON contracts, guardrails, and error handling.
- **Autonomous Agent Workflows**: Execution feedback loops, automated self-healing, and state machines.
- **RAG & Vector Retrieval**: Embedding-based schema pruning to minimize latency and hallucinations.
- **Database Engineering**: Complex CTEs, self-joins, window functions, and AST query parsing.
- **Full-Stack Competency**: FastAPI backend, React 19 / TypeScript, and Tailwind CSS v4.
- **Scientific Evaluation**: Rigorous 100-question benchmarking with empirical deltas over baseline.

---

## 37. Lessons Learned

1. **Schema Dumps Hurt LLMs**: Sending full schemas degrades LLM reasoning. Precision vector retrieval dramatically improves SQL accuracy.
2. **AST Parsers Are Crucial**: Regular expressions cannot securely validate SQL. AST inspection with SQLGlot is required for safe production Text-to-SQL.
3. **Self-Healing Beats Single-Shot**: Even advanced models make syntax or column typos. An automated repair loop bridges the gap from 85% to 99% accuracy.
4. **Accounting Rules Matter**: Without domain logic (fiscal years, restatements, consolidated scope), SQL queries return misleading financial results.

---

## 38. Contributors

- **Gautham Binoy** — *Full-Stack AI & Database Engineer* — [GitHub](https://github.com/gautham-binoy)

---

## 39. License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
