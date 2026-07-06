from typing import List, Literal
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/compliance_db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Cloudflare R2 / S3
    R2_ACCOUNT_ID: str = ""
    R2_ACCESS_KEY_ID: str = ""
    R2_SECRET_ACCESS_KEY: str = ""
    R2_BUCKET_NAME: str = "multimodal-compliance"
    R2_ENDPOINT_URL: str = ""
    R2_PUBLIC_URL: str = ""

    # Gemini VLM
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # OCR
    OCR_ENGINE: Literal["auto", "tesseract", "surya"] = "auto"
    SURYA_ENABLED: bool = False

    # API security
    API_KEY: str = ""

    # Processing limits
    MAX_FILE_SIZE_MB: int = 20
    MAX_PAGES: int = 10
    VIDEO_MAX_SECONDS: int = 60
    VLM_RATE_LIMIT_SLEEP: float = 4.0

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
