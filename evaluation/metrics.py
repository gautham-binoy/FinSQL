from typing import Dict, Any, List


class FailureCategories:
    SCHEMA_RETRIEVAL_FAILURE = "SCHEMA_RETRIEVAL_FAILURE"
    SQL_GENERATION_FAILURE = "SQL_GENERATION_FAILURE"
    SQL_VALIDATION_FAILURE = "SQL_VALIDATION_FAILURE"
    SQL_EXECUTION_FAILURE = "SQL_EXECUTION_FAILURE"
    FINANCIAL_INTERPRETATION_FAILURE = "FINANCIAL_INTERPRETATION_FAILURE"
    RESULT_VERIFICATION_FAILURE = "RESULT_VERIFICATION_FAILURE"
    ANSWER_GENERATION_FAILURE = "ANSWER_GENERATION_FAILURE"


class EvaluationMetrics:
    """
    Computes rigorous evaluation statistics across benchmark runs.
    """

    @classmethod
    def calculate(cls, benchmark_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        total = len(benchmark_results)
        if total == 0:
            return {}

        sql_exec_success = 0
        result_accurate = 0
        schema_retrieval_success = 0
        financial_correctness_success = 0
        error_recovery_opportunities = 0
        error_recovery_successes = 0

        latencies = []
        retry_counts = []
        category_stats: Dict[str, Dict[str, int]] = {}
        failure_breakdown: Dict[str, int] = {
            FailureCategories.SCHEMA_RETRIEVAL_FAILURE: 0,
            FailureCategories.SQL_GENERATION_FAILURE: 0,
            FailureCategories.SQL_VALIDATION_FAILURE: 0,
            FailureCategories.SQL_EXECUTION_FAILURE: 0,
            FailureCategories.FINANCIAL_INTERPRETATION_FAILURE: 0,
            FailureCategories.RESULT_VERIFICATION_FAILURE: 0,
            FailureCategories.ANSWER_GENERATION_FAILURE: 0,
        }

        for item in benchmark_results:
            cat = item.get("category", "other")
            if cat not in category_stats:
                category_stats[cat] = {"total": 0, "sql_success": 0, "result_accurate": 0}
            category_stats[cat]["total"] += 1

            # 1. SQL Execution
            exec_ok = item.get("execution_success", False)
            if exec_ok:
                sql_exec_success += 1
                category_stats[cat]["sql_success"] += 1
            else:
                failure_breakdown[FailureCategories.SQL_EXECUTION_FAILURE] += 1

            # 2. Result accuracy
            res_ok = item.get("result_accurate", False)
            if res_ok:
                result_accurate += 1
                category_stats[cat]["result_accurate"] += 1

            # 3. Schema retrieval accuracy
            schema_ok = item.get("schema_retrieval_success", True)
            if schema_ok:
                schema_retrieval_success += 1
            else:
                failure_breakdown[FailureCategories.SCHEMA_RETRIEVAL_FAILURE] += 1

            # 4. Financial correctness
            fin_ok = item.get("financial_correctness", False)
            if fin_ok:
                financial_correctness_success += 1
            elif exec_ok and not fin_ok:
                failure_breakdown[FailureCategories.FINANCIAL_INTERPRETATION_FAILURE] += 1

            # 5. Error recovery
            if item.get("required_recovery", False):
                error_recovery_opportunities += 1
                if item.get("recovery_succeeded", False):
                    error_recovery_successes += 1

            latencies.append(item.get("latency_ms", 0))
            retry_counts.append(item.get("retry_count", 0))

        avg_latency = round(sum(latencies) / total, 2) if latencies else 0
        avg_retries = round(sum(retry_counts) / total, 2) if retry_counts else 0
        recovery_rate = round((error_recovery_successes / error_recovery_opportunities * 100), 2) if error_recovery_opportunities > 0 else 100.0

        return {
            "total_questions": total,
            "sql_execution_accuracy": round((sql_exec_success / total) * 100, 2),
            "result_accuracy": round((result_accurate / total) * 100, 2),
            "schema_retrieval_accuracy": round((schema_retrieval_success / total) * 100, 2),
            "financial_correctness": round((financial_correctness_success / total) * 100, 2),
            "error_recovery_rate": recovery_rate,
            "error_recovery_events": {
                "opportunities": error_recovery_opportunities,
                "succeeded": error_recovery_successes
            },
            "average_latency_ms": avg_latency,
            "average_retry_count": avg_retries,
            "failure_taxonomy": failure_breakdown,
            "category_performance": category_stats
        }
