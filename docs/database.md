# Database Design & Schema Specification

FinSQL Agent models corporate financial accounting records based on SEC Form 10-K standards and XBRL taxonomies.

## 1. Tables Overview

### `companies`
Master table containing public company identifiers and corporate taxonomy.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `company_id` | `INTEGER` | `PRIMARY KEY`, `AUTOINCREMENT` | Unique company identifier |
| `ticker` | `VARCHAR(20)` | `UNIQUE`, `NOT NULL`, `INDEX` | Stock exchange symbol (AAPL, MSFT, NVDA, etc.) |
| `company_name` | `TEXT` | `NOT NULL`, `INDEX` | Registered legal corporate name |
| `industry` | `TEXT` | `NULL` | Industry classification (e.g. Consumer Electronics) |
| `sector` | `TEXT` | `NULL` | Macro sector (e.g. Technology) |
| `country` | `TEXT` | `DEFAULT 'USA'` | Country of incorporation |

### `financial_facts`
Core fact table containing time-series accounting measurements.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `BIGINT` | `PRIMARY KEY`, `AUTOINCREMENT` | Unique measurement identifier |
| `company_id` | `INTEGER` | `FOREIGN KEY (companies.company_id)` | Linked company reference |
| `concept` | `TEXT` | `NOT NULL`, `INDEX` | Financial concept tag (e.g. Revenue, NetIncome) |
| `concept_description` | `TEXT` | `NULL` | Detailed line item description |
| `value` | `NUMERIC(20,4)` | `NULL` | Numeric financial amount in USD or per-share |
| `unit` | `TEXT` | `NOT NULL`, `DEFAULT 'USD'` | Currency or unit denomination |
| `period_start` | `DATE` | `NULL` | Accounting period start date |
| `period_end` | `DATE` | `NULL` | Accounting period end date |
| `filing_date` | `DATE` | `NULL` | Official SEC filing submission date |
| `fiscal_year` | `INTEGER` | `NOT NULL`, `INDEX` | Accounting fiscal year (2020–2025) |
| `fiscal_period` | `TEXT` | `NOT NULL`, `DEFAULT 'FY'` | Reporting period duration ('FY', 'Q1', 'Q2', etc.) |
| `form` | `TEXT` | `DEFAULT '10-K'` | Regulatory filing form |
| `statement_type` | `TEXT` | `NULL` | IncomeStatement, BalanceSheet, CashFlow |
| `reporting_type` | `TEXT` | `DEFAULT 'consolidated'` | 'consolidated' vs 'standalone' |
| `is_restated` | `BOOLEAN` | `DEFAULT FALSE` | Flag for amended restatement filings |
| `source` | `TEXT` | `NULL` | Primary filing source |

### `financial_concepts`
Accounting taxonomy catalog defining metrics, synonyms, and categories.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY`, `AUTOINCREMENT` | Concept identifier |
| `concept` | `TEXT` | `UNIQUE`, `NOT NULL` | Standard concept name |
| `description` | `TEXT` | `NULL` | Accounting definition |
| `category` | `TEXT` | `NULL` | Statement category |
| `synonyms` | `JSON / TEXT` | `NOT NULL` | Natural language synonyms |
| `unit` | `TEXT` | `DEFAULT 'USD'` | Standard measurement unit |

### `schema_catalog`
Metadata catalog for pgvector semantic schema retrieval.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `INTEGER PRIMARY KEY` | Catalog entry ID |
| `item_type` | `VARCHAR(50)` | 'table', 'column', or 'concept' |
| `table_name` | `VARCHAR(100)` | Target database table |
| `column_name` | `VARCHAR(100)` | Target column name |
| `concept_name` | `VARCHAR(100)` | Target financial concept |
| `display_name` | `TEXT` | Human-readable identifier |
| `description` | `TEXT` | Semantic business definition |
| `synonyms` | `JSON` | Associated keywords |
| `sample_values` | `TEXT` | Example values |
| `embedding_json` | `TEXT / VECTOR(768)` | 768-dim float vector |

---

## 2. Seed Data Profile

The system includes realistic multi-year figures (FY2020–FY2025) calibrated from SEC Form 10-K filings:
- **7 Corporations**: Apple (AAPL), Microsoft (MSFT), Amazon (AMZN), Alphabet (GOOGL), Tesla (TSLA), Nvidia (NVDA), Meta (META).
- **11 Financial Concepts**: Revenue, CostOfRevenue, GrossProfit, OperatingExpenses, OperatingIncome, NetIncome, EarningsPerShare, CashAndCashEquivalents, TotalAssets, TotalLiabilities, Equity.
- **380 Financial Fact Records**: Including restatements and standalone reporting records to test edge cases.
