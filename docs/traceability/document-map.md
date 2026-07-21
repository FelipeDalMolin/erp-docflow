# Document Map

Mapa derivado entre fontes documentais, autoridade, status e artefatos relacionados. Ele ajuda a localizar a fonte correta; não cria decisões nem contratos de implementação.

| Documento | Classe / autoridade | Estado | Relações principais |
| --- | --- | --- | --- |
| [`README.md`](../../README.md) | entrada curta do repositório | vigente | portal e status |
| [`docs/README.md`](../README.md) | portal e matriz de autoridade | vigente | todos os grupos documentais |
| [`docs/project/README.md`](../project/README.md) | índice de projeto e governança | vigente | status, roadmap e modelo operacional |
| [`docs/architecture/README.md`](../architecture/README.md) | índice de arquitetura e domínio | vigente | arquitetura, pipeline, dados, providers e glossário |
| [`docs/operations/README.md`](../operations/README.md) | índice de operação e execução | vigente | ambientes, Git, Project e runbook |
| [`docs/project/PROJECT_STATUS.md`](../project/PROJECT_STATUS.md) | snapshot de fase, gate e fila | vigente | Issues #1, #26, #33–#37 e #73; PR #72 |
| [`AGENTS.md`](../../AGENTS.md) | guardrails executáveis do Codex | vigente | ADR-0003, 0005, 0017 e 0018 |
| [`.codex/config.toml`](../../.codex/config.toml) | capacidade técnica local do Codex | vigente | ADR-0005; não concede escopo |
| [`docs/project/MODELO_OPERACIONAL_DO_PROJETO.md`](../project/MODELO_OPERACIONAL_DO_PROJETO.md) | princípios de governança | vigente | ADR-0001–0018 conforme tema |
| [`docs/operations/FLUXO_GITHUB_PROJECT.md`](../operations/FLUXO_GITHUB_PROJECT.md) | lifecycle, prontidão, modos e outcomes | vigente | ADR-0003, 0005, 0017 e 0018 |
| [`docs/operations/ESTRATEGIA_GIT.md`](../operations/ESTRATEGIA_GIT.md) | branches, commits, PRs e merge | vigente | ADR-0003, 0005, 0017 e 0018 |
| [`docs/operations/FLUXO_VSCODE_GIT_GITHUB_CLI.md`](../operations/FLUXO_VSCODE_GIT_GITHUB_CLI.md) | runbook local/CLI | vigente | estratégia Git e ADR-0004 |
| [`docs/operations/AMBIENTES.md`](../operations/AMBIENTES.md) | ambientes atuais e planejados | vigente/planejado | ADR-0001, 0004, 0007, 0008 e 0014 |
| [`docs/operations/WSL_MULTI_PROJETOS.md`](../operations/WSL_MULTI_PROJETOS.md) | runbook WSL detalhado | vigente | ADR-0004 e ambientes |
| [`docs/project/ROADMAP.md`](../project/ROADMAP.md) | releases, capabilities, dependências, resultados e gates | vigente | Epics #1, #26–#32 e #75; Issues #74–#86 |
| [`docs/product/README.md`](../product/README.md) | índice canônico de produto | planejado/não implementado | north star, piloto R1, UX e entrega |
| [`docs/product/PRODUCT_NORTH_STAR.md`](../product/PRODUCT_NORTH_STAR.md) | direção de produto e invariantes de valor | planejado/não implementado | fato gerencial sustentado por evidência; #73/#74 |
| [`docs/product/PILOT_VERTICAL_SLICE.md`](../product/PILOT_VERTICAL_SLICE.md) | contrato do piloto R1 Golden Month | planejado/não implementado | import-first, fechamento mensal e aceite; Epic #75 |
| [`docs/product/USER_JOURNEYS_AND_UX.md`](../product/USER_JOURNEYS_AND_UX.md) | jornadas e UX mínima do produto | planejado/não implementado | importação, review, livro, relatórios, dossiê e fechamento; #76 |
| [`docs/product/PRODUCT_DELIVERY_AND_ACCEPTANCE.md`](../product/PRODUCT_DELIVERY_AND_ACCEPTANCE.md) | critérios de entrega e aceite | planejado/não implementado | `AccountingDeliveryPackage` (#79) e `ProductReleaseBundle` (#81) |
| [`docs/architecture/ARCHITECTURE.md`](../architecture/ARCHITECTURE.md) | arquitetura lógica de referência | planejado/não implementado | ADR-0001, 0008–0014; ADR-0015/0016 propostos; UML de contexto/componentes |
| [`docs/architecture/DOCUMENT_PIPELINE.md`](../architecture/DOCUMENT_PIPELINE.md) | fluxo documental canônico | planejado/não implementado | ADR-0012, 0013 e 0016 proposto |
| [`docs/architecture/PROVIDER_STRATEGY.md`](../architecture/PROVIDER_STRATEGY.md) | capabilities, adapters e benchmark | proposta de descoberta | ADR-0016 proposto |
| [`docs/architecture/DATA_MODEL_BASELINE.md`](../architecture/DATA_MODEL_BASELINE.md) | conceitos e invariantes, sem schema físico | planejado/não implementado | ADR-0010–0013; ADR-0015/0016 propostos |
| [`docs/architecture/GLOSSARIO_DOCUMENTAL.md`](../architecture/GLOSSARIO_DOCUMENTAL.md) | vocabulário canônico | vigente | arquitetura, pipeline e dados |
| [`docs/architecture/PROCESSING_PROFILE_CONTRACT.md`](../architecture/PROCESSING_PROFILE_CONTRACT.md) | contrato de perfil, algoritmos, métricas e routing | planejado/não implementado | Tika/OCR/rules/assessment/routing #82–#86; ADR-0016 proposto |
| [`docs/architecture/STRUCTURED_IMPORT_PIPELINE.md`](../architecture/STRUCTURED_IMPORT_PIPELINE.md) | pipeline local de XLSX/CSV e mapeamentos | planejado/não implementado | piloto #75/#77 e proveniência por lote/linha |
| [`docs/architecture/MANAGERIAL_FINANCIAL_DOMAIN.md`](../architecture/MANAGERIAL_FINANCIAL_DOMAIN.md) | domínio gerencial e financeiro | planejado/não implementado | decisão #74; fatos, obrigações, liquidações, conciliação e rateios |
| [`docs/architecture/EVIDENCE_TO_REPORT_LINEAGE.md`](../architecture/EVIDENCE_TO_REPORT_LINEAGE.md) | linhagem evidência → fato → relatório | planejado/não implementado | drill-through e read models #78; autoridade #80 |
| [`docs/architecture/ACCOUNTING_CLOSE_AND_DELIVERY.md`](../architecture/ACCOUNTING_CLOSE_AND_DELIVERY.md) | fechamento e entrega contábil | planejado/não implementado | `PeriodClose` e pacote/protocolo #79/#80 |
| [`docs/reviews/GESTAO_DOCUMENTAL_INTELIGENTE.md`](../reviews/GESTAO_DOCUMENTAL_INTELIGENTE.md) | evidência histórica de descoberta | histórico | Issue #22; não é fonte normativa |
| [`docs/reviews/DOCUMENTATION_COHERENCE_2026-07.md`](../reviews/DOCUMENTATION_COHERENCE_2026-07.md) | evidência da auditoria documental | histórico | Issue #69; conflitos, redundâncias e lacunas |
| [`docs/adr/README.md`](../adr/README.md) | governança e catálogo de decisões | vigente | ADR-0001–0018 |
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
- registrar no [Status do projeto](../project/PROJECT_STATUS.md) apenas estado corrente, não repetir nele todo o conteúdo deste mapa;
- registrar a Issue/PR que altera uma fonte primária.
