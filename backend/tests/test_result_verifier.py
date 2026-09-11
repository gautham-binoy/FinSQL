import pytest
from backend.app.validation.result_verifier import ResultVerifier


def test_result_verifier_empty():
    res = ResultVerifier.verify(rows=[], columns=["company_name", "value"])
    assert res["valid"] is False
    assert res["needs_repair"] is True
    assert res["checks"]["empty_result"] is True


def test_result_verifier_duplicate_records():
    rows = [
        {"company_name": "Apple Inc.", "fiscal_year": 2023, "concept": "Revenue", "value": 383285000000, "is_restated": False},
        {"company_name": "Apple Inc.", "fiscal_year": 2023, "concept": "Revenue", "value": 383285000000, "is_restated": True},
    ]
    res = ResultVerifier.verify(rows=rows, columns=["company_name", "fiscal_year", "concept", "value", "is_restated"])
    assert res["checks"]["duplicate_rows"] is True
    assert res["checks"]["restatement_conflict"] is True


def test_result_verifier_clean_row():
    rows = [
        {"company_name": "Apple Inc.", "fiscal_year": 2023, "concept": "Revenue", "value": 383285000000, "unit": "USD", "is_restated": False}
    ]
    res = ResultVerifier.verify(rows=rows, columns=["company_name", "fiscal_year", "concept", "value", "unit", "is_restated"])
    assert res["valid"] is True
    assert res["needs_repair"] is False
    assert res["checks"]["duplicate_rows"] is False
