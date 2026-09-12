# Relatório — IML4.1 Construção de mecanismos de captação de dados

## 1. Problema

A atividade solicita a construção de um mecanismo computacional capaz de coletar informações da seção de artigos científicos do arXiv e armazenar os dados em CSV, com conteinerização e publicação no Docker Hub por meio de CI/CD.

## 2. Fonte dos dados

Foi escolhida a seção **Computation and Language (cs.CL)**:

https://arxiv.org/list/cs.CL/recent

A página disponibiliza, por artigo, informações como identificador arXiv, título, autores, comentários e categorias/assuntos.

## 3. Estratégia de coleta

A aplicação realiza HTTP GET sobre a página e utiliza **BeautifulSoup** para interpretar o HTML. Os seletores são aplicados aos elementos semânticos da página, incluindo `li.arxiv-result`, `p.title`, `p.authors`, o bloco de comentários e as tags de assunto.

Existe suporte a paginação por meio do link **Next page**. A variável `ARXIV_MAX_PAGES` limita o volume coletado e evita requisições excessivas.

## 4. Validação

Os dados extraídos são convertidos para objetos **Pydantic**. Isso centraliza a definição do contrato de dados e valida campos obrigatórios, URLs e tipos.

## 5. Armazenamento

O padrão **Repository** isola a persistência. A implementação atual é `CsvArticleRepository`, que grava UTF-8 com cabeçalho e uma linha por artigo.

## 6. Design Patterns

### Strategy

A interface abstrata `Scraper` define a operação de coleta. `ArxivScraper` é uma implementação concreta. Novas fontes podem ser incorporadas criando outras implementações de `Scraper`.

### Repository

A interface `ArticleRepository` abstrai a persistência. O serviço não conhece os detalhes do CSV.

### Service Layer

`ScrapingService` coordena o caso de uso: coleta os artigos com o scraper e os persiste no repositório.

## 7. Boas práticas

O projeto utiliza:

- Poetry para gerenciamento de dependências e empacotamento;
- Pydantic para validação do modelo de domínio;
- Ruff para lint e formatação;
- Pre-commit para execução automática de verificações antes dos commits;
- pytest para testes unitários;
- Makefile para padronizar comandos;
- `.gitignore` e `.dockerignore`;
- Docker com usuário não-root;
- variáveis de ambiente para configuração;
- documentação e type hints;
- separação entre domínio, coleta, persistência e entrada da aplicação.

## 8. Containerização

O `Dockerfile` utiliza Python 3.12 slim, instala as dependências de produção com Poetry, cria um usuário sem privilégios e monta `/app/data` como volume para permitir a recuperação do CSV pelo host.

## 9. CI/CD

O workflow do GitHub Actions possui dois jobs:

1. **quality**: instala Python/Poetry, instala dependências, executa Ruff e pytest;
2. **docker**: constrói a imagem, executa um teste básico de inicialização e, em `push` na branch `main`, autentica no Docker Hub e publica as tags `latest` e `sha`.

Também foram habilitados SBOM e provenance na publicação da imagem.

## 10. Segurança

Credenciais do Docker Hub não ficam armazenadas no código. O workflow utiliza:

- `DOCKERHUB_USERNAME` como GitHub Actions Variable;
- `DOCKERHUB_TOKEN` como GitHub Actions Secret.

O token deve ser criado no Docker Hub com a menor permissão necessária para publicação no repositório.

## 11. Execução

Localmente:

```bash
poetry install
make check
make scrape
```

Com Docker:

```bash
docker build -t iml41-arxiv-scraper .
docker run --rm -v "$PWD/data:/app/data" iml41-arxiv-scraper
```

## 12. Resultado esperado

Ao final da execução, `data/articles.csv` conterá os artigos encontrados na seção configurada do arXiv.
