import json
from pathlib import Path
from fastapi import APIRouter

router = APIRouter(prefix="/api/metrics", tags=["Metrics"])

REPORT_PATH = Path(__file__).resolve().parent.parent.parent.parent / "evaluation" / "reports" / "evaluation_report.json"


@router.get("")
def get_metrics():
    """
    Returns system evaluation metrics and comparative benchmarks between Baseline and FinSQL Agent.
    """
    if REPORT_PATH.exists():
        try:
            with open(REPORT_PATH, "r") as f:
                return json.load(f)
        except Exception as e:
            return {"error": f"Failed reading report: {e}"}

    # Return default fallback metrics if report not yet generated
    return {
        "status": "pending",
        "message": "Run python -m evaluation.evaluator to generate real-time metrics."
    }
