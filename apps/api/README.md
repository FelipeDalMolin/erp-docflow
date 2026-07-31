# API

Backend mínimo do ERP DocFlow para a Phase 1. Nesta slice, a aplicação expõe
somente o healthcheck público `GET /health`; não há banco, storage,
autenticação, providers externos ou dados reais.

## Pré-requisitos

- Python 3.13.14;
- [uv](https://docs.astral.sh/uv/).

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

## Validar

```bash
uv run ruff check .
uv run pytest
```
