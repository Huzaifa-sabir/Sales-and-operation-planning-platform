from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    APP_NAME: str = "S&OP Portal API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    MONGODB_URL: str = "mongodb+srv://huzaifasabir289_db_user:4SLjzoPzm00pQNNv@cluster0.4owv6bf.mongodb.net/sop_portal?retryWrites=true&w=majority"
    MONGODB_DB_NAME: str = "sop_portal"

    # JWT
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production-12345"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # Security
    PASSWORD_MIN_LENGTH: int = 8
    MAX_LOGIN_ATTEMPTS: int = 5
    SESSION_TIMEOUT_MINUTES: int = 480

    # CORS - Production defaults include Netlify URL
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:5174,http://localhost:3000,https://soptest.netlify.app"

    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@heavygarlic.com"
    SMTP_FROM_NAME: str = "Heavy Garlic S&OP Portal"
    EMAIL_ENABLED: bool = False

    # File Upload
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 10

    # S&OP
    DEFAULT_FORECAST_MONTHS: int = 16
    MANDATORY_FORECAST_MONTHS: int = 12
    CYCLE_REMINDER_DAYS: int = 5

    # Admin User (Initial)
    ADMIN_USERNAME: str = "lpolo"
    ADMIN_EMAIL: str = "lpolo@garlandfood.net"
    ADMIN_PASSWORD: str = "admin123"
    ADMIN_FULL_NAME: str = "L Polo"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        origins = [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
        # Ensure localhost:5173 and localhost:5174 are always included for development
        if "http://localhost:5173" not in origins:
            origins.append("http://localhost:5173")
        if "http://localhost:5174" not in origins:
            origins.append("http://localhost:5174")
        return origins


# Create global settings instance
settings = Settings()
