"""Scraping abstractions and arXiv HTML implementation."""

from __future__ import annotations

import logging
import re
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

from .models import Article

logger = logging.getLogger(__name__)


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

        pages_processed = 0

        for page_number in range(1, self.max_pages + 1):
            current_url = self._build_page_url(page_number)

            logger.info(
                "Scraping page %d/%d: %s",
                page_number,
                self.max_pages,
                current_url,
            )

            html = self._get(current_url)
            page_articles = self._parse_page(html)

            logger.info(
                "Page %d/%d: collected %d articles",
                page_number,
                self.max_pages,
                len(page_articles),
            )

            if not page_articles:
                logger.warning(
                    "Page %d/%d returned no articles. Stopping pagination.",
                    page_number,
                    self.max_pages,
                )
                break

            articles.extend(page_articles)
            pages_processed = page_number

        logger.info(
            "Scraping finished: %d pages processed, %d articles collected",
            pages_processed,
            len(articles),
        )

        return articles

    def _get(self, url: str) -> str:
        response = self.session.get(url, timeout=self.timeout_seconds)
        response.raise_for_status()
        return response.text

    def _parse_page(self, html: str) -> list[Article]:
        """Parse the current arXiv list-page structure."""
        soup = BeautifulSoup(html, "html.parser")
        entries = soup.select("dl > dt")
        scraped_at = datetime.now(UTC)

        articles: list[Article] = []

        for dt in entries:
            dd = dt.find_next_sibling("dd")

            if not isinstance(dd, Tag):
                continue

            try:
                articles.append(self._parse_entry(dt, dd, scraped_at))
            except ValueError:
                # Ignore malformed entries while allowing the page
                # to continue processing the remaining submissions.
                continue

        return articles

    def _parse_entry(
        self,
        dt: Tag,
        dd: Tag,
        scraped_at: datetime,
    ) -> Article:
        """Parse one arXiv submission from its dt/dd pair."""
        title = self._clean_text(dd.select_one("div.list-title")).removeprefix("Title:").strip()

        authors = [self._clean_text(author) for author in dd.select("div.list-authors a")]

        comments_node = dd.select_one("div.list-comments")
        subjects_node = dd.select_one("div.list-subjects")

        comments = self._clean_text(comments_node) if isinstance(comments_node, Tag) else None
        if comments:
            comments = comments.removeprefix("Comments:").strip() or None

        subjects = self._clean_text(subjects_node) if isinstance(subjects_node, Tag) else "Unknown"
        subjects = subjects.removeprefix("Subjects:").strip() or "Unknown"

        if not title:
            raise ValueError("arXiv entry without a title")

        abs_link = dt.select_one('a[href*="/abs/"]')

        if not isinstance(abs_link, Tag):
            raise ValueError("arXiv entry without abstract link")

        href = abs_link.get("href")
        if not isinstance(href, str) or not href:
            raise ValueError("arXiv entry with invalid abstract link")

        abstract_url = urljoin(
            "https://arxiv.org",
            href,
        )

        match = re.search(
            r"arxiv\.org/abs/([^/?#]+)",
            abstract_url,
        )

        if not match:
            raise ValueError(f"Could not extract arXiv id from URL: {abstract_url}")

        arxiv_id = match.group(1)

        return Article(
            arxiv_id=arxiv_id,
            title=title,
            authors=authors,
            comments=comments,
            subjects=subjects,
            pdf_url=f"https://arxiv.org/pdf/{arxiv_id}",
            html_url=f"https://arxiv.org/html/{arxiv_id}",
            source_url=self.source_url,
            scraped_at=scraped_at,
        )

    def _clean_text(self, node: Any) -> str:
        if not isinstance(node, Tag):
            return ""
        return " ".join(node.get_text(" ", strip=True).split())

    def _build_page_url(self, page_number: int) -> str:
        """Build an arXiv list URL for a one-based page number."""
        if page_number < 1:
            raise ValueError("page_number must be greater than or equal to 1")

        skip = (page_number - 1) * 50
        separator = "&" if "?" in self.source_url else "?"
        return f"{self.source_url}{separator}skip={skip}&show=50"

    def _get_next_page(self, html: str, current_url: str) -> str | None:
        soup = BeautifulSoup(html, "html.parser")
        link = soup.select_one("a[title='Next page']")
        if not isinstance(link, Tag) or not link.get("href"):
            return None
        return urljoin(current_url, link["href"])
