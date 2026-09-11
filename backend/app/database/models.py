import json
from typing import List, Optional
from datetime import date
from sqlalchemy import (
    Column, Integer, BigInteger, String, Text, Numeric, Date, Boolean, ForeignKey, Index
)
from sqlalchemy.types import TypeDecorator, TEXT
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class JSONEncodedList(TypeDecorator):
    """Platform-independent list of strings stored as JSON text."""
    impl = TEXT
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return "[]"
        if isinstance(value, list):
            return json.dumps(value)
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return []
        if isinstance(value, str):
            try:
                return json.loads(value)
            except Exception:
                return [v.strip() for v in value.strip("{}").split(",") if v.strip()]
        return value


class Company(Base):
    __tablename__ = "companies"

    company_id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(20), unique=True, nullable=False, index=True)
    company_name = Column(Text, nullable=False, index=True)
    industry = Column(Text, nullable=True)
    sector = Column(Text, nullable=True)
    country = Column(Text, nullable=True, default="USA")

    facts = relationship("FinancialFact", back_populates="company", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "company_id": self.company_id,
            "ticker": self.ticker,
            "company_name": self.company_name,
            "industry": self.industry,
            "sector": self.sector,
            "country": self.country,
        }


class FinancialFact(Base):
    __tablename__ = "financial_facts"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.company_id"), nullable=False, index=True)
    concept = Column(Text, nullable=False, index=True)
    concept_description = Column(Text, nullable=True)
    value = Column(Numeric(precision=20, scale=4), nullable=True)
    unit = Column(Text, nullable=False, default="USD")
    period_start = Column(Date, nullable=True)
    period_end = Column(Date, nullable=True)
    filing_date = Column(Date, nullable=True)
    fiscal_year = Column(Integer, nullable=False, index=True)
    fiscal_period = Column(Text, nullable=False, default="FY")  # 'FY', 'Q1', 'Q2', 'Q3', 'Q4'
    form = Column(Text, nullable=True, default="10-K")          # '10-K', '10-Q'
    statement_type = Column(Text, nullable=True)                # 'IncomeStatement', 'BalanceSheet', 'CashFlow'
    reporting_type = Column(Text, nullable=False, default="consolidated") # 'consolidated', 'standalone'
    is_restated = Column(Boolean, default=False, nullable=False)
    source = Column(Text, nullable=True, default="SEC EDGAR 10-K")

    company = relationship("Company", back_populates="facts")

    __table_args__ = (
        Index("idx_fact_company_year_concept", "company_id", "fiscal_year", "concept"),
        Index("idx_fact_concept_reporting", "concept", "reporting_type", "is_restated"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "company_id": self.company_id,
            "ticker": self.company.ticker if self.company else None,
            "concept": self.concept,
            "concept_description": self.concept_description,
            "value": float(self.value) if self.value is not None else None,
            "unit": self.unit,
            "period_start": self.period_start.isoformat() if self.period_start else None,
            "period_end": self.period_end.isoformat() if self.period_end else None,
            "filing_date": self.filing_date.isoformat() if self.filing_date else None,
            "fiscal_year": self.fiscal_year,
            "fiscal_period": self.fiscal_period,
            "form": self.form,
            "statement_type": self.statement_type,
            "reporting_type": self.reporting_type,
            "is_restated": self.is_restated,
            "source": self.source,
        }


class FinancialConcept(Base):
    __tablename__ = "financial_concepts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    concept = Column(Text, unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(Text, nullable=True) # e.g. 'IncomeStatement', 'BalanceSheet', 'CashFlow', 'Ratios'
    synonyms = Column(JSONEncodedList, nullable=False, default=list)
    unit = Column(Text, nullable=True, default="USD")

    def to_dict(self):
        return {
            "id": self.id,
            "concept": self.concept,
            "description": self.description,
            "category": self.category,
            "synonyms": self.synonyms,
            "unit": self.unit,
        }


class SchemaCatalog(Base):
    """
    Metadata catalog describing tables, columns, concepts, sample values,
    and business definitions with their vector embeddings.
    """
    __tablename__ = "schema_catalog"

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_type = Column(String(50), nullable=False) # 'table', 'column', 'concept'
    table_name = Column(String(100), nullable=True)
    column_name = Column(String(100), nullable=True)
    concept_name = Column(String(100), nullable=True)
    display_name = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    synonyms = Column(JSONEncodedList, nullable=False, default=list)
    sample_values = Column(Text, nullable=True)
    embedding_json = Column(Text, nullable=True) # Vector stored as JSON string for universal compatibility

    def to_dict(self):
        return {
            "id": self.id,
            "item_type": self.item_type,
            "table_name": self.table_name,
            "column_name": self.column_name,
            "concept_name": self.concept_name,
            "display_name": self.display_name,
            "description": self.description,
            "synonyms": self.synonyms,
            "sample_values": self.sample_values,
        }
