import time
from typing import Dict, Any, List, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session
from backend.app.config import settings


class SQLExecutor:
    """
    Safe execution engine with query timeout, row limits, duration measurement,
    and structured error mapping.
    """

    def __init__(self, db_session: Session):
        self.db = db_session
        self.max_rows = settings.MAX_RESULT_ROWS
        self.timeout_sec = settings.QUERY_TIMEOUT_SECONDS

    def execute_query(self, sql: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executes a validated read-only SQL query and returns structured results.
        """
        start_time = time.perf_counter()
        params = params or {}

        try:
            # Enforce max row limit if not already limited
            sql_clean = sql.strip().rstrip(";")

            # Execute with timeout if PostgreSQL
            execution_options = {}
            if settings.DATABASE_URL.startswith("postgresql"):
                execution_options["timeout"] = self.timeout_sec

            result_proxy = self.db.execute(
                text(sql_clean),
                params,
                execution_options=execution_options
            )

            # Extract column headers
            columns = list(result_proxy.keys()) if result_proxy.returns_rows else []

            # Fetch rows up to max_rows
            raw_rows = result_proxy.fetchmany(self.max_rows) if result_proxy.returns_rows else []

            # Convert to serializable row dictionaries
            rows: List[Dict[str, Any]] = []
            for r in raw_rows:
                row_dict = {}
                for idx, col in enumerate(columns):
                    val = r[idx]
                    # Format numeric and date objects cleanly
                    if hasattr(val, "isoformat"):
                        val = val.isoformat()
                    elif isinstance(val, (int, float)):
                        val = float(val) if isinstance(val, float) else int(val)
                    row_dict[col] = val
                rows.append(row_dict)

            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

            return {
                "success": True,
                "rows": rows,
                "columns": columns,
                "row_count": len(rows),
                "execution_time_ms": elapsed_ms,
                "truncated": len(raw_rows) >= self.max_rows,
                "error_type": None,
                "message": None,
            }

        except Exception as exc:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            err_msg = str(exc)
            
            # Map exception types
            error_type = "SQL_EXECUTION_ERROR"
            if "timeout" in err_msg.lower():
                error_type = "QUERY_TIMEOUT"
            elif "syntax" in err_msg.lower():
                error_type = "SYNTAX_ERROR"
            elif "no such table" in err_msg.lower() or "relation" in err_msg.lower():
                error_type = "TABLE_NOT_FOUND"
            elif "no such column" in err_msg.lower() or "column" in err_msg.lower():
                error_type = "COLUMN_NOT_FOUND"

            return {
                "success": False,
                "rows": [],
                "columns": [],
                "row_count": 0,
                "execution_time_ms": elapsed_ms,
                "truncated": False,
                "error_type": error_type,
                "message": err_msg,
            }
