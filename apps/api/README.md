# API

Backend do ERP DocFlow com o healthcheck R0 e a materialização relacional
PDF-first da #39. O único endpoint continua sendo `GET /health`; domínio,
migrations e repositórios PostgreSQL ainda não são expostos por HTTP.

O schema persiste ocorrência idempotente, `DocumentEnvelope`, versão original,
referência `FileObject` verificada e `AuditEvent` append-only. Ele não grava
bytes, não comprova que o objeto existe e não inclui MinIO, upload, OCR,
interpretação, autenticação, provider externo ou dado real.

## Pré-requisitos

- Python 3.13.14;
- [uv](https://docs.astral.sh/uv/).
- PostgreSQL 18.4 para migrations e testes marcados `postgres`.

O patch do Python é definido em `.python-version` e o intervalo compatível em
`pyproject.toml`.

## Preparar o ambiente

Dentro de `apps/api`:

```bash
uv sync --locked
```

## Executar

```bash
uv run uvicorn --app-dir src erp_docflow_api.main:app --host 127.0.0.1 --port 8000
```

Em outro terminal, valide o contrato:

```bash
curl --fail --header 'Accept: application/json' http://127.0.0.1:8000/health
```

Resposta esperada:

```json
{"status":"ok","service":"erp-docflow-api"}
```

Importar a aplicação ou iniciar o Uvicorn não executa migrations. Para preparar
o PostgreSQL interno e aplicar o head explicitamente, siga o
[runbook do Compose](../../docs/operations/DEVELOPMENT_COMPOSE.md).

## Migrations

Com os cinco componentes `ERP_DOCFLOW_DATABASE_*` configurados:

```bash
uv run alembic upgrade head
uv run alembic current --check-heads
uv run alembic check
```

`create_all`, SQLite e upgrade automático no startup não pertencem ao contrato.
Downgrade só pode ser executado em banco comprovadamente descartável; a CI cria
um banco próprio para esse ciclo.

## Validar

```bash
uv run ruff check .
uv run pytest -m "not postgres"
```

Os testes reais de PostgreSQL, incluindo concorrência, rollback, constraints e
imutabilidade, são executados pelo lifecycle documentado na
[validação local equivalente à CI](../../docs/operations/VALIDACAO_LOCAL_CI.md).
