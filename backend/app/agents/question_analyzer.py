import re
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.app.config import settings
from backend.app.database.models import Company, FinancialConcept

# Load prompt template
PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "question_analysis.txt"
QUESTION_ANALYSIS_PROMPT = PROMPT_PATH.read_text(encoding="utf-8") if PROMPT_PATH.exists() else ""

KNOWN_COMPANIES = {
    "apple": ("AAPL", "Apple Inc."),
    "aapl": ("AAPL", "Apple Inc."),
    "microsoft": ("MSFT", "Microsoft Corporation"),
    "msft": ("MSFT", "Microsoft Corporation"),
    "amazon": ("AMZN", "Amazon.com, Inc."),
    "amzn": ("AMZN", "Amazon.com, Inc."),
    "alphabet": ("GOOGL", "Alphabet Inc."),
    "google": ("GOOGL", "Alphabet Inc."),
    "googl": ("GOOGL", "Alphabet Inc."),
    "goog": ("GOOGL", "Alphabet Inc."),
    "tesla": ("TSLA", "Tesla, Inc."),
    "tsla": ("TSLA", "Tesla, Inc."),
    "nvidia": ("NVDA", "Nvidia Corporation"),
    "nvda": ("NVDA", "Nvidia Corporation"),
    "meta": ("META", "Meta Platforms, Inc."),
    "facebook": ("META", "Meta Platforms, Inc."),
}

CONCEPT_SYNONYM_MAP = {
    "revenue": "Revenue",
    "sales": "Revenue",
    "turnover": "Revenue",
    "net income": "NetIncome",
    "profit": "NetIncome",
    "net profit": "NetIncome",
    "earnings": "NetIncome",
    "gross profit": "GrossProfit",
    "gross margin": "GrossProfit",
    "operating income": "OperatingIncome",
    "operating profit": "OperatingIncome",
    "ebit": "OperatingIncome",
    "assets": "TotalAssets",
    "total assets": "TotalAssets",
    "liabilities": "TotalLiabilities",
    "debt": "TotalLiabilities",
    "cash": "CashAndCashEquivalents",
    "cash and cash equivalents": "CashAndCashEquivalents",
    "operating expenses": "OperatingExpenses",
    "opex": "OperatingExpenses",
    "eps": "EarningsPerShare",
    "earnings per share": "EarningsPerShare",
}


class QuestionAnalyzer:
    """
    Extracts structured intent, entities, metrics, periods, and operations
    from natural language questions using Gemini or local semantic heuristics.
    """

    def __init__(self, db_session: Session):
        self.db = db_session

    def analyze(self, question: str) -> Dict[str, Any]:
        """
        Analyzes question and validates against database entity catalogs.
        """
        raw_analysis = None

        # 1. Try Gemini if configured and not demo mode
        if settings.GEMINI_API_KEY and not settings.DEMO_MODE:
            try:
                raw_analysis = self._analyze_with_gemini(question)
            except Exception as e:
                print(f"Notice: Gemini question analysis failed ({e}), using heuristic fallback.")
                raw_analysis = None

        # 2. Fallback heuristic analysis if Gemini wasn't available or errored
        if raw_analysis is None:
            raw_analysis = self._heuristic_analysis(question)

        # 3. Ground truth validation against database catalog
        validated_analysis = self._validate_and_enrich(raw_analysis, question)
        return validated_analysis

    def _analyze_with_gemini(self, question: str) -> Optional[Dict[str, Any]]:
        from google import genai
        client = genai.Client(api_key=settings.GEMINI_API_KEY)

        prompt = f"{QUESTION_ANALYSIS_PROMPT}\n\nQuestion: \"{question}\"\nJSON Output:"
        response = client.models.generate_content(
            model=settings.MODEL_NAME,
            contents=prompt,
        )

        text_content = response.text.strip()
        # Clean JSON markdown if model wrapped it
        if "```json" in text_content:
            text_content = text_content.split("```json")[1].split("```")[0].strip()
        elif "```" in text_content:
            text_content = text_content.split("```")[1].split("```")[0].strip()

        return json.loads(text_content)

    def _heuristic_analysis(self, question: str) -> Dict[str, Any]:
        q_lower = question.lower()

        # Detect companies
        entities = []
        tickers = []
        for key, (t, cname) in KNOWN_COMPANIES.items():
            pattern = rf"\b{re.escape(key)}\b"
            if re.search(pattern, q_lower):
                if cname not in entities:
                    entities.append(cname)
                    tickers.append(t)

        # Detect metrics
        metrics = []
        for term, std_concept in CONCEPT_SYNONYM_MAP.items():
            pattern = rf"\b{re.escape(term)}\b"
            if re.search(pattern, q_lower):
                if std_concept not in metrics:
                    metrics.append(std_concept)

        if not metrics:
            metrics = ["Revenue"] # Default metric if general question

        # Detect years
        years_found = [int(y) for y in re.findall(r"\b(202[0-5])\b", question)]
        years_found = sorted(list(set(years_found)))

        # Detect range indicators
        is_range = any(w in q_lower for w in ["from", "between", "to", "over", "last 5", "last five", "historical"])
        if ("last 5" in q_lower or "last five" in q_lower) and not years_found:
            years_found = [2021, 2022, 2023, 2024, 2025]
            time_period = {
                "type": "range",
                "start_year": 2021,
                "end_year": 2025,
                "years": years_found
            }
        elif len(years_found) >= 2:
            time_period = {
                "type": "range",
                "start_year": min(years_found),
                "end_year": max(years_found),
                "years": list(range(min(years_found), max(years_found) + 1))
            }
        elif len(years_found) == 1:
            time_period = {
                "type": "single_year",
                "start_year": years_found[0],
                "end_year": years_found[0],
                "years": years_found
            }
        else:
            time_period = {
                "type": "all",
                "start_year": 2020,
                "end_year": 2025,
                "years": [2020, 2021, 2022, 2023, 2024, 2025]
            }

        # Detect operation
        operation = "lookup"
        requires_calc = False
        calc_type = None

        if "growth" in q_lower or "increase" in q_lower or "change" in q_lower:
            operation = "growth"
            requires_calc = True
            calc_type = "percentage_change"
        elif "margin" in q_lower:
            operation = "calculation"
            requires_calc = True
            calc_type = "margin_ratio"
        elif "compare" in q_lower or "vs" in q_lower or len(entities) > 1:
            operation = "comparison"
        elif "highest" in q_lower or "top" in q_lower or "lowest" in q_lower or "rank" in q_lower:
            operation = "ranking"
        elif "average" in q_lower or "total" in q_lower or "sum" in q_lower or "mean" in q_lower:
            operation = "aggregation"
        elif time_period["type"] == "range" or len(time_period["years"]) > 1:
            operation = "trend"

        return {
            "entities": entities,
            "tickers": tickers,
            "metrics": metrics,
            "time_period": time_period,
            "operation": operation,
            "filters": {
                "reporting_type": "standalone" if "standalone" in q_lower else "consolidated",
                "is_restated": True if "restated" in q_lower else False
            },
            "requires_calculation": requires_calc,
            "calculation_type": calc_type,
            "ambiguity": "Fiscal year assumed equal to reporting period"
        }

    def _validate_and_enrich(self, analysis: Dict[str, Any], question: str) -> Dict[str, Any]:
        """
        Cross-checks extracted entities and concepts with the database tables.
        """
        validated = dict(analysis)

        # Validate entities in DB
        db_companies = self.db.query(Company).all()
        comp_lookup = {c.company_name.lower(): c.ticker for c in db_companies}
        ticker_lookup = {c.ticker.lower(): c.company_name for c in db_companies}

        verified_tickers = []
        verified_entities = []

        # Check by ticker or name
        for t in validated.get("tickers", []):
            if t.lower() in ticker_lookup:
                verified_tickers.append(t.upper())
                verified_entities.append(ticker_lookup[t.lower()])

        for e in validated.get("entities", []):
            e_low = e.lower()
            if e_low in comp_lookup:
                tk = comp_lookup[e_low]
                if tk not in verified_tickers:
                    verified_tickers.append(tk)
                    verified_entities.append(e)

        # If entities weren't specified, check if it's an industry-wide question
        if not verified_tickers and any(w in question.lower() for w in ["companies", "all", "average", "highest", "sector"]):
            # All companies question
            pass

        validated["tickers"] = verified_tickers
        validated["entities"] = verified_entities

        # Validate concepts in DB
        db_concepts = {c.concept.lower(): c.concept for c in self.db.query(FinancialConcept).all()}
        verified_metrics = []
        for m in validated.get("metrics", []):
            if m.lower() in db_concepts:
                verified_metrics.append(db_concepts[m.lower()])
        if not verified_metrics:
            verified_metrics = ["Revenue"]

        validated["metrics"] = verified_metrics
        return validated
