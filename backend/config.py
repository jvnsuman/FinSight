from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/finance_analytics_platform"
    SECRET_KEY: str = "change-me"
    JWT_SECRET_KEY: str = "change-me"
    ALGORITHM: str = "HS256"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES: int = 60
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 30
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""
    SMTP_FROM_NAME: str = "Finance Analytics Platform"
    BREVO_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    APP_NAME: str = "Finance Analytics Platform"
    DEBUG: bool = False
    FRONTEND_URL: str = "http://localhost:5173"
    MARKET_DATA_CACHE_TTL_MINUTES: int = 15
    FINVU_PRIVATE_KEY_PATH: str = "backend/secrets/finvu_private_key.pem"
    FINVU_PUBLIC_JWK_PATH: str = "backend/secrets/finvu_public_key.jwk.json"

settings = Settings()
