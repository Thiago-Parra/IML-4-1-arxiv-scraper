"""Domain models for scraped arXiv articles."""

from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class Article(BaseModel):
    """Validated metadata for an arXiv article."""

    arxiv_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    authors: list[str] = Field(default_factory=list)
    comments: str | None = None
    subjects: str = Field(min_length=1)
    pdf_url: HttpUrl
    html_url: HttpUrl | None = None
    source_url: HttpUrl
    scraped_at: datetime
