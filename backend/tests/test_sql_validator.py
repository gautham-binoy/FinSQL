import pytest
from backend.app.validation.sql_validator import SQLValidator


def test_sql_validator_select_valid():
    sql = "SELECT c.company_name, f.value FROM companies c JOIN financial_facts f ON c.company_id = f.company_id WHERE f.fiscal_year = 2023;"
    res = SQLValidator.validate(sql)
    assert res["valid"] is True
    assert res["error_type"] is None
    assert "companies" in res["ast_tables"]
    assert "financial_facts" in res["ast_tables"]


def test_sql_validator_cte_valid():
    sql = """WITH y22 AS (
        SELECT company_id, value FROM financial_facts WHERE fiscal_year = 2022
    ),
    y23 AS (
        SELECT company_id, value FROM financial_facts WHERE fiscal_year = 2023
    )
    SELECT y23.value - y22.value FROM y23 JOIN y22 ON y23.company_id = y22.company_id;"""
    res = SQLValidator.validate(sql)
    assert res["valid"] is True


def test_sql_validator_reject_destructive():
    for dangerous in [
        "DROP TABLE companies;",
        "DELETE FROM financial_facts;",
        "UPDATE companies SET ticker = 'HACK';",
        "INSERT INTO companies (ticker, company_name) VALUES ('X', 'Fake');",
        "ALTER TABLE companies DROP COLUMN country;",
        "TRUNCATE TABLE financial_facts;"
    ]:
        res = SQLValidator.validate(dangerous)
        assert res["valid"] is False
        assert res["error_type"] == "DANGEROUS_OPERATION"


def test_sql_validator_reject_unapproved_table():
    sql = "SELECT username, password FROM users;"
    res = SQLValidator.validate(sql)
    assert res["valid"] is False
    assert res["error_type"] == "UNAPPROVED_TABLE"


def test_sql_validator_reject_multi_statement():
    sql = "SELECT * FROM companies; DROP TABLE companies;"
    res = SQLValidator.validate(sql)
    assert res["valid"] is False
