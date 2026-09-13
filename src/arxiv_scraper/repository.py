"""Persistence abstractions for collected articles."""

from __future__ import annotations

import csv
from abc import ABC, abstractmethod
from pathlib import Path

from .models import Article


class ArticleRepository(ABC):
    """Repository interface for article persistence."""

    @abstractmethod
    def save_all(self, articles: list[Article]) -> None:
        """Persist a collection of articles."""
        raise NotImplementedError


class CsvArticleRepository(ArticleRepository):
    """Persist articles as a UTF-8 CSV file."""

    FIELDNAMES = [
        "arxiv_id",
        "title",
        "authors",
        "comments",
        "subjects",
        "pdf_url",
        "html_url",
        "source_url",
        "scraped_at",
    ]

    def __init__(self, output_file: Path) -> None:
        self.output_file = output_file

    def save_all(self, articles: list[Article]) -> None:
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

        with self.output_file.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=self.FIELDNAMES,
                delimiter="|",
                quoting=csv.QUOTE_MINIMAL,
            )
            writer.writeheader()
            for article in articles:
                row = article.model_dump(mode="json")
                row["authors"] = "; ".join(article.authors)
                writer.writerow(row)
