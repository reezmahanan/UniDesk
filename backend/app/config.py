from pydantic_settings import BaseSettings
from typing import Optional, List
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "UniDesk — AI University Help Desk & Ticketing Platform"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = "apex-university-super-secret-jwt-key-2026-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./apex_dev.db")
    
    # AI Generation & Embeddings
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", None)
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "gemini")  # 'gemini' or 'local_tfidf'
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-004")
    EMBEDDING_DIMENSION: int = 768
    MOCK_AI_MODE: bool = os.getenv("MOCK_AI_MODE", "true").lower() in ("true", "1", "yes")
    
    # File Uploads
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./storage/uploads")
    DOCUMENTS_DIR: str = os.getenv("DOCUMENTS_DIR", "./storage/documents")
    MAX_FILE_SIZE_BYTES: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg"]
    
    # Rate Limiting
    LOGIN_RATE_LIMIT_PER_MINUTE: int = 10
    CHAT_RATE_LIMIT_PER_MINUTE: int = 20
    
    # Cookie & Security
    COOKIE_NAME: str = "apex_access_token"
    CSRF_COOKIE_NAME: str = "apex_csrf_token"
    COOKIE_SECURE: bool = False  # Set to True in HTTPS production
    COOKIE_SAMESITE: str = "lax"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
