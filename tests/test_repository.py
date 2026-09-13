import csv
from datetime import UTC, datetime

from arxiv_scraper.models import Article
from arxiv_scraper.repository import CsvArticleRepository


def test_repository_writes_csv(tmp_path) -> None:
    output = tmp_path / "articles.csv"

    article = Article(
        arxiv_id="1234.5678",
        title="Example, with comma",
        authors=["A. Author", "B. Author"],
        comments="Example comment; with semicolon",
        subjects="Computation and Language (cs.CL)",
        pdf_url="https://arxiv.org/pdf/1234.5678",
        html_url="https://arxiv.org/html/1234.5678",
        source_url="https://arxiv.org/list/cs.CL/recent",
        scraped_at=datetime.now(UTC),
    )

    CsvArticleRepository(output).save_all([article])

    with output.open(
        encoding="utf-8",
        newline="",
    ) as file:
        rows = list(
            csv.DictReader(
                file,
                delimiter="|",
            )
        )

    assert rows[0]["arxiv_id"] == "1234.5678"
    assert rows[0]["title"] == "Example, with comma"
    assert rows[0]["authors"] == "A. Author; B. Author"
    assert rows[0]["comments"] == "Example comment; with semicolon"
