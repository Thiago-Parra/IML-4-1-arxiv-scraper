"""Command-line entry point."""

import argparse
import logging

from .config import Settings
from .repository import CsvArticleRepository
from .scraper import ArxivScraper
from .service import ScrapingService

logger = logging.getLogger(__name__)


def configure_logging() -> None:
    """Configure a compact application log format."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")


def main() -> None:
    """Run the scraping application."""
    parser = argparse.ArgumentParser(description="Scrape recent arXiv cs.CL submissions.")
    parser.parse_args()
    configure_logging()
    settings = Settings()

    scraper = ArxivScraper(
        source_url=settings.source_url,
        timeout_seconds=settings.timeout_seconds,
        user_agent=settings.user_agent,
        max_pages=settings.max_pages,
    )
    repository = CsvArticleRepository(settings.output_file)
    service = ScrapingService(scraper, repository)

    articles = service.execute()
    logger.info("Collected %d articles and saved to %s", len(articles), settings.output_file)


if __name__ == "__main__":
    main()
