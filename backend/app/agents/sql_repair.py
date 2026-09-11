import re
import json
from pathlib import Path
from typing import Dict, Any, Optional
from backend.app.config import settings

# Load repair prompt template
PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "sql_repair.txt"
SQL_REPAIR_PROMPT = PROMPT_PATH.read_text(encoding="utf-8") if PROMPT_PATH.exists() else ""


class SQLRepairAgent:
    """
    Agentic repair loop that analyzes database execution errors, AST validation failures,
    or empty result anomalies and synthesizes corrected SQL queries.
    """

    @classmethod
    def repair(
        cls,
        question: str,
        previous_sql: str,
        error_message: str,
        retrieved_schema: Dict[str, Any],
        attempt_number: int = 1
    ) -> Dict[str, Any]:
        """
        Synthesizes a repaired SQL query given the error feedback.
        """
        # 1. Try Gemini if configured and not demo mode
        if settings.GEMINI_API_KEY and not settings.DEMO_MODE:
            try:
                result = cls._repair_with_gemini(question, previous_sql, error_message, retrieved_schema)
                if result and result.get("sql"):
                    return result
            except Exception as e:
                print(f"Notice: Gemini SQL repair failed ({e}), using heuristic repair.")

        # 2. Deterministic repair heuristics
        return cls._repair_heuristically(question, previous_sql, error_message, attempt_number)

    @classmethod
    def _repair_with_gemini(
        cls,
        question: str,
        previous_sql: str,
        error_message: str,
        retrieved_schema: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        from google import genai
        client = genai.Client(api_key=settings.GEMINI_API_KEY)

        prompt = SQL_REPAIR_PROMPT.format(
            question=question,
            previous_sql=previous_sql,
            error_message=error_message,
            retrieved_schema=retrieved_schema.get("prompt_schema_text", "")
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

        return json.loads(text_content)

    @classmethod
    def _repair_heuristically(
        cls,
        question: str,
        previous_sql: str,
        error_message: str,
        attempt: int
    ) -> Dict[str, Any]:
        sql = previous_sql
        err_low = error_message.lower()
        strategy = "GENERAL_REPAIR"

        # Case 1: Column name fix (e.g. fiscalYear -> fiscal_year)
        if "fiscalyear" in err_low or "year" in err_low:
            sql = re.sub(r"\bfiscalYear\b", "fiscal_year", sql, flags=re.IGNORECASE)
            sql = re.sub(r"\bf\.year\b", "f.fiscal_year", sql, flags=re.IGNORECASE)
            strategy = "CORRECTED_COLUMN_NAME"

        # Case 2: Table name fix (e.g. company -> companies)
        if "company " in err_low or "no such table: company" in err_low:
            sql = re.sub(r"\bFROM company\b", "FROM companies", sql, flags=re.IGNORECASE)
            sql = re.sub(r"\bJOIN company\b", "JOIN companies", sql, flags=re.IGNORECASE)
            strategy = "CORRECTED_TABLE_NAME"

        # Case 3: Missing quotes around string literals
        if "near" in err_low or "syntax" in err_low:
            # Replace double quotes on strings with single quotes
            sql = re.sub(r'\"([A-Za-z0-9_]+)\"', r"'\1'", sql)
            strategy = "FIXED_SYNTAX_QUOTES"

        # Case 4: 0 rows returned due to over-filtering
        if "0 rows" in err_low:
            # Relax is_restated or reporting_type
            if "is_restated" in sql:
                sql = re.sub(r"\s+AND\s+f\.is_restated\s*=\s*(FALSE|0)", "", sql, flags=re.IGNORECASE)
                strategy = "RELAXED_RESTATEMENT_FILTER"
            elif "reporting_type" in sql:
                sql = re.sub(r"\s+AND\s+f\.reporting_type\s*=\s*'consolidated'", "", sql, flags=re.IGNORECASE)
                strategy = "RELAXED_REPORTING_FILTER"

        # Clean trailing semicolons/whitespace
        sql = sql.strip()
        if not sql.endswith(";"):
            sql += ";"

        return {
            "sql": sql,
            "explanation": f"Repaired SQL query on attempt #{attempt} applying strategy {strategy} for error: {error_message}",
            "repair_strategy": strategy,
            "confidence": 0.88
        }
