from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.database.connection import get_db
from backend.app.database.models import Company, FinancialFact, FinancialConcept, SchemaCatalog
from backend.app.config import settings

router = APIRouter(prefix="/api/health", tags=["Health"])


@router.get("")
def get_health(db: Session = Depends(get_db)):
    """
    Returns system health, database statistics, and Gemini AI configuration status.
    """
    db_status = "connected"
    companies_count = 0
    facts_count = 0
    concepts_count = 0
    embeddings_count = 0

    try:
        companies_count = db.query(Company).count()
        facts_count = db.query(FinancialFact).count()
        concepts_count = db.query(FinancialConcept).count()
        embeddings_count = db.query(SchemaCatalog).count()
    except Exception as e:
        db_status = f"error: {str(e)}"

    gemini_ready = bool(settings.GEMINI_API_KEY and not settings.DEMO_MODE)

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": {
            "status": db_status,
            "url_type": "postgresql" if settings.DATABASE_URL.startswith("postgresql") else "sqlite",
            "companies_count": companies_count,
            "financial_facts_count": facts_count,
            "financial_concepts_count": concepts_count,
            "schema_embeddings_count": embeddings_count,
        },
        "ai": {
            "gemini_configured": gemini_ready,
            "demo_mode": settings.DEMO_MODE,
            "model_name": settings.MODEL_NAME,
            "embedding_model": settings.EMBEDDING_MODEL,
        },
        "version": "1.0.0",
        "service": "FinSQL Agent Backend"
    }
