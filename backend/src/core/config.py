import os
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    # Database settings
    database_url: Optional[str] = Field(default=None, alias="DATABASE_URL")

    # Qdrant settings
    qdrant_url: Optional[str] = Field(default=None, alias="QDRANT_URL")
    qdrant_api_key: Optional[str] = Field(default=None, alias="QDRANT_API_KEY")

    # API Keys
    gemini_api_key: Optional[str] = Field(default=None, alias="GEMINI_API_KEY")
    groq_api_key: Optional[str] = Field(default=None, alias="GROQ_API_KEY")
    cohere_api_key: Optional[str] = Field(default=None, alias="COHERE_API_KEY")

    # Model settings
    embedding_model: str = Field(default="embed-english-v3.0", alias="EMBEDDING_MODEL")
    llm_model: str = Field(default="gemini/gemini-2.0-flash", alias="LLM_MODEL")

    # RAG settings
    retrieval_limit: int = 5
    similarity_threshold: float = 0.5

    class Config:
        env_file = ".env"
        populate_by_name = True
        extra = "ignore"

settings = Settings()