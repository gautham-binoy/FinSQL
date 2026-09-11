import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.database.connection import SessionLocal, init_database
from backend.app.database.models import SchemaCatalog, FinancialConcept
from backend.app.retrieval.embeddings import get_embedding


SCHEMA_METADATA_ITEMS = [
    # Table Level
    {
        "item_type": "table",
        "table_name": "companies",
        "column_name": None,
        "concept_name": None,
        "display_name": "companies",
        "description": "Master table containing corporate entities, ticker symbols (AAPL, MSFT, NVDA, AMZN, GOOGL, TSLA, META), company names, sector, and industry.",
        "synonyms": ["firm", "corporation", "issuer", "enterprise", "ticker", "business"],
        "sample_values": "Apple Inc. (AAPL), Microsoft Corporation (MSFT), Nvidia Corporation (NVDA)",
    },
    {
        "item_type": "table",
        "table_name": "financial_facts",
        "column_name": None,
        "concept_name": None,
        "display_name": "financial_facts",
        "description": "Core time-series fact table containing numeric financial metrics, fiscal years (2020-2025), periods (FY), concepts (Revenue, NetIncome), values, units, and restatement flags.",
        "synonyms": ["financial statements", "income statement", "balance sheet", "sec filings", "facts", "numbers", "metrics"],
        "sample_values": "value=383285000000, fiscal_year=2023, concept=Revenue",
    },
    {
        "item_type": "table",
        "table_name": "financial_concepts",
        "column_name": None,
        "concept_name": None,
        "display_name": "financial_concepts",
        "description": "Financial catalog defining standard accounting measurement concepts, synonyms, categories, and units.",
        "synonyms": ["accounting catalog", "metric definitions", "taxonomy", "dictionary"],
        "sample_values": "Revenue, NetIncome, GrossProfit, TotalAssets",
    },

    # Columns: companies
    {
        "item_type": "column",
        "table_name": "companies",
        "column_name": "company_id",
        "concept_name": None,
        "display_name": "companies.company_id",
        "description": "Primary key integer identifier for a company. Joins with financial_facts.company_id.",
        "synonyms": ["company id", "id", "firm id"],
        "sample_values": "1, 2, 3",
    },
    {
        "item_type": "column",
        "table_name": "companies",
        "column_name": "ticker",
        "concept_name": None,
        "display_name": "companies.ticker",
        "description": "Public stock exchange trading symbol such as AAPL, MSFT, AMZN, GOOGL, TSLA, NVDA, META.",
        "synonyms": ["symbol", "stock symbol", "trading code", "ticker symbol"],
        "sample_values": "'AAPL', 'MSFT', 'NVDA'",
    },
    {
        "item_type": "column",
        "table_name": "companies",
        "column_name": "company_name",
        "concept_name": None,
        "display_name": "companies.company_name",
        "description": "Full legal registered corporate name of the company, e.g. 'Apple Inc.', 'Microsoft Corporation', 'Nvidia Corporation'.",
        "synonyms": ["name", "firm name", "corporation name", "organization"],
        "sample_values": "'Apple Inc.', 'Microsoft Corporation'",
    },
    {
        "item_type": "column",
        "table_name": "companies",
        "column_name": "sector",
        "concept_name": None,
        "display_name": "companies.sector",
        "description": "Macroeconomic sector classification such as Technology, Communication Services, Consumer Cyclical.",
        "synonyms": ["economic sector", "broad industry", "industry sector"],
        "sample_values": "'Technology', 'Consumer Cyclical'",
    },
    {
        "item_type": "column",
        "table_name": "companies",
        "column_name": "industry",
        "concept_name": None,
        "display_name": "companies.industry",
        "description": "Specific industry segment classification like Consumer Electronics, Semiconductors, Systems Software.",
        "synonyms": ["business line", "niche", "specialization"],
        "sample_values": "'Consumer Electronics', 'Semiconductors'",
    },

    # Columns: financial_facts
    {
        "item_type": "column",
        "table_name": "financial_facts",
        "column_name": "company_id",
        "concept_name": None,
        "display_name": "financial_facts.company_id",
        "description": "Foreign key reference joining with companies.company_id to filter or join company attributes.",
        "synonyms": ["company reference", "fk company", "company"],
        "sample_values": "1, 2",
    },
    {
        "item_type": "column",
        "table_name": "financial_facts",
        "column_name": "concept",
        "concept_name": None,
        "display_name": "financial_facts.concept",
        "description": "Standard financial measurement tag name: 'Revenue', 'NetIncome', 'GrossProfit', 'OperatingIncome', 'TotalAssets', 'TotalLiabilities', 'CashAndCashEquivalents', 'EarningsPerShare', 'OperatingExpenses', 'CostOfRevenue'.",
        "synonyms": ["metric", "financial metric", "tag", "concept name", "accounting line item", "kpi"],
        "sample_values": "'Revenue', 'NetIncome', 'OperatingIncome'",
    },
    {
        "item_type": "column",
        "table_name": "financial_facts",
        "column_name": "value",
        "concept_name": None,
        "display_name": "financial_facts.value",
        "description": "Exact numeric financial amount reported in USD or per-share (e.g. 383285000000 for Apple's $383.28B revenue).",
        "synonyms": ["amount", "figure", "total", "dollars", "sum", "financial number"],
        "sample_values": "383285000000, 211915000000, 6.13",
    },
    {
        "item_type": "column",
        "table_name": "financial_facts",
        "column_name": "fiscal_year",
        "concept_name": None,
        "display_name": "financial_facts.fiscal_year",
        "description": "The 4-digit fiscal year of the financial record (e.g., 2020, 2021, 2022, 2023, 2024, 2025).",
        "synonyms": ["year", "fy", "reporting year", "annual period"],
        "sample_values": "2020, 2022, 2023, 2024, 2025",
    },
    {
        "item_type": "column",
        "table_name": "financial_facts",
        "column_name": "fiscal_period",
        "concept_name": None,
        "display_name": "financial_facts.fiscal_period",
        "description": "Period duration code: 'FY' for full annual fiscal year, or 'Q1', 'Q2', 'Q3', 'Q4' for quarters. Default to 'FY'.",
        "synonyms": ["quarter", "annual", "period", "reporting duration"],
        "sample_values": "'FY', 'Q1'",
    },
    {
        "item_type": "column",
        "table_name": "financial_facts",
        "column_name": "period_start",
        "concept_name": None,
        "display_name": "financial_facts.period_start",
        "description": "Calendar starting date of the accounting reporting period.",
        "synonyms": ["start date", "from date", "beginning date"],
        "sample_values": "'2022-09-25'",
    },
    {
        "item_type": "column",
        "table_name": "financial_facts",
        "column_name": "period_end",
        "concept_name": None,
        "display_name": "financial_facts.period_end",
        "description": "Calendar ending date of the accounting reporting period (e.g., Apple's fiscal year ends late September).",
        "synonyms": ["end date", "to date", "as of date", "balance date"],
        "sample_values": "'2023-09-30'",
    },
    {
        "item_type": "column",
        "table_name": "financial_facts",
        "column_name": "reporting_type",
        "concept_name": None,
        "display_name": "financial_facts.reporting_type",
        "description": "Consolidation scope: 'consolidated' (full corporate group including subsidiaries) vs 'standalone' (parent company only). Always filter or prefer 'consolidated'.",
        "synonyms": ["consolidation", "consolidated", "standalone", "parent entity"],
        "sample_values": "'consolidated', 'standalone'",
    },
    {
        "item_type": "column",
        "table_name": "financial_facts",
        "column_name": "is_restated",
        "concept_name": None,
        "display_name": "financial_facts.is_restated",
        "description": "Boolean flag indicating whether the financial fact was restated in subsequent SEC filings. Typically filter for is_restated = FALSE unless asking for restatements.",
        "synonyms": ["restatement", "restated", "amendment", "adjustment"],
        "sample_values": "FALSE, TRUE",
    },
    {
        "item_type": "column",
        "table_name": "financial_facts",
        "column_name": "unit",
        "concept_name": None,
        "display_name": "financial_facts.unit",
        "description": "Currency or measurement unit: 'USD' for financial amounts, 'per-share' for EPS.",
        "synonyms": ["currency", "denomination", "measure"],
        "sample_values": "'USD', 'per-share'",
    },
]


def build_schema_embeddings():
    init_database()
    db = SessionLocal()

    try:
        print("Clearing existing schema catalog...")
        db.query(SchemaCatalog).delete()
        db.commit()

        print("Building schema metadata items & embeddings...")
        catalog_items = []

        # 1. Base table & column items
        for item in SCHEMA_METADATA_ITEMS:
            content_to_embed = f"{item['display_name']} - {item['description']} Synonyms: {', '.join(item['synonyms'])}. Sample: {item['sample_values']}"
            emb = get_embedding(content_to_embed)
            
            entry = SchemaCatalog(
                item_type=item["item_type"],
                table_name=item["table_name"],
                column_name=item["column_name"],
                concept_name=item["concept_name"],
                display_name=item["display_name"],
                description=item["description"],
                synonyms=item["synonyms"],
                sample_values=item["sample_values"],
                embedding_json=json.dumps(emb)
            )
            catalog_items.append(entry)

        # 2. Financial Concepts from database
        concepts = db.query(FinancialConcept).all()
        for conc in concepts:
            content_to_embed = f"Financial concept: {conc.concept} ({conc.category}). Description: {conc.description}. Synonyms: {', '.join(conc.synonyms)}. Unit: {conc.unit}"
            emb = get_embedding(content_to_embed)
            
            entry = SchemaCatalog(
                item_type="concept",
                table_name="financial_facts",
                column_name="concept",
                concept_name=conc.concept,
                display_name=f"Concept: {conc.concept}",
                description=conc.description or f"Financial metric {conc.concept}",
                synonyms=conc.synonyms,
                sample_values=f"concept='{conc.concept}', unit='{conc.unit}'",
                embedding_json=json.dumps(emb)
            )
            catalog_items.append(entry)

        db.add_all(catalog_items)
        db.commit()
        print(f"Successfully generated and stored {len(catalog_items)} schema metadata embeddings.")

    except Exception as e:
        db.rollback()
        print(f"Error building schema embeddings: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    build_schema_embeddings()
