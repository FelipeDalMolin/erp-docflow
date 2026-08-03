# Route Map

Mapa das rotas que existem no bootstrap técnico R0. Ele registra evidência do
código atual; não define endpoints ou jornadas futuras.

## Rotas técnicas implementadas

| Superfície | Método/caminho | Responsabilidade atual | Fonte | Evidência |
| --- | --- | --- | --- | --- |
| API | `GET /health` | responder o estado determinístico do processo FastAPI | `apps/api/src/erp_docflow_api/main.py` | #34, PR #90; teste de contrato em `apps/api/tests/test_health.py` |
| web | `/` | apresentar a fundação técnica R0 e seus limites | `apps/web/src/app/router.tsx` | #35, PR #91; teste do router |
| web | `/system` | apresentar configuração e roadmap informativo, sem consultar a API | `apps/web/src/app/router.tsx` | #35, PR #91; teste do router |
| web | `*` | renderizar a página de rota não encontrada | `apps/web/src/app/router.tsx` | #35, PR #91; teste do router |

O Compose integrado pelos PRs #94 e #97 publica essas superfícies apenas para
desenvolvimento local. A configuração de `VITE_API_BASE_URL` não representa
integração funcional: a interface ainda não chama a API.

## Capacidades que não existem

```text
Não há rota de intake ou upload.
Não há rota de interpretação ou processamento PDF-first.
Não há Inbox, review, aceite, domínio gerencial ou operação ERP funcional.
Não há contrato HTTP de produto além do healthcheck técnico.
```

O profile e o dataset sintético PDF-first integrados no PR #93 são artefatos de
preparação e avaliação. Eles não materializam endpoint, serviço de
processamento ou fluxo de usuário.

## Quando atualizar

- Quando uma rota técnica mudar ou ganhar novo contrato testado.
- Quando a Phase 2 criar rotas relacionadas ao núcleo GED.
- Quando uma rota passar a depender de ADR, entidade, módulo ou diagrama.

## Regras

- Não registrar rotas hipotéticas como contrato.
- Distinguir healthcheck, shell web e configuração de uma capacidade de produto.
- Cada rota futura deve apontar módulo, entidades afetadas, ADRs relacionados e documentação de suporte.
