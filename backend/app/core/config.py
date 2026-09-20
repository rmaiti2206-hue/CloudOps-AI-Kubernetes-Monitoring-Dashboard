from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./cloudops_ai.db"

    jwt_secret: str = "development-only-change-me"

    jwt_algorithm: str = "HS256"

    access_token_expire_minutes: int = 60

    prometheus_url: str = "http://localhost:9090"

    # IMPORTANT:
    # False = use real Kubernetes cluster
    # True  = use demo/sample data
    demo_mode: bool = False

    cors_origins: list[str] = ["http://localhost:5173"]

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()