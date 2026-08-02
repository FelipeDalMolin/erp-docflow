# Compose de desenvolvimento da aplicação

Status: implementado para a fundação R0 da Phase 1

Este Compose executa somente a API e a interface web em desenvolvimento. Ele
não é um bundle de piloto ou produção e não contém PostgreSQL, object storage,
worker, fila, dados reais, secrets ou volumes persistentes de produto.

## Pré-requisitos

- Docker Engine com Docker Compose v2 e o plugin Buildx funcional;
- portas locais `8100` e `5180` livres.

Os comandos abaixo partem da raiz do repositório.

## Validar e iniciar

```bash
docker compose config
docker compose build
docker compose up --detach
docker compose ps
```

Os dois serviços possuem healthchecks independentes e não usam
`depends_on`. Aguarde até que `docker compose ps` mostre `healthy` para ambos.
As portas são publicadas somente no loopback `127.0.0.1`, sem exposição direta
às outras interfaces de rede do host.

No host compartilhado, as portas publicadas são intencionalmente diferentes
das portas internas para não colidir com o Jubileu:

| Serviço | Host | Container |
| --- | --- | --- |
| API | `127.0.0.1:8100` | `8000` |
| web | `127.0.0.1:5180` | `5173` |

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

Esse comando encerra os containers e a rede do projeto
`erp_docflow_dev`. Não desliga o servidor/WSL e não fecha a sessão remota do
VS Code. Não há volume persistente de produto neste Compose.

## Diagnóstico

Se uma porta estiver ocupada, identifique primeiro o processo ou container
existente; não altere o contrato de portas silenciosamente. Para inspecionar o
estado e os logs:

```bash
docker compose ps
docker compose logs api
docker compose logs web
```

Se o build falhar informando ausência de `docker-buildx`, repare ou instale o
plugin compatível com a versão do Docker deste host antes de continuar. Esse é
um requisito da instalação local, não uma alteração a ser feita no Compose do
projeto.

## Registro do ADR-0008

Esta slice aciona a primeira materialização da direção aceita no ADR-0008,
limitada ao desenvolvimento local e a dois serviços stateless. Ela não declara
o Compose como estratégia de produção, não cria persistência e não satisfaz os
gates de banco, storage, backup/restore ou segurança das fases seguintes.
