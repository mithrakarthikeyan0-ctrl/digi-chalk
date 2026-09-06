from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GATEWAY_API_KEY: str = "local-dev-gateway-key-secret"
    BACKEND_URL: str = "http://127.0.0.1:8000"
    DATABASE_URL: str = "sqlite+aiosqlite:///./gateway.db"
    CORS_ORIGINS: list[str] = [
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ]

    class Config:
        env_file = ".env"

settings = Settings()
