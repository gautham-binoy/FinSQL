import pytest
from backend.app.database.connection import SessionLocal
from backend.app.agents.question_analyzer import QuestionAnalyzer


@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.close()


def test_question_analyzer_simple(db):
    analyzer = QuestionAnalyzer(db)
    res = analyzer.analyze("What was Apple's revenue in 2023?")
    assert "Apple Inc." in res["entities"]
    assert "AAPL" in res["tickers"]
    assert "Revenue" in res["metrics"]
    assert res["time_period"]["start_year"] == 2023


def test_question_analyzer_comparison(db):
    analyzer = QuestionAnalyzer(db)
    res = analyzer.analyze("Compare Apple's revenue with Microsoft's revenue in 2023.")
    assert "AAPL" in res["tickers"]
    assert "MSFT" in res["tickers"]
    assert "Revenue" in res["metrics"]
    assert res["operation"] == "comparison"


def test_question_analyzer_growth(db):
    analyzer = QuestionAnalyzer(db)
    res = analyzer.analyze("What was Apple's revenue growth between 2022 and 2023?")
    assert res["operation"] == "growth"
    assert res["requires_calculation"] is True
    assert res["calculation_type"] == "percentage_change"
    assert res["time_period"]["start_year"] == 2022
    assert res["time_period"]["end_year"] == 2023
