# IML4.1 — Construção de mecanismos de captação de dados

Scraper conteinerizado para a seção **Computation and Language (cs.CL)** do arXiv.

## Objetivo

A aplicação acessa a página pública de submissões recentes do arXiv, extrai os metadados disponíveis dos artigos e grava os resultados em CSV.

Fonte: <https://arxiv.org/list/cs.CL/recent>

Os campos coletados são:

- `arxiv_id`
- `title`
- `authors`
- `comments`
- `subjects`
- `pdf_url`
- `html_url`
- `source_url`
- `scraped_at`

## Arquitetura

O projeto foi organizado em camadas simples e testáveis:

```text
src/arxiv_scraper/
├── cli.py          # ponto de entrada
├── config.py       # configurações com Pydantic Settings
├── models.py       # modelo de domínio
├── scraper.py      # Strategy + implementação do scraper
├── repository.py   # Repository para persistência CSV
└── service.py      # orquestração do caso de uso
```

### Design Patterns

**Strategy Pattern:** `Scraper` define o contrato de coleta e `ArxivScraper` implementa a estratégia para o arXiv. Isso permite adicionar outras fontes futuramente sem alterar o serviço principal.

**Repository Pattern:** `CsvArticleRepository` encapsula a persistência dos dados e mantém essa responsabilidade fora do scraper.

**Service Layer:** `ScrapingService` coordena coleta e armazenamento.

## Execução local

### Pré-requisitos

- Python 3.12+
- Poetry

```bash
poetry install
poetry run arxiv-scraper
```

Por padrão, o arquivo será criado em `data/articles.csv`.

Para alterar quantidade e arquivo:

```bash
ARXIV_MAX_PAGES=2 OUTPUT_FILE=data/articles.csv poetry run arxiv-scraper
```

## Makefile

```bash
make install
make scrape
make test
make lint
make format
make check
```

## Docker

Construção:

```bash
docker build -t arxiv-scraper:local .
```

Execução:

```bash
docker run --rm -v "$PWD/data:/app/data" arxiv-scraper:local
```

O volume permite recuperar o CSV gerado no host.

## Pre-commit

Instalação:

```bash
poetry run pre-commit install
```

Execução manual:

```bash
poetry run pre-commit run --all-files
```

## CI/CD

O workflow `.github/workflows/ci-cd.yml` executa:

1. checkout do código;
2. instalação das dependências;
3. Ruff;
4. testes;
5. build da imagem Docker;
6. teste do container;
7. login no Docker Hub;
8. push da imagem quando o evento for um `push` na branch `main`.

Configure no repositório:

- **Variable:** `DOCKERHUB_USERNAME`
- **Secret:** `DOCKERHUB_TOKEN`

A imagem será publicada como:

```text
<DOCKERHUB_USERNAME>/iml41-arxiv-scraper:latest
```

## Exemplo de saída

```csv
arxiv_id,title,authors,comments,subjects,pdf_url,html_url,source_url,scraped_at
2609.11913,"Distance generalization in transformers: why bother with positional encoding?","Daniel Henrik Nevermann; Claudius Gros","15 pages, 7 figures","Computation and Language (cs.CL)",https://arxiv.org/pdf/2609.11913,https://arxiv.org/html/2609.11913,https://arxiv.org/list/cs.CL/recent,2026-09-12T22:00:00+00:00
```

## Relação com a atividade

A solução atende aos requisitos solicitados:

- captação automatizada de dados;
- armazenamento em CSV;
- Pydantic;
- Poetry;
- Makefile;
- Pre-commit;
- Ruff;
- testes automatizados;
- documentação;
- Design Patterns;
- containerização com Docker;
- CI/CD com GitHub Actions;
- publicação no Docker Hub.
