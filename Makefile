POETRY ?= poetry
PYTHON ?= python3

.PHONY: install scrape test lint format check clean

install:
	$(POETRY) install

scrape:
	$(POETRY) run arxiv-scraper

test:
	$(POETRY) run pytest -q

lint:
	$(POETRY) run ruff check .

format:
	$(POETRY) run ruff format .

check: lint test

clean:
	rm -rf .pytest_cache .ruff_cache __pycache__ .coverage
