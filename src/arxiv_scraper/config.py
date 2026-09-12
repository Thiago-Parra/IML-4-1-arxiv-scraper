"""Application configuration."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    source_url: str = Field(default="https://arxiv.org/list/cs.CL/recent")
    output_file: Path = Field(default=Path("data/articles.csv"))
    max_pages: int = Field(default=1, ge=1, le=20)
    timeout_seconds: float = Field(default=20.0, gt=0)
    user_agent: str = Field(default="IML4.1-Arxiv-Scraper/1.0")
