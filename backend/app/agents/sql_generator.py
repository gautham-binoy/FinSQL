import json
from pathlib import Path
from typing import Dict, Any, Optional
from backend.app.config import settings

# Load prompt template
PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "sql_generation.txt"
SQL_GENERATION_PROMPT = PROMPT_PATH.read_text(encoding="utf-8") if PROMPT_PATH.exists() else ""


class SQLGenerator:
    """
    Generates read-only SQL queries grounded in the retrieved schema context
    and structured question analysis using Gemini with deterministic fallback.
    """

    @classmethod
    def generate(
        cls,
        question: str,
        analysis: Dict[str, Any],
        retrieved_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generates structured SQL output.
        """
        # 1. Use Gemini if configured and not in demo mode
        if settings.GEMINI_API_KEY and not settings.DEMO_MODE:
            try:
                result = cls._generate_with_gemini(question, analysis, retrieved_schema)
                if result and result.get("sql"):
                    return result
            except Exception as e:
                print(f"Notice: Gemini SQL generation failed ({e}), falling back to deterministic generator.")

        # 2. Deterministic generator
        return cls._generate_deterministic(question, analysis, retrieved_schema)

    @classmethod
    def _generate_with_gemini(
        cls,
        question: str,
        analysis: Dict[str, Any],
        retrieved_schema: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        from google import genai
        client = genai.Client(api_key=settings.GEMINI_API_KEY)

        prompt = SQL_GENERATION_PROMPT.format(
            question=question,
            analysis_json=json.dumps(analysis, indent=2),
            retrieved_schema=retrieved_schema.get("prompt_schema_text", ""),
            metric_name=analysis.get("metrics", ["Revenue"])[0] if analysis.get("metrics") else "Revenue"
        )

        response = client.models.generate_content(
            model=settings.MODEL_NAME,
            contents=prompt,
        )

        text_content = response.text.strip()
        if "```json" in text_content:
            text_content = text_content.split("```json")[1].split("```")[0].strip()
        elif "```" in text_content:
            text_content = text_content.split("```")[1].split("```")[0].strip()

        parsed = json.loads(text_content)
        return parsed

    @classmethod
    def _generate_deterministic(
        cls,
        question: str,
        analysis: Dict[str, Any],
        retrieved_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generates correct financial SQL using analytical query templates.
        """
        q_low = question.lower()
        tickers = analysis.get("tickers", [])
        metrics = analysis.get("metrics", ["Revenue"])
        time_period = analysis.get("time_period", {})
        operation = analysis.get("operation", "lookup")
        requires_calc = analysis.get("requires_calculation", False)
        calc_type = analysis.get("calculation_type")

        primary_metric = metrics[0] if metrics else "Revenue"
        target_year = time_period.get("start_year", 2023)

        # 1. Growth calculation (e.g. Apple revenue growth between 2022 and 2023)
        if requires_calc and calc_type == "percentage_change":
            y_start = time_period.get("start_year", 2022)
            y_end = time_period.get("end_year", 2023)
            ticker = tickers[0] if tickers else "AAPL"
            sql = f"""WITH y_start AS (
    SELECT c.company_id, c.company_name, c.ticker, f.value AS start_val
    FROM companies c
    JOIN financial_facts f ON c.company_id = f.company_id
    WHERE c.ticker = '{ticker}' AND f.concept = '{primary_metric}' AND f.fiscal_year = {y_start}
      AND f.fiscal_period = 'FY' AND f.reporting_type = 'consolidated' AND f.is_restated = FALSE
),
y_end AS (
    SELECT c.company_id, c.company_name, c.ticker, f.value AS end_val
    FROM companies c
    JOIN financial_facts f ON c.company_id = f.company_id
    WHERE c.ticker = '{ticker}' AND f.concept = '{primary_metric}' AND f.fiscal_year = {y_end}
      AND f.fiscal_period = 'FY' AND f.reporting_type = 'consolidated' AND f.is_restated = FALSE
)
SELECT 
    y_end.company_name,
    y_end.ticker,
    '{primary_metric}' AS concept,
    {y_start} AS start_year,
    y_start.start_val,
    {y_end} AS end_year,
    y_end.end_val,
    ROUND(((y_end.end_val - y_start.start_val) * 100.0 / y_start.start_val), 2) AS growth_percentage
FROM y_end
JOIN y_start ON y_end.company_id = y_start.company_id;"""
            return {
                "sql": sql,
                "explanation": f"Calculated {primary_metric} percentage growth for {ticker} from {y_start} to {y_end} using CTEs.",
                "assumptions": ["Consolidated financial facts", "Full annual fiscal years (FY)", "Latest non-restated filings"],
                "confidence": 0.98
            }

        # 2. Net Income Margin / Margin Ratio
        if requires_calc and calc_type == "margin_ratio":
            sql = f"""WITH rev AS (
    SELECT company_id, value AS revenue
    FROM financial_facts
    WHERE concept = 'Revenue' AND fiscal_year = {target_year}
      AND fiscal_period = 'FY' AND reporting_type = 'consolidated' AND is_restated = FALSE
),
net AS (
    SELECT company_id, value AS net_income
    FROM financial_facts
    WHERE concept = 'NetIncome' AND fiscal_year = {target_year}
      AND fiscal_period = 'FY' AND reporting_type = 'consolidated' AND is_restated = FALSE
)
SELECT 
    c.company_name,
    c.ticker,
    {target_year} AS fiscal_year,
    rev.revenue,
    net.net_income,
    ROUND((net.net_income * 100.0 / rev.revenue), 2) AS net_income_margin_pct
FROM companies c
JOIN rev ON c.company_id = rev.company_id
JOIN net ON c.company_id = net.company_id
ORDER BY net_income_margin_pct DESC;"""
            return {
                "sql": sql,
                "explanation": f"Calculated Net Income Margin (NetIncome / Revenue * 100) for all companies in FY{target_year} ranked in descending order.",
                "assumptions": ["Consolidated financial facts", "Fiscal year 2023", "Non-restated statements"],
                "confidence": 0.97
            }

        # 3. Aggregation (e.g. Average revenue of companies in 2023)
        if operation == "aggregation":
            sql = f"""SELECT 
    f.concept,
    f.fiscal_year,
    ROUND(AVG(f.value), 2) AS average_value,
    COUNT(DISTINCT c.company_id) AS company_count,
    f.unit
FROM companies c
JOIN financial_facts f ON c.company_id = f.company_id
WHERE f.concept = '{primary_metric}'
  AND f.fiscal_year = {target_year}
  AND f.fiscal_period = 'FY'
  AND f.reporting_type = 'consolidated'
  AND f.is_restated = FALSE
GROUP BY f.concept, f.fiscal_year, f.unit;"""
            return {
                "sql": sql,
                "explanation": f"Calculated average {primary_metric} across all reporting companies in FY{target_year}.",
                "assumptions": ["Consolidated financial facts", "Annual period (FY)"],
                "confidence": 0.95
            }

        # 4. Ranking / Highest (e.g. Which company had highest revenue in 2023?)
        if operation == "ranking":
            order_dir = "ASC" if "lowest" in q_low else "DESC"
            sql = f"""SELECT 
    c.company_name,
    c.ticker,
    f.fiscal_year,
    f.concept,
    f.value,
    f.unit
FROM companies c
JOIN financial_facts f ON c.company_id = f.company_id
WHERE f.concept = '{primary_metric}'
  AND f.fiscal_year = {target_year}
  AND f.fiscal_period = 'FY'
  AND f.reporting_type = 'consolidated'
  AND f.is_restated = FALSE
ORDER BY f.value {order_dir};"""
            return {
                "sql": sql,
                "explanation": f"Ranked companies by {primary_metric} in FY{target_year} in {order_dir} order.",
                "assumptions": ["Consolidated financial facts", "Latest non-restated filings"],
                "confidence": 0.96
            }

        # 5. Multi-metric (e.g. Apple's revenue and net income for last 5 years)
        if len(metrics) > 1:
            concepts_in = ", ".join(f"'{m}'" for m in metrics)
            ticker_clause = f"c.ticker = '{tickers[0]}'" if tickers else "1=1"
            years = time_period.get("years", [])
            years_clause = f"f.fiscal_year >= {min(years)}" if years else f"f.fiscal_year = {target_year}"

            sql = f"""SELECT 
    c.company_name,
    c.ticker,
    f.fiscal_year,
    f.concept,
    f.value,
    f.unit
FROM companies c
JOIN financial_facts f ON c.company_id = f.company_id
WHERE {ticker_clause}
  AND f.concept IN ({concepts_in})
  AND {years_clause}
  AND f.fiscal_period = 'FY'
  AND f.reporting_type = 'consolidated'
  AND f.is_restated = FALSE
ORDER BY f.fiscal_year ASC, f.concept ASC;"""
            return {
                "sql": sql,
                "explanation": f"Retrieved multi-metric series ({', '.join(metrics)}) for {ticker_clause} across fiscal years.",
                "assumptions": ["Consolidated financial statements", "Annual FY periods"],
                "confidence": 0.95
            }

        # 6. Company Comparison (e.g. Compare Apple and Microsoft revenue)
        if len(tickers) > 1:
            tickers_in = ", ".join(f"'{t}'" for t in tickers)
            years = time_period.get("years", [target_year])
            if len(years) > 1:
                year_filter = f"f.fiscal_year BETWEEN {min(years)} AND {max(years)}"
            else:
                year_filter = f"f.fiscal_year = {years[0]}"

            sql = f"""SELECT 
    c.company_name,
    c.ticker,
    f.fiscal_year,
    f.concept,
    f.value,
    f.unit
FROM companies c
JOIN financial_facts f ON c.company_id = f.company_id
WHERE c.ticker IN ({tickers_in})
  AND f.concept = '{primary_metric}'
  AND {year_filter}
  AND f.fiscal_period = 'FY'
  AND f.reporting_type = 'consolidated'
  AND f.is_restated = FALSE
ORDER BY f.fiscal_year ASC, f.value DESC;"""
            return {
                "sql": sql,
                "explanation": f"Compared {primary_metric} between {', '.join(tickers)} for {year_filter}.",
                "assumptions": ["Consolidated accounts", "Standard fiscal year comparison"],
                "confidence": 0.96
            }

        # 7. Time-series / Multi-year trend
        if operation == "trend" or len(time_period.get("years", [])) > 1:
            years = time_period.get("years", [2020, 2021, 2022, 2023, 2024, 2025])
            ticker = tickers[0] if tickers else "AAPL"
            sql = f"""SELECT 
    c.company_name,
    c.ticker,
    f.fiscal_year,
    f.concept,
    f.value,
    f.unit
FROM companies c
JOIN financial_facts f ON c.company_id = f.company_id
WHERE c.ticker = '{ticker}'
  AND f.concept = '{primary_metric}'
  AND f.fiscal_year BETWEEN {min(years)} AND {max(years)}
  AND f.fiscal_period = 'FY'
  AND f.reporting_type = 'consolidated'
  AND f.is_restated = FALSE
ORDER BY f.fiscal_year ASC;"""
            return {
                "sql": sql,
                "explanation": f"Retrieved multi-year trend for {ticker} {primary_metric} from {min(years)} to {max(years)}.",
                "assumptions": ["Consolidated statements", "Full fiscal years"],
                "confidence": 0.97
            }

        # 8. Single lookup default (e.g. What was Apple's revenue in 2023?)
        ticker = tickers[0] if tickers else "AAPL"
        sql = f"""SELECT 
    c.company_name,
    c.ticker,
    f.fiscal_year,
    f.concept,
    f.value,
    f.unit
FROM companies c
JOIN financial_facts f ON c.company_id = f.company_id
WHERE c.ticker = '{ticker}'
  AND f.concept = '{primary_metric}'
  AND f.fiscal_year = {target_year}
  AND f.fiscal_period = 'FY'
  AND f.reporting_type = 'consolidated'
  AND f.is_restated = FALSE;"""

        return {
            "sql": sql,
            "explanation": f"Looked up {ticker} {primary_metric} for fiscal year {target_year}.",
            "assumptions": ["Consolidated reporting", "Latest non-restated filing", "Full fiscal year (FY)"],
            "confidence": 0.96
        }
