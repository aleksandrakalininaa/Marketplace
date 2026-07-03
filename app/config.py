from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Marketplace"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    DATABASE_URL: str = "postgresql+asyncpg://marketplace:marketplace@localhost:5432/marketplace"

    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    VK_APP_ID: str = ""
    VK_SECRET: str = ""
    VK_REDIRECT_URI: str = "http://localhost:3000/auth/vk-callback"

    FRONTEND_URL: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()