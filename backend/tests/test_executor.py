import pytest
from backend.app.database.connection import SessionLocal
from backend.app.database.executor import SQLExecutor


@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.close()


def test_executor_valid_query(db):
    executor = SQLExecutor(db)
    sql = "SELECT ticker, company_name FROM companies WHERE ticker = 'AAPL';"
    res = executor.execute_query(sql)
    assert res["success"] is True
    assert res["row_count"] == 1
    assert res["rows"][0]["ticker"] == "AAPL"
    assert res["execution_time_ms"] >= 0


def test_executor_invalid_query(db):
    executor = SQLExecutor(db)
    sql = "SELECT nonexistent_column FROM companies;"
    res = executor.execute_query(sql)
    assert res["success"] is False
    assert res["error_type"] in ["COLUMN_NOT_FOUND", "SQL_EXECUTION_ERROR"]
    assert res["row_count"] == 0
