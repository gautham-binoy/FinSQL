import pytest
from backend.app.database.connection import SessionLocal
from backend.app.retrieval.schema_retriever import SchemaRetriever


@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.close()


def test_schema_retriever_apple_microsoft(db):
    retriever = SchemaRetriever(db)
    res = retriever.retrieve(
        question="Compare Apple's revenue and Microsoft's revenue in 2023.",
        detected_entities=["Apple Inc.", "Microsoft Corporation"],
        detected_metrics=["Revenue"]
    )
    assert len(res["retrieved_items"]) > 0
    assert "companies" in res["relevant_tables"]
    assert "financial_facts" in res["relevant_tables"]
    assert "Revenue" in res["relevant_concepts"]

    # Ensure column names were retrieved
    col_names = [it["column_name"] for it in res["retrieved_items"] if it["column_name"]]
    assert "company_id" in col_names or "company_name" in col_names
    assert "value" in col_names or "concept" in col_names
