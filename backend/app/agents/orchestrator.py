import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.app.config import settings
from backend.app.retrieval.schema_retriever import SchemaRetriever
from backend.app.agents.question_analyzer import QuestionAnalyzer
from backend.app.agents.sql_generator import SQLGenerator
from backend.app.agents.sql_repair import SQLRepairAgent
from backend.app.agents.answer_generator import AnswerGenerator
from backend.app.validation.sql_validator import SQLValidator
from backend.app.validation.result_verifier import ResultVerifier
from backend.app.database.executor import SQLExecutor


class FinSQLOrchestrator:
    """
    Master pipeline orchestrator for the FinSQL Agent:
    Question -> Analysis -> Schema Retrieval -> SQL Generation -> AST Validation
    -> Execution -> Repair Loop (if error or anomaly) -> Result Verification -> Grounded Answer.
    """

    def __init__(self, db_session: Session):
        self.db = db_session
        self.retriever = SchemaRetriever(db_session)
        self.analyzer = QuestionAnalyzer(db_session)
        self.executor = SQLExecutor(db_session)

    def run(self, question: str, initial_sql_override: Optional[str] = None) -> Dict[str, Any]:
        request_id = str(uuid.uuid4())
        overall_start = time.perf_counter()
        timestamp = datetime.now(timezone.utc).isoformat()

        trace_steps: List[Dict[str, Any]] = []
        attempts: List[Dict[str, Any]] = []

        # =========================================================================
        # Stage 1: Question Analysis
        # =========================================================================
        s1_start = time.perf_counter()
        analysis = self.analyzer.analyze(question)
        s1_latency = round((time.perf_counter() - s1_start) * 1000, 2)
        trace_steps.append({
            "step": "question_analysis",
            "title": "Question Analyzed",
            "status": "completed",
            "latency_ms": s1_latency,
            "details": {
                "entities": analysis.get("entities", []),
                "tickers": analysis.get("tickers", []),
                "metrics": analysis.get("metrics", []),
                "time_period": analysis.get("time_period", {}),
                "operation": analysis.get("operation", "lookup"),
            }
        })

        # =========================================================================
        # Stage 2: Relevant Schema Retrieval (pgvector / semantic hybrid)
        # =========================================================================
        s2_start = time.perf_counter()
        retrieved_schema = self.retriever.retrieve(
            question=question,
            detected_entities=analysis.get("entities", []),
            detected_metrics=analysis.get("metrics", []),
            top_k=10
        )
        s2_latency = round((time.perf_counter() - s2_start) * 1000, 2)
        trace_steps.append({
            "step": "schema_retrieval",
            "title": "Relevant Schema Retrieved",
            "status": "completed",
            "latency_ms": s2_latency,
            "details": {
                "relevant_tables": retrieved_schema.get("relevant_tables", []),
                "relevant_concepts": retrieved_schema.get("relevant_concepts", []),
                "item_count": len(retrieved_schema.get("retrieved_items", [])),
                "top_items": [it["display_name"] for it in retrieved_schema.get("retrieved_items", [])[:5]]
            }
        })

        # =========================================================================
        # Stage 3: SQL Generation & AST Validation & Safe Execution with Repair Loop
        # =========================================================================
        s3_start = time.perf_counter()
        if initial_sql_override:
            current_sql = initial_sql_override
            explanation = "Initial candidate SQL (testing error recovery loop)."
            assumptions = ["Candidate query for repair testing"]
        else:
            current_sql_data = SQLGenerator.generate(question, analysis, retrieved_schema)
            current_sql = current_sql_data.get("sql", "").strip()
            explanation = current_sql_data.get("explanation", "")
            assumptions = current_sql_data.get("assumptions", [])

        max_retries = settings.MAX_SQL_RETRIES
        attempt_count = 0
        execution_result: Dict[str, Any] = {}
        validation_result: Dict[str, Any] = {}
        verification_result: Dict[str, Any] = {}

        while attempt_count <= max_retries:
            attempt_count += 1
            attempt_log: Dict[str, Any] = {
                "attempt": attempt_count,
                "sql": current_sql,
                "validation": None,
                "execution": None,
                "repaired": attempt_count > 1,
            }

            # 3A. SQLGlot AST Validation
            validation_result = SQLValidator.validate(current_sql)
            attempt_log["validation"] = validation_result

            if not validation_result.get("valid"):
                err_msg = f"Validation failed: {validation_result.get('reason')}"
                attempt_log["error"] = err_msg
                attempts.append(attempt_log)

                if attempt_count <= max_retries:
                    # Repair SQL
                    repaired = SQLRepairAgent.repair(
                        question=question,
                        previous_sql=current_sql,
                        error_message=err_msg,
                        retrieved_schema=retrieved_schema,
                        attempt_number=attempt_count
                    )
                    current_sql = repaired.get("sql", current_sql)
                    continue
                else:
                    break

            # 3B. Execution
            execution_result = self.executor.execute_query(current_sql)
            attempt_log["execution"] = {
                "success": execution_result.get("success"),
                "row_count": execution_result.get("row_count"),
                "execution_time_ms": execution_result.get("execution_time_ms"),
                "error_type": execution_result.get("error_type"),
            }

            if not execution_result.get("success"):
                err_msg = f"Database execution error: {execution_result.get('message')}"
                attempt_log["error"] = err_msg
                attempts.append(attempt_log)

                if attempt_count <= max_retries:
                    # Repair SQL
                    repaired = SQLRepairAgent.repair(
                        question=question,
                        previous_sql=current_sql,
                        error_message=err_msg,
                        retrieved_schema=retrieved_schema,
                        attempt_number=attempt_count
                    )
                    current_sql = repaired.get("sql", current_sql)
                    continue
                else:
                    break

            # 3C. Result Verification (Financial checks)
            verification_result = ResultVerifier.verify(
                rows=execution_result.get("rows", []),
                columns=execution_result.get("columns", []),
                question_analysis=analysis
            )
            attempt_log["verification"] = verification_result

            if verification_result.get("needs_repair") and attempt_count <= max_retries:
                # E.g. empty results or restatement conflict that can be repaired
                repair_msg = verification_result.get("repair_reason", "Result anomaly detected.")
                attempt_log["error"] = repair_msg
                attempts.append(attempt_log)

                repaired = SQLRepairAgent.repair(
                    question=question,
                    previous_sql=current_sql,
                    error_message=repair_msg,
                    retrieved_schema=retrieved_schema,
                    attempt_number=attempt_count
                )
                current_sql = repaired.get("sql", current_sql)
                continue

            # Query succeeded and passed verification or has warnings
            attempts.append(attempt_log)
            break

        s3_latency = round((time.perf_counter() - s3_start) * 1000, 2)

        trace_steps.append({
            "step": "sql_generation",
            "title": "SQL Generated & Validated",
            "status": "completed" if validation_result.get("valid") else "failed",
            "latency_ms": s3_latency,
            "details": {
                "sql": current_sql,
                "tables_accessed": validation_result.get("ast_tables", []),
                "is_read_only": validation_result.get("valid", False),
                "retries": attempt_count - 1,
            }
        })

        trace_steps.append({
            "step": "sql_execution",
            "title": "Query Executed & Verified",
            "status": "completed" if execution_result.get("success") else "failed",
            "latency_ms": execution_result.get("execution_time_ms", 0),
            "details": {
                "row_count": execution_result.get("row_count", 0),
                "verification_checks": verification_result.get("checks", {}),
                "warnings": verification_result.get("warnings", []),
            }
        })

        # =========================================================================
        # Stage 4: Grounded Answer Generation
        # =========================================================================
        s4_start = time.perf_counter()
        answer_data = AnswerGenerator.generate(
            question=question,
            sql=current_sql,
            execution_result=execution_result,
            verification_result=verification_result,
            assumptions=assumptions
        )
        s4_latency = round((time.perf_counter() - s4_start) * 1000, 2)

        trace_steps.append({
            "step": "answer_generation",
            "title": "Answer Generated",
            "status": "completed",
            "latency_ms": s4_latency,
            "details": {
                "chart_type": answer_data.get("chart_recommendation", {}).get("type", "none"),
                "provenance_source": answer_data.get("provenance", {}).get("data_source", "Database"),
            }
        })

        total_latency_ms = round((time.perf_counter() - overall_start) * 1000, 2)

        return {
            "request_id": request_id,
            "timestamp": timestamp,
            "question": question,
            "analysis": analysis,
            "retrieved_schema": retrieved_schema.get("retrieved_items", []),
            "sql": current_sql,
            "sql_explanation": explanation,
            "assumptions": assumptions,
            "validation": validation_result,
            "execution": execution_result,
            "verification": verification_result,
            "answer": answer_data.get("summary", ""),
            "detailed_analysis": answer_data.get("detailed_analysis", ""),
            "key_metrics": answer_data.get("key_metrics", []),
            "chart": answer_data.get("chart_recommendation", {}),
            "provenance": answer_data.get("provenance", {}),
            "attempts": attempts,
            "retry_count": max(0, len(attempts) - 1),
            "trace": trace_steps,
            "latency_ms": total_latency_ms,
            "mode": "FinSQL Agent",
            "model": settings.MODEL_NAME if settings.GEMINI_API_KEY and not settings.DEMO_MODE else "Deterministic Demo Mode",
        }
