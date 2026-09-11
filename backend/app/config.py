import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Gemini AI Configuration
    GEMINI_API_KEY: str = Field(default="", env="GEMINI_API_KEY")
    MODEL_NAME: str = Field(default="gemini-2.5-flash", env="MODEL_NAME")
    EMBEDDING_MODEL: str = Field(default="text-embedding-004", env="EMBEDDING_MODEL")

    # Database Configuration
    DATABASE_URL: str = Field(default="sqlite:///./data/finsql.db", env="DATABASE_URL")

    # Execution & Safety Limits
    MAX_SQL_RETRIES: int = Field(default=3, env="MAX_SQL_RETRIES")
    QUERY_TIMEOUT_SECONDS: int = Field(default=10, env="QUERY_TIMEOUT_SECONDS")
    MAX_RESULT_ROWS: int = Field(default=1000, env="MAX_RESULT_ROWS")

    # Application Behavior
    DEMO_MODE: bool = Field(default=False, env="DEMO_MODE")
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "*"]

    # Evaluator configuration
    EVAL_SAMPLE_SIZE: int = Field(default=100, env="EVAL_SAMPLE_SIZE")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()

# If GEMINI_API_KEY is empty or default placeholder, enable DEMO_MODE automatically
if not settings.GEMINI_API_KEY or "your_gemini_api_key" in settings.GEMINI_API_KEY.lower():
    settings.DEMO_MODE = True
