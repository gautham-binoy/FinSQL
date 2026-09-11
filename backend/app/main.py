from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import settings
from backend.app.database.connection import init_database
from backend.app.api.query import router as query_router
from backend.app.api.health import router as health_router
from backend.app.api.schema import router as schema_router
from backend.app.api.examples import router as examples_router
from backend.app.api.metrics import router as metrics_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure database tables exist on startup
    init_database()
    yield


app = FastAPI(
    title="FinSQL Agent API",
    description="Agentic Text-to-SQL System for Financial Data featuring Schema Retrieval, AST Validation, and Grounded Financial Intelligence.",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(query_router)
app.include_router(health_router)
app.include_router(schema_router)
app.include_router(examples_router)
app.include_router(metrics_router)

# Mount frontend/dist if built (enables single-service free hosting on Render / Hugging Face)
from pathlib import Path
from fastapi.staticfiles import StaticFiles

frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
else:
    @app.get("/")
    def root():
        return {
            "name": "FinSQL Agent API",
            "description": "Agentic Text-to-SQL for Financial Data",
            "version": "1.0.0",
            "endpoints": {
                "query": "/api/query",
                "health": "/api/health",
                "schema": "/api/schema",
                "examples": "/api/examples",
                "metrics": "/api/metrics",
                "docs": "/docs"
            }
        }
