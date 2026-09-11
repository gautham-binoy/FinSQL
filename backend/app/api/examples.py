from fastapi import APIRouter
from typing import List, Dict, Any

router = APIRouter(prefix="/api/examples", tags=["Examples"])

EXAMPLE_QUESTIONS: List[Dict[str, Any]] = [
    {
        "id": "ex_01",
        "category": "simple_lookup",
        "question": "What was Apple's revenue in 2023?",
        "description": "Basic single-metric scalar lookup with fiscal year resolution.",
        "difficulty": "Easy"
    },
    {
        "id": "ex_02",
        "category": "comparison",
        "question": "Compare Apple's revenue with Microsoft's revenue in 2023.",
        "description": "Multi-company comparison query with fiscal period alignment.",
        "difficulty": "Easy"
    },
    {
        "id": "ex_03",
        "category": "trend",
        "question": "Show Apple's revenue from 2020 to 2025.",
        "description": "Multi-year time-series analysis generating a trend line chart.",
        "difficulty": "Medium"
    },
    {
        "id": "ex_04",
        "category": "ranking",
        "question": "Which company had the highest revenue in 2023?",
        "description": "Ordered ranking across all reporting companies in the database.",
        "difficulty": "Medium"
    },
    {
        "id": "ex_05",
        "category": "simple_lookup",
        "question": "What was Microsoft's net income in 2023?",
        "description": "Profitability lookup for Microsoft in fiscal 2023.",
        "difficulty": "Easy"
    },
    {
        "id": "ex_06",
        "category": "comparison",
        "question": "Compare the net income of Apple and Microsoft from 2021 to 2023.",
        "description": "Multi-year, multi-company profitability comparison.",
        "difficulty": "Medium"
    },
    {
        "id": "ex_07",
        "category": "growth",
        "question": "What was Apple's revenue growth between 2022 and 2023?",
        "description": "Calculates percentage change using CTEs or period self-joins.",
        "difficulty": "Hard"
    },
    {
        "id": "ex_08",
        "category": "aggregation",
        "question": "What was the average revenue of the companies in 2023?",
        "description": "SQL aggregation (AVG, COUNT) across all companies in the dataset.",
        "difficulty": "Medium"
    },
    {
        "id": "ex_09",
        "category": "calculation",
        "question": "Which company had the highest net income margin in 2023?",
        "description": "Ratio calculation across two distinct metrics (NetIncome / Revenue * 100).",
        "difficulty": "Hard"
    },
    {
        "id": "ex_10",
        "category": "multi_metric",
        "question": "Give me Apple's revenue and net income for the last five fiscal years.",
        "description": "Multiple accounting concepts over historical multi-year periods.",
        "difficulty": "Hard"
    },
    {
        "id": "ex_11",
        "category": "ranking",
        "question": "Which company had the highest total assets in 2023?",
        "description": "Balance sheet metric ranking across enterprises.",
        "difficulty": "Medium"
    },
    {
        "id": "ex_12",
        "category": "simple_lookup",
        "question": "What was Nvidia's revenue in 2024?",
        "description": "Examines explosive semiconductor revenue growth in fiscal 2024.",
        "difficulty": "Easy"
    },
    {
        "id": "ex_13",
        "category": "comparison",
        "question": "Compare the cash holdings of Google and Amazon in 2023.",
        "description": "Balance sheet liquid assets comparison (CashAndCashEquivalents).",
        "difficulty": "Medium"
    },
    {
        "id": "ex_14",
        "category": "financial_domain",
        "question": "Show Apple's consolidated revenue in 2023 excluding restatements.",
        "description": "Financial trap resolution: enforces consolidated reporting and latest filing.",
        "difficulty": "Hard"
    },
    {
        "id": "ex_15",
        "category": "trend",
        "question": "Show Tesla's net income from 2020 to 2025.",
        "description": "Tracks profitability trajectory from initial profit to scale.",
        "difficulty": "Medium"
    }
]


@router.get("")
def get_examples():
    """
    Returns curated example questions covering diverse financial queries.
    """
    return {
        "count": len(EXAMPLE_QUESTIONS),
        "examples": EXAMPLE_QUESTIONS
    }
