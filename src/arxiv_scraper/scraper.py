"""Scraping abstractions and arXiv HTML implementation."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

from .models import Article


class Scraper(ABC):
    """Strategy interface for a web data source."""

    @abstractmethod
    def scrape(self) -> list[Article]:
        """Collect and return validated domain objects."""
        raise NotImplementedError


class ArxivScraper(Scraper):
    """Scrape recent Computation and Language submissions from arXiv."""

    def __init__(
        self,
        source_url: str,
        timeout_seconds: float,
        user_agent: str,
        max_pages: int = 1,
    ) -> None:
        self.source_url = source_url
        self.max_pages = max_pages
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})
        self.timeout_seconds = timeout_seconds

    def scrape(self) -> list[Article]:
        """Scrape configured pages from the source and return article metadata."""
        articles: list[Article] = []
        current_url = self.source_url

        for _ in range(self.max_pages):
            html = self._get(current_url)
            page_articles = self._parse_page(html)
            articles.extend(page_articles)

            next_url = self._get_next_page(html, current_url)
            if not next_url:
                break
            current_url = next_url

        return articles

    def _get(self, url: str) -> str:
        response = self.session.get(url, timeout=self.timeout_seconds)
        response.raise_for_status()
        return response.text

    def _parse_page(self, html: str) -> list[Article]:
        soup = BeautifulSoup(html, "html.parser")
        entries = soup.select("li.arxiv-result")
        scraped_at = datetime.now(UTC)
        return [
            self._parse_entry(entry, scraped_at)
            for entry in entries
        ]

    def _parse_entry(self, entry: Tag, scraped_at: datetime) -> Article:
        title = self._clean_text(entry.select_one("p.title"))
        authors = [self._clean_text(author) for author in entry.select("p.authors a")]
        comments = self._extract_labeled_text(entry, "Comments")
        subjects = self._extract_subjects(entry)

        abs_link = entry.select_one("p.list-title a")
        if not isinstance(abs_link, Tag) or not abs_link.get("href"):
            raise ValueError("arXiv entry without abstract link")

        abstract_url = urljoin("https://arxiv.org", abs_link["href"])
        match = re.search(r"arxiv\.org/abs/([^/?#]+)", abstract_url)
        if not match:
            raise ValueError(f"Could not extract arXiv id from URL: {abstract_url}")

        arxiv_id = match.group(1)
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}"
        html_url = f"https://arxiv.org/html/{arxiv_id}"

        return Article(
            arxiv_id=arxiv_id,
            title=title,
            authors=authors,
            comments=comments,
            subjects=subjects,
            pdf_url=pdf_url,
            html_url=html_url,
            source_url=self.source_url,
            scraped_at=scraped_at,
        )

    @staticmethod
    def _clean_text(node: Any) -> str:
        if not isinstance(node, Tag):
            return ""
        return " ".join(node.get_text(" ", strip=True).split())

    def _extract_labeled_text(self, entry: Tag, label: str) -> str | None:
        prefix = f"{label}:"
        for paragraph in entry.select("p.comments, div.meta, p"):
            text = self._clean_text(paragraph)
            if text.startswith(prefix):
                value = text[len(prefix) :].strip()
                return value or None
        return None

    def _extract_subjects(self, entry: Tag) -> str:
        subject_block = entry.select_one("div.tags")
        if not isinstance(subject_block, Tag):
            return "Unknown"
        tags = [self._clean_text(tag) for tag in subject_block.select("span.tag")]
        return "; ".join(tag for tag in tags if tag) or "Unknown"

    def _get_next_page(self, html: str, current_url: str) -> str | None:
        soup = BeautifulSoup(html, "html.parser")
        link = soup.select_one("a[title='Next page']")
        if not isinstance(link, Tag) or not link.get("href"):
            return None
        return urljoin(current_url, link["href"])
