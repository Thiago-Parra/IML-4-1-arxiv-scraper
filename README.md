## Autor: **Thiago Henrique Parra**

# IML4.1 — Construção de mecanismos de captação de dados

Scraper conteinerizado para coleta de artigos recentes da categoria **Computation and Language (cs.CL)** do [arXiv](https://arxiv.org/).

O projeto foi desenvolvido como atividade **IML 4.1 — Construção de mecanismos de captação de dados** do MBA em Machine Learning in Production — UFSCar, com foco na construção de um mecanismo automatizado de captação de dados utilizando boas práticas de desenvolvimento de software, testes automatizados, conteinerização e integração contínua.

## Objetivo

O objetivo do projeto é desenvolver um mecanismo capaz de:

- acessar a página de artigos recentes da categoria `cs.CL` do arXiv;
- coletar os metadados dos artigos publicados recentemente;
- armazenar os dados coletados em um arquivo CSV;
- executar o processo localmente ou dentro de um container Docker;
- disponibilizar uma estrutura preparada para integração com CI/CD;
- aplicar boas práticas de desenvolvimento, como tipagem, validação de dados, testes, linting e formatação automática.

## Dados coletados

Para cada artigo, o scraper coleta as seguintes informações:

| Campo | Descrição |
|---|---|
| `arxiv_id` | Identificador do artigo no arXiv |
| `title` | Título do artigo |
| `authors` | Lista de autores |
| `comments` | Comentários adicionais do artigo |
| `subjects` | Categorias/assuntos do artigo |
| `pdf_url` | URL para o arquivo PDF |
| `html_url` | URL para a versão HTML do artigo |
| `source_url` | URL da página de listagem utilizada na coleta |

Os dados são armazenados em:

```text
data/articles.csv
```

O arquivo utiliza **UTF-8** e o caractere `|` como separador de campos.

A escolha do separador `|` evita conflitos com vírgulas presentes naturalmente em títulos, comentários ou outros campos textuais.

## Estrutura do projeto

```text
iml41-arxiv-scraper/
├── .github/
│   └── workflows/
│       └── ci-cd.yml
├── data/
│   └── articles.csv
├── src/
│   └── arxiv_scraper/
│       ├── cli.py
│       ├── config.py
│       ├── models.py
│       ├── repository.py
│       ├── scraper.py
│       └── service.py
├── tests/
│   ├── fixtures/
│   │   └── arxiv_recent.html
│   ├── test_repository.py
│   └── test_scraper.py
├── .dockerignore
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── Dockerfile
├── LICENSE
├── Makefile
├── README.md
└── pyproject.toml
```

## Arquitetura

O projeto foi organizado em componentes com responsabilidades distintas.

```text
                         ┌─────────────────────┐
                         │       CLI           │
                         │      cli.py         │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │      Service        │
                         │     service.py      │
                         └──────────┬──────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
          ┌─────────────────────┐         ┌─────────────────────┐
          │       Scraper       │         │    Repository       │
          │     scraper.py      │         │   repository.py     │
          └──────────┬──────────┘         └──────────┬──────────┘
                     │                               │
                     ▼                               ▼
          ┌─────────────────────┐         ┌─────────────────────┐
          │       arXiv          │         │   articles.csv      │
          │      Web Page        │         │                     │
          └─────────────────────┘         └─────────────────────┘
```

### Componentes

**`cli.py`**

Ponto de entrada da aplicação. Responsável por configurar o logging, carregar as configurações e iniciar o processo de coleta.

**`config.py`**

Centraliza as configurações da aplicação utilizando `Pydantic Settings`.

**`models.py`**

Define o modelo `Article` utilizado para validação e tipagem dos dados coletados.

**`scraper.py`**

Responsável pelo acesso ao arXiv, paginação e extração dos dados HTML.

**`service.py`**

Orquestra o processo de coleta e persistência dos dados.

**`repository.py`**

Responsável pela gravação dos artigos coletados no arquivo CSV.

## Paginação

A página de artigos recentes do arXiv utiliza os parâmetros `skip` e `show` para controlar a paginação.

O scraper utiliza páginas de até **50 artigos**.

Por exemplo:

```text
Página 1:
https://arxiv.org/list/cs.CL/recent?skip=0&show=50

Página 2:
https://arxiv.org/list/cs.CL/recent?skip=50&show=50

Página 3:
https://arxiv.org/list/cs.CL/recent?skip=100&show=50
```

A quantidade máxima de páginas processadas é controlada pela configuração `MAX_PAGES`.

Caso uma página não contenha artigos, o processo de paginação é interrompido.

## Requisitos

Para executar o projeto localmente, são necessários:

- Python 3.12 ou superior;
- Poetry;
- GNU Make, opcionalmente;
- Docker, para execução em container.

## Instalação

Clone o repositório:

```bash
git clone <URL_DO_REPOSITORIO>
cd iml41-arxiv-scraper
```

Instale as dependências:

```bash
poetry install
```

Entre no ambiente virtual criado pelo Poetry:

```bash
poetry shell
```

Ou execute os comandos diretamente através do Poetry:

```bash
poetry run <comando>
```

## Configuração

As configurações podem ser definidas por variáveis de ambiente.

Um arquivo de exemplo está disponível em:

```text
.env.example
```

Exemplo:

```env
SOURCE_URL=https://arxiv.org/list/cs.CL/recent
OUTPUT_FILE=data/articles.csv
MAX_PAGES=10
TIMEOUT_SECONDS=20
USER_AGENT=IML4.1-Arxiv-Scraper/1.0
```

### Configurações disponíveis

| Variável | Padrão | Descrição |
|---|---|---|
| `SOURCE_URL` | `https://arxiv.org/list/cs.CL/recent` | URL da listagem do arXiv |
| `OUTPUT_FILE` | `data/articles.csv` | Arquivo de saída |
| `MAX_PAGES` | `10` | Quantidade máxima de páginas processadas |
| `TIMEOUT_SECONDS` | `20` | Timeout das requisições HTTP |
| `USER_AGENT` | `IML4.1-Arxiv-Scraper/1.0` | User-Agent utilizado nas requisições |

`MAX_PAGES` aceita valores entre `1` e `20`.

Como cada página possui até 50 artigos, o valor padrão de 10 páginas permite coletar até aproximadamente 500 artigos por execução.

## Execução local

O scraper pode ser executado diretamente através do Poetry:

```bash
poetry run arxiv-scraper
```

Ou utilizando o Makefile:

```bash
make scrape
```

Ao executar o processo, serão exibidas mensagens de log semelhantes a:

```text
INFO | Configured max_pages=3
INFO | Scraping page 1/3: https://arxiv.org/list/cs.CL/recent?skip=0&show=50
INFO | Page 1/3: collected 50 articles
INFO | Scraping page 2/3: https://arxiv.org/list/cs.CL/recent?skip=50&show=50
INFO | Page 2/3: collected 50 articles
INFO | Scraping page 3/3: https://arxiv.org/list/cs.CL/recent?skip=100&show=50
INFO | Page 3/3: collected 50 articles
INFO | Scraping finished: 3 pages processed, 150 articles collected
INFO | Collected 150 articles and saved to data/articles.csv
```

## Saída

O resultado da execução é salvo em:

```text
data/articles.csv
```

Exemplo:

```text
arxiv_id|title|authors|comments|subjects|pdf_url|html_url|source_url
2609.11913|Distance generalization in transformers|Daniel Henrik Nevermann; Claudius Gros|15 pages, 7 figures|Computation and Language (cs.CL)|https://arxiv.org/pdf/2609.11913|https://arxiv.org/html/2609.11913|https://arxiv.org/list/cs.CL/recent
```

## Testes

Os testes automatizados utilizam `pytest`.

Execute:

```bash
poetry run pytest -v
```

Ou:

```bash
make test
```

Os testes verificam, entre outros pontos:

- parsing da estrutura HTML do arXiv;
- extração de títulos;
- extração de autores;
- extração de comentários;
- extração de subjects;
- geração das URLs de paginação;
- respeito ao limite de páginas configurado;
- interrupção da paginação quando não existem artigos;
- geração correta do arquivo CSV;
- tratamento de campos contendo vírgulas e ponto e vírgula.

Os testes do scraper utilizam um arquivo HTML de fixture:

```text
tests/fixtures/arxiv_recent.html
```

Dessa forma, o comportamento da extração HTML pode ser validado sem depender de uma requisição externa durante a execução dos testes.

## Qualidade de código

O projeto utiliza [Ruff](https://docs.astral.sh/ruff/) para linting e formatação.

Verifique problemas de lint:

```bash
poetry run ruff check .
```

Execute a formatação:

```bash
poetry run ruff format .
```

Verifique se todos os arquivos já estão formatados:

```bash
poetry run ruff format --check .
```

Também é possível utilizar:

```bash
make lint
```

## Pre-commit

O projeto possui configuração para `pre-commit`.

Instale os hooks:

```bash
poetry run pre-commit install
```

Execute manualmente:

```bash
poetry run pre-commit run --all-files
```

Os hooks ajudam a garantir que o código seja validado antes de ser enviado ao repositório.

## Makefile

Os principais comandos podem ser executados através do `Makefile`.

Exemplos:

```bash
make install
make scrape
make test
make lint
make format
```

Para visualizar os comandos disponíveis:

```bash
make help
```

## Docker

O projeto também pode ser executado em um container Docker.

### Construção da imagem

Construa a imagem:

```bash
docker build -t iml41-arxiv-scraper .
```

### Execução

Execute:

```bash
docker run --rm -v "$PWD/data:/app/data" iml41-arxiv-scraper
```

No PowerShell:

```powershell
docker run --rm -v "${PWD}/data:/app/data" iml41-arxiv-scraper
```

O diretório local `data` é montado no diretório `/app/data` do container.

Dessa forma, o arquivo gerado pelo scraper permanece disponível no host após a execução do container.

## Segurança do container

A aplicação é executada dentro do container utilizando um usuário não privilegiado:

```text
appuser
```

O projeto também utiliza uma imagem base oficial do Python e mantém as dependências declaradas no `pyproject.toml`.

O diretório destinado aos dados é exposto através de:

```text
/app/data
```

## CI/CD

O projeto possui um workflow de GitHub Actions em:

```text
.github/workflows/ci-cd.yml
```

O pipeline tem como objetivo automatizar o processo de validação e publicação da aplicação.

De forma geral, o fluxo contempla:

```text
Push / Pull Request
        │
        ▼
   Instalação das
    dependências
        │
        ▼
       Lint
        │
        ▼
      Testes
        │
        ▼
  Build da imagem
      Docker
        │
        ▼
 Publicação no
   Docker Hub
```

A publicação da imagem Docker depende da configuração das credenciais necessárias no GitHub Actions.

## Docker Hub

A imagem pode ser publicada no Docker Hub utilizando um repositório, por exemplo:

```text
<DOCKERHUB_USERNAME>/iml41-arxiv-scraper
```

Exemplo de build local com uma tag específica:

```bash
docker build -t <DOCKERHUB_USERNAME>/iml41-arxiv-scraper:latest .
```

Login:

```bash
docker login
```

Push:

```bash
docker push <DOCKERHUB_USERNAME>/iml41-arxiv-scraper:latest
```

No pipeline de CI/CD, essas credenciais devem ser armazenadas como secrets do GitHub, e não diretamente no código-fonte.

## Boas práticas utilizadas

O projeto foi estruturado considerando princípios de engenharia de software aplicados a pipelines de dados.

Entre as práticas utilizadas estão:

**Separação de responsabilidades**

A coleta, validação, persistência e orquestração são realizadas por componentes diferentes.

**Validação com Pydantic**

Os dados extraídos do HTML são validados através de modelos tipados.

**Configuração externa**

Parâmetros operacionais são definidos por variáveis de ambiente, evitando valores fixos diretamente no código.

**Testes automatizados**

O comportamento principal do scraper e do repositório é validado através de testes com `pytest`.

**Fixture para testes**

O parser HTML pode ser testado sem depender de acesso à internet.

**Logging**

O processo de scraping fornece informações de progresso e quantidade de registros coletados.

**Conteinerização**

A aplicação pode ser executada de forma reprodutível através de Docker.

**Linting e formatação**

O código é validado e formatado automaticamente com Ruff.

**Pre-commit**

Os hooks permitem validar o código antes dos commits.

**CI/CD**

O GitHub Actions permite automatizar a validação e publicação da aplicação.

## Tratamento de erros e interrupção da paginação

Durante a coleta, o scraper verifica se a página processada contém artigos.

Quando uma página não retorna artigos, a execução da paginação é interrompida.

Exemplo de comportamento:

```text
Scraping page 1/10
Page 1/10: collected 50 articles

Scraping page 2/10
Page 2/10: collected 50 articles

Scraping page 3/10
Page 3/10: collected 0 articles
Stopping pagination.
```

Essa abordagem evita requisições desnecessárias quando não existem mais resultados disponíveis.

## Exemplo completo de execução

Um fluxo completo utilizando Poetry pode ser executado da seguinte forma:

```bash
poetry install
poetry run ruff check .
poetry run ruff format --check .
poetry run pytest -v
poetry run arxiv-scraper
```

Ou através do Makefile:

```bash
make install
make lint
make test
make scrape
```

## Exemplo completo utilizando Docker

```bash
docker build -t iml41-arxiv-scraper .

docker run --rm \
  -e MAX_PAGES=3 \
  -v "$PWD/data:/app/data" \
  iml41-arxiv-scraper
```

Após a execução:

```text
data/
└── articles.csv
```