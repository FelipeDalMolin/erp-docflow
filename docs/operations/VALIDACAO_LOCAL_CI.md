# Validação local equivalente ao Application CI

- **Classe:** runbook operacional
- **Estado:** vigente para a fundação técnica R0 da Phase 1
- **Atualizar quando:** versões pinadas ou comandos do Application CI mudarem

Este runbook reproduz localmente, na mesma ordem, os comandos `run` executados
pelo Application CI para backend, frontend e configuração do Compose. Execute
todos os blocos a partir da raiz do repositório. O `cd apps/api` reproduz o
`working-directory` do job de backend; as actions de setup da CI são
representadas localmente pelas versões requeridas abaixo.

## Escopo comprovado

Os checks comprovam somente a fundação técnica R0: API mínima, shell web e
configuração do Compose de desenvolvimento. Eles não comprovam um ERP funcional
e não implementam nem validam upload, intake, interpretação, revisão ou
persistência de PDFs e outros documentos.

O Structural CI permanece separado e continua responsável pela estrutura do
repositório, links e catálogos documentais.

## Versões requeridas

| Ferramenta | Versão |
| --- | --- |
| Python | `3.13.14` |
| uv | `0.11.16` |
| Node.js | `24.18.0` |
| pnpm | `11.13.1` |
| Docker Compose | v2 |

Os pins de Python e Node também estão registrados, respectivamente, em
`apps/api/.python-version` e `.nvmrc`. O pin do pnpm está no campo
`packageManager` do `package.json` raiz.

## Backend

```bash
cd apps/api
uv sync --locked
uv run ruff check .
uv run pytest
cd ../..
```

`uv sync --locked` deve falhar, em vez de alterar `uv.lock`, se as dependências
declaradas e o lockfile divergirem.

## Frontend

```bash
pnpm install --frozen-lockfile
pnpm --filter @erp-docflow/web lint
pnpm --filter @erp-docflow/web typecheck
pnpm --filter @erp-docflow/web test
pnpm --filter @erp-docflow/web build
```

`pnpm install --frozen-lockfile` deve falhar, em vez de alterar
`pnpm-lock.yaml`, se o workspace e o lockfile divergirem.

## Configuração do Compose

```bash
docker compose version
docker compose config --quiet
```

Esse comando valida a configuração sem construir imagens, iniciar containers ou
ocupar as portas do host. Para executar a fundação R0 em `5180` e `8100`, siga o
[Compose de desenvolvimento](DEVELOPMENT_COMPOSE.md).

## Resultado esperado

Todos os comandos devem encerrar com código `0` e não modificar lockfiles. Uma
falha local deve ser corrigida e reproduzida antes do push; não se deve relaxar
um check da CI apenas para obter resultado verde.
