from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "PhantomCrowd"
    debug: bool = False
    anthropic_api_key: str = ""
    database_url: str = "sqlite+aiosqlite:///./data/phantomcrowd.db"

    # Model configuration
    persona_model: str = "claude-haiku-4-5-20251001"
    analysis_model: str = "claude-sonnet-4-5-20241022"

    # Simulation defaults
    default_audience_size: int = 50
    max_audience_size: int = 500
    batch_size: int = 10

    model_config = {"env_file": ".env", "env_prefix": "PC_"}


settings = Settings()
