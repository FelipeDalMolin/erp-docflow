# Compose de desenvolvimento da aplicação

Status: implementado para a fundação R0 e a persistência relacional da S2.02

Este Compose executa a API, a interface web e um PostgreSQL interno em
desenvolvimento. Ele não é um bundle de piloto ou produção e não contém object
storage, worker, fila, dados reais ou secrets versionados. O volume nomeado do
PostgreSQL preserva somente o estado relacional sintético entre reinícios.

A página entregue pelo serviço web é um shell técnico R0, não um ERP funcional.
A imagem da API contém a camada relacional da #39, mas o runtime HTTP ainda
expõe somente `GET /health` e não aciona a materialização. Também não há bytes
preservados, upload HTTP, interpretação, revisão ou aceite de PDFs e outros
documentos. A preservação verificável do original pertence à S2.03/#40.

## Pré-requisitos

- Docker Engine com Docker Compose v2 e o plugin Buildx funcional;
- portas locais `8100` e `5180` livres;
- um arquivo `.env` ignorado pelo Git com uma senha exclusivamente local e
  sintética para o PostgreSQL.

Os comandos abaixo partem da raiz do repositório.

Para executar exatamente o check de configuração usado pelo Application CI,
consulte a [validação local equivalente ao CI](VALIDACAO_LOCAL_CI.md). Esse check
não inicia os serviços nem ocupa portas; os comandos abaixo executam o runtime.

## Preparar a configuração local

Crie o arquivo ignorado a partir do modelo versionado, preencha os três
componentes e restrinja sua leitura. Não use credencial compartilhada, de
produção ou de qualquer outro sistema:

```bash
cp .env.example .env
chmod 600 .env
```

Edite `.env` localmente e defina `ERP_DOCFLOW_DATABASE_NAME`,
`ERP_DOCFLOW_DATABASE_USER` e `ERP_DOCFLOW_DATABASE_PASSWORD`. Os valores do
modelo são vazios: o Compose falha fechado enquanto qualquer componente estiver
ausente e não oferece credencial padrão. Não registre o conteúdo do arquivo em
logs, documentos ou commits.

A API recebe host, porta, nome, usuário e senha como componentes separados. O
backend monta a URL `postgresql+psycopg` com `SQLAlchemy URL.create`, sem
concatenar ou registrar a senha. Importar ou iniciar a aplicação não executa
migration automaticamente.

## Validar, migrar e iniciar

```bash
docker compose config --quiet
docker compose build api web
docker compose up --detach --wait postgres
docker compose run -T --rm --no-deps api uv run alembic upgrade head
docker compose run -T --rm --no-deps api uv run alembic current --check-heads
docker compose run -T --rm --no-deps api uv run alembic check
docker compose up --detach --wait api web
docker compose ps
```

Os três serviços possuem healthchecks. A API depende da saúde do PostgreSQL,
mas migrations continuam explícitas: iniciar ou importar a aplicação não
executa `alembic upgrade`. Aguarde até que `docker compose ps` mostre `healthy`.
Somente API e web publicam portas, sempre no loopback `127.0.0.1`; o PostgreSQL
permanece acessível apenas pela rede interna do Compose.

No host compartilhado, as portas publicadas são intencionalmente diferentes
das portas internas para não colidir com o Jubileu:

| Serviço | Host | Container |
| --- | --- | --- |
| API | `127.0.0.1:8100` | `8000` |
| web | `127.0.0.1:5180` | `5173` |
| PostgreSQL | não publicada | `5432` |

Os healthchecks continuam usando as portas internas dos containers.

Valide as portas publicadas:

```bash
curl --fail --header 'Accept: application/json' \
  http://127.0.0.1:8100/health
curl --fail http://127.0.0.1:5180/
```

A resposta da API deve ser:

```json
{"status":"ok","service":"erp-docflow-api"}
```

A interface abre em `http://127.0.0.1:5180`. O valor
`VITE_API_BASE_URL=http://localhost:8100` é configuração pública de build e
runtime do Vite; não é credencial.

Para conferir a migration aplicada sem revelar a URL do banco:

```bash
docker compose run -T --rm --no-deps api uv run alembic current --check-heads
docker compose run -T --rm --no-deps api uv run alembic check
```

## Hot reload

O Compose monta apenas os fontes usados em runtime:

- `apps/api/src` para reload do Uvicorn;
- `apps/web/src` e `apps/web/index.html` para HMR do Vite.

Uma alteração nesses arquivos deve aparecer sem rebuild da imagem. Mudanças
em dependências, lockfiles, Dockerfiles ou configurações fora desses mounts
exigem novo `docker compose build`.

Para acompanhar a recompilação:

```bash
docker compose logs --follow api web
```

## Encerrar

```bash
docker compose down --remove-orphans
```

Esse comando encerra os containers e a rede do projeto `erp_docflow_dev`, mas
preserva o volume relacional `postgres_data`. Não desliga o servidor/WSL e não
fecha a sessão remota do VS Code. `docker compose down --volumes` não pertence
ao fluxo normal e não deve ser usado para contornar falhas ou migrations.

Para comprovar a persistência relacional, o probe abaixo grava uma
materialização determinística e exclusivamente sintética, reinicia o PostgreSQL
sem remover o volume e relê ocorrência, envelope, arquivo referenciado e evento:

```bash
docker compose run -T --rm --no-deps api sh -c \
  'PYTHONPATH=src uv run python tests/integration/postgresql/restart_probe.py seed'
docker compose restart postgres
docker compose up --detach --wait postgres
docker compose run -T --rm --no-deps api uv run alembic current --check-heads
docker compose run -T --rm --no-deps api sh -c \
  'PYTHONPATH=src uv run python tests/integration/postgresql/restart_probe.py verify'
```

O probe persiste somente referências e metadados inventados; ele não cria nem
comprova a recuperação de um arquivo original. Essa evidência depende do object
storage da #40.

## Diagnóstico

Se uma porta estiver ocupada, identifique primeiro o processo ou container
existente; não altere o contrato de portas silenciosamente. Para inspecionar o
estado e os logs:

```bash
docker compose ps
docker compose logs api
docker compose logs web
docker compose logs postgres
```

Se a senha local for alterada depois que o volume foi inicializado, o valor
novo não reconfigura automaticamente o usuário existente. Preserve o `.env`
usado para aquele volume e investigue antes de qualquer ação; excluir volume
não é procedimento de recuperação deste runbook.

Se o build falhar informando ausência de `docker-buildx`, repare ou instale o
plugin compatível com a versão do Docker deste host antes de continuar. Esse é
um requisito da instalação local, não uma alteração a ser feita no Compose do
projeto.

## Registro do ADR-0008

A fundação R0 acionou a primeira materialização da direção aceita no ADR-0008.
A S2.02 acrescenta PostgreSQL local e persistência relacional sintética, sem
declarar o Compose como estratégia de produção nem satisfazer os gates de
storage, backup/restore, autenticação ou segurança das fases seguintes.
