from pathlib import Path
from unittest.mock import call, patch

from arxiv_scraper.scraper import ArxivScraper

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "arxiv_recent.html"

SOURCE_URL = "https://arxiv.org/list/cs.CL/recent"


def make_scraper(max_pages: int = 1) -> ArxivScraper:
    return ArxivScraper(
        source_url=SOURCE_URL,
        timeout_seconds=10.0,
        user_agent="test-agent",
        max_pages=max_pages,
    )


def test_parse_page_extracts_articles_from_current_arxiv_structure() -> None:
    html = FIXTURE_PATH.read_text(encoding="utf-8")
    scraper = make_scraper()

    articles = scraper._parse_page(html)

    assert len(articles) == 2

    first = articles[0]

    assert first.arxiv_id == "2609.11913"
    assert first.title == "Distance generalization in transformers"
    assert first.authors == [
        "Daniel Henrik Nevermann",
        "Claudius Gros",
    ]
    assert first.comments == "15 pages, 7 figures"
    assert first.subjects == "Computation and Language (cs.CL)"
    assert str(first.pdf_url) == ("https://arxiv.org/pdf/2609.11913")
    assert str(first.html_url) == ("https://arxiv.org/html/2609.11913")


def test_parse_page_preserves_multiple_subjects() -> None:
    html = FIXTURE_PATH.read_text(encoding="utf-8")
    scraper = make_scraper()

    articles = scraper._parse_page(html)

    assert articles[1].subjects == (
        "Computation and Language (cs.CL); Artificial Intelligence (cs.AI)"
    )


def test_build_page_url() -> None:
    scraper = make_scraper()

    assert scraper._build_page_url(1) == ("https://arxiv.org/list/cs.CL/recent?skip=0&show=50")

    assert scraper._build_page_url(2) == ("https://arxiv.org/list/cs.CL/recent?skip=50&show=50")

    assert scraper._build_page_url(3) == ("https://arxiv.org/list/cs.CL/recent?skip=100&show=50")


def test_build_page_url_rejects_invalid_page_number() -> None:
    scraper = make_scraper()

    try:
        scraper._build_page_url(0)
    except ValueError as exc:
        assert str(exc) == ("page_number must be greater than or equal to 1")
    else:
        raise AssertionError("_build_page_url should reject page_number=0")


def test_scrape_respects_max_pages() -> None:
    html = FIXTURE_PATH.read_text(encoding="utf-8")
    scraper = make_scraper(max_pages=3)

    with patch.object(scraper, "_get", return_value=html) as get:
        articles = scraper.scrape()

    assert len(articles) == 6

    assert get.call_args_list == [
        call("https://arxiv.org/list/cs.CL/recent?skip=0&show=50"),
        call("https://arxiv.org/list/cs.CL/recent?skip=50&show=50"),
        call("https://arxiv.org/list/cs.CL/recent?skip=100&show=50"),
    ]


def test_scrape_stops_when_page_has_no_articles() -> None:
    html = FIXTURE_PATH.read_text(encoding="utf-8")
    scraper = make_scraper(max_pages=3)

    with patch.object(
        scraper,
        "_get",
        side_effect=[html, "<html><body></body></html>"],
    ) as get:
        articles = scraper.scrape()

    assert len(articles) == 2
    assert get.call_count == 2


def test_scrape_uses_http_and_parses_fixture() -> None:
    html = FIXTURE_PATH.read_text(encoding="utf-8")
    scraper = make_scraper()

    with patch.object(scraper, "_get", return_value=html) as get:
        articles = scraper.scrape()

    get.assert_called_once_with("https://arxiv.org/list/cs.CL/recent?skip=0&show=50")
    assert len(articles) == 2
    assert articles[0].arxiv_id == "2609.11913"
