from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "PhantomCrowd"
    debug: bool = False
    database_url: str = "sqlite+aiosqlite:///./data/phantomcrowd.db"

    # LLM configuration (OpenAI-compatible)
    llm_api_key: str = ""
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4o-mini"
    llm_analysis_model: str = "gpt-4o"
    controversy_model: str = ""  # Separate model for controversy detection (uses Ollama native API)

    # Simulation defaults
    default_audience_size: int = 50
    max_audience_size: int = 500
    batch_size: int = 10

    model_config = {"env_file": ".env", "env_prefix": "PC_"}


settings = Settings()
