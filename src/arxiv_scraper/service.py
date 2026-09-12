"""Application service for the scraping use case."""

from .models import Article
from .repository import ArticleRepository
from .scraper import Scraper


class ScrapingService:
    """Orchestrate data collection and persistence."""

    def __init__(self, scraper: Scraper, repository: ArticleRepository) -> None:
        self.scraper = scraper
        self.repository = repository

    def execute(self) -> list[Article]:
        """Collect articles and persist them through the configured repository."""
        articles = self.scraper.scrape()
        self.repository.save_all(articles)
        return articles
