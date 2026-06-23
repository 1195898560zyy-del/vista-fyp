from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    port: int = 3000
    public_base_url: str = "http://localhost:3000"

    openai_api_key: str = ""
    openai_key: str = ""
    openai_chat_model: str = "gpt-4o-mini"

    unsplash_key: str = ""
    pexels_key: str = ""
    pixabay_key: str = ""

    weather_api_key: str = ""

    replicate_api_token: str = ""
    replicate_api_key: str = ""

    @property
    def openai_key_resolved(self) -> str:
        return self.openai_api_key or self.openai_key

    @property
    def replicate_token_resolved(self) -> str:
        return self.replicate_api_token or self.replicate_api_key

    @property
    def frontend_dir(self) -> Path:
        return Path(__file__).resolve().parent.parent.parent / "vistapj"


@lru_cache
def get_settings() -> Settings:
    return Settings()
