"""Load settings from environment variables / .env file."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Always load vista-backend/.env regardless of current working directory
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE) if ENV_FILE.exists() else None,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    port: int = 3000
    public_base_url: str | None = None

    unsplash_key: str = ""
    pexels_key: str = ""
    pixabay_key: str = ""

    weather_api_key: str = ""

    openai_api_key: str = ""
    openai_key: str = ""
    openai_chat_model: str = "gpt-4o-mini"

    replicate_api_token: str = ""
    replicate_api_key: str = ""

    @property
    def resolved_openai_key(self) -> str:
        return self.openai_api_key or self.openai_key

    @property
    def resolved_replicate_token(self) -> str:
        return self.replicate_api_token or self.replicate_api_key


def get_settings() -> Settings:
    return Settings()
