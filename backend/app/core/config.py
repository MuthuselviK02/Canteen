from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:////data/canteen.db"

    # JWT
    SECRET_KEY: str = "dev-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # CORS
    ALLOWED_ORIGINS: str = "*"

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60

    # API
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Smart Canteen Management System"

    # Image Base URL (you added this earlier fix — keep it)
    IMAGE_BASE_URL: str = "http://localhost:8000"

    def get_cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    class Config:
        env_file = ".env"
        extra = "ignore"  # 🔥 THIS prevents crashes from unknown env vars


settings = Settings()