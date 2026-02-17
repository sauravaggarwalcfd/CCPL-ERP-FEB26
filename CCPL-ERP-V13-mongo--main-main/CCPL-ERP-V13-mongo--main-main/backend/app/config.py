from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Inventory ERP"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "inventory_erp"

    # JWT - Use environment variable in production!
    SECRET_KEY: str = "your-super-secret-key-min-32-characters-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # 15 minutes for better security
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Security
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]
    CORS_ALLOW_CREDENTIALS: bool = True
    
    # Password requirements
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_NUMBERS: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True
    
    # Login security
    MAX_LOGIN_ATTEMPTS: int = 5
    LOGIN_LOCKOUT_MINUTES: int = 30
    PASSWORD_HASH_ROUNDS: int = 12
    
    # Token security
    SECURE_COOKIES: bool = True  # HTTPS only in production
    HTTPONLY_COOKIES: bool = True
    SAMESITE_COOKIES: str = "strict"
    TOKEN_BLACKLIST_ENABLED: bool = True

    # Upload
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB

    class Config:
        env_file = ".env"


settings = Settings()

# Validate SECRET_KEY in production
if settings.ENVIRONMENT == "production" and settings.SECRET_KEY == "your-super-secret-key-min-32-characters-change-in-production":
    raise ValueError("SECRET_KEY must be changed in production environment!")
