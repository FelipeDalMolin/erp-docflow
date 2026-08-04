# Validação local equivalente ao Application CI

- **Classe:** runbook operacional
- **Estado:** vigente para a fundação R0 e a persistência relacional da S2.02
- **Atualizar quando:** versões pinadas ou comandos do Application CI mudarem

Este runbook reproduz localmente, na mesma ordem, os comandos `run` executados
pelo Application CI para backend, frontend e configuração do Compose. Execute
todos os blocos a partir da raiz do repositório. O `cd apps/api` reproduz o
`working-directory` do job de backend; as actions de setup da CI são
representadas localmente pelas versões requeridas abaixo.

## Escopo comprovado

Os checks comprovam a fundação técnica R0 e o contrato relacional da S2.02 em
PostgreSQL real: migrations, constraints, repositórios e metadados documentais
sintéticos. Eles não comprovam preservação dos bytes do original, upload HTTP,
interpretação, revisão ou aceite. Essas capacidades permanecem nas slices
posteriores.

O Structural CI permanece separado e continua responsável pela estrutura do
repositório, links e catálogos documentais.

### Guard transitório do ADR-0021

Backend, frontend e `docker compose config --quiet` não controlam o runtime
compartilhado. O bloco local de PostgreSQL abaixo, porém, ainda usa o
`compose.yml` com project name `erp_docflow_dev` e pode adotar ou alterar o
runtime legado iniciado por outra worktree.

Até `compose.check.yml`, `compose.rehearsal.yml` e `devctl` serem integrados:

- não executar o bloco mutante de PostgreSQL no `app-host` nem em worktree;
- usar os checks do GitHub Actions como evidência isolada ou abrir Issue
  operacional para uma execução local explicitamente controlada;
- não inventar project name, porta ou volume alternativo sem que o modelo
  efetivo prove isolamento;
- nunca usar `down`, `--volumes` ou `prune` contra `erp_docflow_dev` para limpar
  uma validação.

Os comandos permanecem registrados para explicar a cobertura vigente; não são
autorização de execução no runtime compartilhado.

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
uv run pytest -m "not postgres"
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

Crie `.env` conforme o [runbook do Compose](DEVELOPMENT_COMPOSE.md) antes da
validação. O arquivo é ignorado pelo Git, a senha deve ser apenas local e
sintética e o Compose falha se qualquer componente
`ERP_DOCFLOW_DATABASE_*` obrigatório estiver vazio.

```bash
docker compose version
docker compose config --quiet
```

Esse comando valida a configuração sem construir imagens, iniciar containers ou
ocupar as portas do host. Use `--quiet`: a representação expandida pode conter a
configuração sensível local. Para executar API/web em `8100/5180` e o PostgreSQL
sem porta publicada, siga o [Compose de desenvolvimento](DEVELOPMENT_COMPOSE.md).

## Migrations e integração PostgreSQL — referência pendente de isolamento

Os comandos abaixo usam somente o banco local sintético e não gravam bytes de
documentos no PostgreSQL. O Docker pode baixar as imagens pinadas quando elas
ainda não estiverem presentes no host; a suíte da aplicação não chama serviços
externos:

```bash
docker compose build api
docker compose up --detach --wait postgres
docker compose run -T --rm --no-deps api uv run alembic upgrade head
docker compose run -T --rm --no-deps api uv run alembic current --check-heads
docker compose run -T --rm --no-deps api uv run alembic check
docker compose run -T --rm --no-deps api uv run pytest -m postgres
docker compose run -T --rm --no-deps api sh -c \
  'PYTHONPATH=src uv run python tests/integration/postgresql/restart_probe.py seed'
docker compose restart postgres
docker compose up --detach --wait postgres
docker compose run -T --rm --no-deps api uv run alembic current --check-heads
docker compose run -T --rm --no-deps api sh -c \
  'PYTHONPATH=src uv run python tests/integration/postgresql/restart_probe.py verify'
docker compose down --remove-orphans
```

O probe grava e relê uma materialização determinística composta exclusivamente
por referências e metadados sintéticos. Assim, o restart verifica o schema e a
ocorrência concluída, mas não cria nem recupera o arquivo original.
`docker compose down` preserva o volume. Não execute downgrade nem remoção de
volumes em banco que não esteja comprovadamente descartável.

Na CI, o job `PostgreSQL / migrations and integration` usa este mesmo Compose,
um project name exclusivo da execução e componentes de credencial
explicitamente sintéticos. O PostgreSQL continua sem porta publicada. O job
confirma que existe exatamente um head, executa upgrade/check, faz `downgrade
base` seguido de novo `upgrade head`, roda os testes marcados com `postgres` e
semeia/relê o probe relacional depois de um restart.

O cleanup `docker compose down --volumes --remove-orphans` existe somente nesse
job efêmero e usa `if: always()`. O ciclo destrutivo e a remoção do volume são
exclusivos daquele banco comprovadamente descartável; não integram o
procedimento local normal.

## Resultado esperado

Todos os comandos devem encerrar com código `0`, migrations devem terminar no
único head e lockfiles não podem ser modificados. Uma falha local deve ser
corrigida e reproduzida antes do push; não se deve relaxar um check da CI apenas
para obter resultado verde.
