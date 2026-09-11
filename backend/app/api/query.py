from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.app.database.connection import get_db
from backend.app.agents.orchestrator import FinSQLOrchestrator
from backend.app.agents.baseline import BaselineAgent

router = APIRouter(prefix="/api/query", tags=["Query"])


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=500, description="Natural language financial question")
    mode: Optional[str] = Field("agent", description="'agent' for FinSQL Agent, 'baseline' for Baseline Text-to-SQL")


class QueryResponse(BaseModel):
    request_id: str
    question: str
    mode: str
    sql: str
    answer: str
    latency_ms: float
    analysis: Optional[Dict[str, Any]] = None
    retrieved_schema: Optional[List[Dict[str, Any]]] = None
    validation: Optional[Dict[str, Any]] = None
    execution: Optional[Dict[str, Any]] = None
    verification: Optional[Dict[str, Any]] = None
    detailed_analysis: Optional[str] = None
    key_metrics: Optional[List[Dict[str, Any]]] = None
    chart: Optional[Dict[str, Any]] = None
    provenance: Optional[Dict[str, Any]] = None
    attempts: Optional[List[Dict[str, Any]]] = None
    retry_count: Optional[int] = 0
    trace: Optional[List[Dict[str, Any]]] = None
    model: Optional[str] = None


@router.post("", response_model=QueryResponse)
def execute_query(payload: QueryRequest, db: Session = Depends(get_db)):
    """
    Executes a natural language financial query using either FinSQL Agent (default)
    or Baseline Text-to-SQL mode.
    """
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    if payload.mode == "baseline":
        agent = BaselineAgent(db)
        result = agent.run(payload.question)
    else:
        orchestrator = FinSQLOrchestrator(db)
        result = orchestrator.run(payload.question)

    return result


@router.post("/baseline", response_model=QueryResponse)
def execute_baseline(payload: QueryRequest, db: Session = Depends(get_db)):
    """
    Dedicated endpoint for Baseline Text-to-SQL execution.
    """
    agent = BaselineAgent(db)
    return agent.run(payload.question)
