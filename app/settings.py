from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    openai_api_key: str
    openai_model: str = "gpt-5.2"

    # Safety constraints
    max_rows: int = 200
    statement_timeout_ms: int = 8000

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
