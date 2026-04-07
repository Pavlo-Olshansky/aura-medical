from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg_async://postgres:postgres@localhost:5432/medtracker"
    SECRET_KEY: str
    DOCUMENTS_DIR: str = "../documents"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]
    RATE_LIMIT: str = "10/minute"
    LOG_LEVEL: str = "DEBUG"
    SKYPULSE_API_KEY: str = ""
    WEATHER_CITY: str = "Kyiv"
    VAPID_MAILTO: str = "mailto:noreply@example.com"
    TEST_MODE: bool = False

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
