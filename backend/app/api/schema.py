from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database.connection import get_db
from backend.app.database.models import Company, FinancialConcept, SchemaCatalog

router = APIRouter(prefix="/api/schema", tags=["Schema"])


@router.get("")
def get_schema(db: Session = Depends(get_db)):
    """
    Returns database schema information, supported companies, and financial concepts.
    """
    companies = db.query(Company).order_by(Company.ticker).all()
    concepts = db.query(FinancialConcept).order_by(FinancialConcept.category, FinancialConcept.concept).all()
    catalog_items = db.query(SchemaCatalog).all()

    tables_info = [
        {
            "name": "companies",
            "description": "Master table containing corporate entities and stock ticker symbols.",
            "columns": [
                {"name": "company_id", "type": "INTEGER", "is_primary_key": True, "description": "Primary key"},
                {"name": "ticker", "type": "VARCHAR(20)", "is_primary_key": False, "description": "Stock trading ticker symbol (e.g. AAPL, MSFT)"},
                {"name": "company_name", "type": "TEXT", "is_primary_key": False, "description": "Legal company name"},
                {"name": "sector", "type": "TEXT", "is_primary_key": False, "description": "Economic sector"},
                {"name": "industry", "type": "TEXT", "is_primary_key": False, "description": "Industry line"},
                {"name": "country", "type": "TEXT", "is_primary_key": False, "description": "Country of incorporation"}
            ]
        },
        {
            "name": "financial_facts",
            "description": "Core fact table storing historical accounting measurements and 10-K reported figures.",
            "columns": [
                {"name": "id", "type": "BIGINT", "is_primary_key": True, "description": "Fact record ID"},
                {"name": "company_id", "type": "INTEGER", "is_primary_key": False, "description": "FK referencing companies.company_id"},
                {"name": "concept", "type": "TEXT", "is_primary_key": False, "description": "Standard XBRL concept tag (e.g. Revenue, NetIncome)"},
                {"name": "concept_description", "type": "TEXT", "is_primary_key": False, "description": "Filing line item description"},
                {"name": "value", "type": "NUMERIC", "is_primary_key": False, "description": "Numeric financial value in USD or shares"},
                {"name": "unit", "type": "TEXT", "is_primary_key": False, "description": "Currency unit (USD, per-share)"},
                {"name": "fiscal_year", "type": "INTEGER", "is_primary_key": False, "description": "Reporting fiscal year (2020-2025)"},
                {"name": "fiscal_period", "type": "TEXT", "is_primary_key": False, "description": "Reporting period ('FY' for annual)"},
                {"name": "period_start", "type": "DATE", "is_primary_key": False, "description": "Calendar start date of reporting period"},
                {"name": "period_end", "type": "DATE", "is_primary_key": False, "description": "Calendar end date of reporting period"},
                {"name": "statement_type", "type": "TEXT", "is_primary_key": False, "description": "IncomeStatement, BalanceSheet, etc."},
                {"name": "reporting_type", "type": "TEXT", "is_primary_key": False, "description": "'consolidated' or 'standalone'"},
                {"name": "is_restated", "type": "BOOLEAN", "is_primary_key": False, "description": "Whether the record represents an amended restatement"},
                {"name": "source", "type": "TEXT", "is_primary_key": False, "description": "SEC EDGAR filing source"}
            ]
        },
        {
            "name": "financial_concepts",
            "description": "Taxonomy catalog defining recognized financial concepts, synonyms, and categories.",
            "columns": [
                {"name": "id", "type": "INTEGER", "is_primary_key": True, "description": "Concept ID"},
                {"name": "concept", "type": "TEXT", "is_primary_key": False, "description": "Concept tag name"},
                {"name": "category", "type": "TEXT", "is_primary_key": False, "description": "Accounting category"},
                {"name": "description", "type": "TEXT", "is_primary_key": False, "description": "Detailed business definition"},
                {"name": "synonyms", "type": "JSON", "is_primary_key": False, "description": "Alternative natural language terms"},
                {"name": "unit", "type": "TEXT", "is_primary_key": False, "description": "Standard measurement unit"}
            ]
        }
    ]

    return {
        "tables": tables_info,
        "companies": [c.to_dict() for c in companies],
        "concepts": [c.to_dict() for c in concepts],
        "schema_catalog_size": len(catalog_items),
    }
