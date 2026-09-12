from pathlib import Path

from arxiv_scraper.scraper import ArxivScraper


FIXTURE = Path(__file__).parent / "fixtures" / "cscl_recent.html"


def test_parse_page_extracts_article_metadata() -> None:
    scraper = ArxivScraper(
        source_url="https://arxiv.org/list/cs.CL/recent",
        timeout_seconds=10,
        user_agent="test-agent",
    )

    articles = scraper._parse_page(FIXTURE.read_text(encoding="utf-8"))

    assert len(articles) == 1
    article = articles[0]
    assert article.arxiv_id == "2609.11913"
    assert article.title == (
        "Distance generalization in transformers: why bother with positional encoding?"
    )
    assert article.authors == ["Daniel Henrik Nevermann", "Claudius Gros"]
    assert article.comments == "15 pages, 7 figures"
    assert article.subjects == "Computation and Language (cs.CL)"
    assert str(article.pdf_url) == "https://arxiv.org/pdf/2609.11913"
