import time
import uuid
import re
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from backend.app.config import settings
from backend.app.database.executor import SQLExecutor


class BaselineAgent:
    """
    Baseline Text-to-SQL implementation for empirical scientific comparison.
    Generates SQL directly without schema retrieval, without AST safety validation,
    without error feedback recovery, and without financial result verification.
    """

    def __init__(self, db_session: Session):
        self.db = db_session
        self.executor = SQLExecutor(db_session)

    def run(self, question: str) -> Dict[str, Any]:
        request_id = str(uuid.uuid4())
        start_time = time.perf_counter()

        sql = ""
        # 1. Try Gemini if available
        if settings.GEMINI_API_KEY and not settings.DEMO_MODE:
            try:
                sql = self._generate_with_gemini(question)
            except Exception as e:
                print(f"Notice: Baseline Gemini call failed: {e}")
                sql = ""

        # 2. Simple baseline naive heuristic generator
        if not sql:
            sql = self._generate_naive_sql(question)

        # 3. Direct execution without AST validation or repair loops
        exec_start = time.perf_counter()
        execution_result = self.executor.execute_query(sql)
        exec_time = round((time.perf_counter() - exec_start) * 1000, 2)

        total_latency = round((time.perf_counter() - start_time) * 1000, 2)

        rows = execution_result.get("rows", [])
        if execution_result.get("success") and rows:
            answer = f"The query executed and returned {len(rows)} record(s)."
        elif not execution_result.get("success"):
            answer = f"SQL Execution Failed: {execution_result.get('message')}"
        else:
            answer = "The query executed but returned 0 rows."

        return {
            "request_id": request_id,
            "question": question,
            "sql": sql,
            "execution": execution_result,
            "answer": answer,
            "latency_ms": total_latency,
            "mode": "Baseline Text-to-SQL",
            "retrieved_schema": [],
            "attempts": [{"attempt": 1, "sql": sql, "execution": execution_result}],
            "retry_count": 0,
            "trace": [
                {"step": "sql_generation", "title": "Direct Prompt to SQL (No Retrieval)", "status": "completed", "latency_ms": total_latency - exec_time},
                {"step": "execution", "title": "Direct DB Query (No AST Validation or Verification)", "status": "completed" if execution_result.get("success") else "failed", "latency_ms": exec_time}
            ]
        }

    def _generate_with_gemini(self, question: str) -> str:
        from google import genai
        client = genai.Client(api_key=settings.GEMINI_API_KEY)

        prompt = f"""You are a basic Text-to-SQL bot.
Generate a SQL query for this question without schema details:
Question: {question}

Return ONLY the raw SQL query, no markdown."""

        response = client.models.generate_content(
            model=settings.MODEL_NAME,
            contents=prompt,
        )
        text_content = response.text.strip()
        if "```sql" in text_content:
            text_content = text_content.split("```sql")[1].split("```")[0].strip()
        elif "```" in text_content:
            text_content = text_content.split("```")[1].split("```")[0].strip()
        return text_content

    def _generate_naive_sql(self, question: str) -> str:
        """
        Naive baseline SQL generator that often makes typical Text-to-SQL mistakes:
        - omitting reporting_type filter
        - omitting restatement filter (mixing restatements)
        - guessing column names (e.g. year instead of fiscal_year)
        - missing proper joins
        """
        q_low = question.lower()
        if "growth" in q_low:
            # Typical naive error: doesn't use CTE or joins, just selects raw facts
            return "SELECT company_id, concept, value, fiscal_year FROM financial_facts WHERE concept = 'Revenue';"
        elif "apple" in q_low and "microsoft" in q_low:
            # Often produces duplicate rows because it misses reporting_type / is_restated
            return "SELECT c.company_name, f.value, f.fiscal_year FROM companies c JOIN financial_facts f ON c.company_id = f.company_id WHERE (c.company_name LIKE '%Apple%' OR c.company_name LIKE '%Microsoft%') AND f.concept = 'Revenue' AND f.fiscal_year = 2023;"
        elif "apple" in q_low:
            return "SELECT c.company_name, f.value, f.fiscal_year FROM companies c JOIN financial_facts f ON c.company_id = f.company_id WHERE c.company_name LIKE '%Apple%' AND f.concept = 'Revenue' AND f.fiscal_year = 2023;"
        elif "highest" in q_low or "top" in q_low:
            return "SELECT c.company_name, f.value FROM companies c JOIN financial_facts f ON c.company_id = f.company_id WHERE f.concept = 'Revenue' ORDER BY f.value DESC LIMIT 5;"
        else:
            return "SELECT * FROM financial_facts LIMIT 10;"
