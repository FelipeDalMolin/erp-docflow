# Document Map

Mapa derivado entre fontes documentais, autoridade, status e artefatos relacionados. Ele ajuda a localizar a fonte correta; não cria decisões nem contratos de implementação.

| Documento | Classe / autoridade | Estado | Relações principais |
| --- | --- | --- | --- |
| [`README.md`](../../README.md) | entrada curta do repositório | vigente | portal e status |
| [`docs/README.md`](../README.md) | portal e matriz de autoridade | vigente | todos os grupos documentais |
| [`docs/PROJECT_STATUS.md`](../PROJECT_STATUS.md) | snapshot de fase, gate e fila | vigente | Issues #1, #26, #33–#37 e #65 |
| [`AGENTS.md`](../../AGENTS.md) | guardrails executáveis do Codex | vigente | ADR-0003, 0005 e 0017 |
| [`.codex/config.toml`](../../.codex/config.toml) | capacidade técnica local do Codex | vigente | ADR-0005; não concede escopo |
| [`docs/MODELO_OPERACIONAL_DO_PROJETO.md`](../MODELO_OPERACIONAL_DO_PROJETO.md) | princípios de governança | vigente | ADR-0001–0017 conforme tema |
| [`docs/FLUXO_GITHUB_PROJECT.md`](../FLUXO_GITHUB_PROJECT.md) | lifecycle, prontidão, modos e outcomes | vigente | ADR-0003, 0005 e 0017 |
| [`docs/ESTRATEGIA_GIT.md`](../ESTRATEGIA_GIT.md) | branches, commits, PRs e merge | vigente | ADR-0003, 0005 e 0017 |
| [`docs/FLUXO_VSCODE_GIT_GITHUB_CLI.md`](../FLUXO_VSCODE_GIT_GITHUB_CLI.md) | runbook local/CLI | vigente | estratégia Git e ADR-0004 |
| [`docs/AMBIENTES.md`](../AMBIENTES.md) | ambientes atuais e planejados | vigente/planejado | ADR-0001, 0004, 0007, 0008 e 0014 |
| [`docs/WSL_MULTI_PROJETOS.md`](../WSL_MULTI_PROJETOS.md) | runbook WSL detalhado | vigente | ADR-0004 e ambientes |
| [`docs/ROADMAP.md`](../ROADMAP.md) | fases, dependências, resultados e gates | vigente | Epics #1 e #26–#32 |
| [`docs/ARCHITECTURE.md`](../ARCHITECTURE.md) | arquitetura lógica de referência | planejado/não implementado | ADR-0001, 0008–0014; ADR-0015/0016 propostos; UML de contexto/componentes |
| [`docs/DOCUMENT_PIPELINE.md`](../DOCUMENT_PIPELINE.md) | fluxo documental canônico | planejado/não implementado | ADR-0012, 0013 e 0016 proposto |
| [`docs/PROVIDER_STRATEGY.md`](../PROVIDER_STRATEGY.md) | capabilities, adapters e benchmark | proposta de descoberta | ADR-0016 proposto |
| [`docs/DATA_MODEL_BASELINE.md`](../DATA_MODEL_BASELINE.md) | conceitos e invariantes, sem schema físico | planejado/não implementado | ADR-0010–0013; ADR-0015/0016 propostos |
| [`docs/GLOSSARIO_DOCUMENTAL.md`](../GLOSSARIO_DOCUMENTAL.md) | vocabulário canônico | vigente | arquitetura, pipeline e dados |
| [`docs/reviews/GESTAO_DOCUMENTAL_INTELIGENTE.md`](../reviews/GESTAO_DOCUMENTAL_INTELIGENTE.md) | evidência histórica de descoberta | histórico | Issue #22; não é fonte normativa |
| [`docs/adr/README.md`](../adr/README.md) | governança e catálogo de decisões | vigente | ADR-0001–0017 |
| [`docs/traceability/README.md`](README.md) | regras e catálogo dos mapas | vigente | todos os mapas derivados |
| [`docs/uml/README.md`](../uml/README.md) | catálogo de representações visuais | vigente | `docs/uml/**/*.puml` |
| [`docs/templates/epic.md`](../templates/epic.md) | template de referência de Epic | vigente como referência | fluxo do Project; não é formulário nativo |
| [`docs/templates/issue-slice.md`](../templates/issue-slice.md) | template de referência de slice | vigente como referência | fluxo do Project; não é formulário nativo |
| [`docs/templates/sub-issue.md`](../templates/sub-issue.md) | template de referência de sub-issue | vigente como referência | fluxo do Project; não é formulário nativo |
| [`docs/templates/pr.md`](../templates/pr.md) | template de referência de PR | vigente como referência | estratégia Git; não é template nativo |

## Regras de manutenção

- atualizar quando documento canônico, ADR ou classe documental surgir;
- manter links clicáveis e relativos ao repositório;
- preservar qualificadores `proposto`, `planejado` e `não implementado`;
- não listar rota, tabela, módulo ou serviço como real antes de código/testes e Issue/PR correspondentes;
- registrar no [Status do projeto](../PROJECT_STATUS.md) apenas estado corrente, não repetir nele todo o conteúdo deste mapa;
- registrar a Issue/PR que altera uma fonte primária.
