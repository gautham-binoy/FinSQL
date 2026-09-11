import pytest
from backend.app.agents.sql_repair import SQLRepairAgent


def test_sql_repair_column_name():
    faulty = "SELECT c.company_name, f.value FROM companies c JOIN financial_facts f ON c.company_id = f.company_id WHERE f.fiscalYear = 2023;"
    err = "no such column: f.fiscalYear"
    repaired = SQLRepairAgent.repair(
        question="Apple revenue in 2023",
        previous_sql=faulty,
        error_message=err,
        retrieved_schema={},
        attempt_number=1
    )
    assert "fiscal_year" in repaired["sql"]
    assert "fiscalYear" not in repaired["sql"]


def test_sql_repair_table_name():
    faulty = "SELECT * FROM company WHERE ticker = 'AAPL';"
    err = "no such table: company"
    repaired = SQLRepairAgent.repair(
        question="Apple ticker",
        previous_sql=faulty,
        error_message=err,
        retrieved_schema={},
        attempt_number=1
    )
    assert "FROM companies" in repaired["sql"]
