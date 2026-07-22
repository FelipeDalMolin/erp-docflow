# UML

Esta pasta armazena diagramas operacionais da Phase 0 e diagramas de produto **planejado/não implementado**. A Issue #73 ampliou o contexto de documento para evidência → fato gerencial → relatório/fechamento e distinguiu desenvolvimento do piloto on-prem; #88/#89 acrescentam lifecycle reproduzível e estrutura/layout por provider.

## 1. Regra de leitura

Cada diagrama deve declarar no cabeçalho:

- Issue de origem;
- ADRs relacionados;
- guardrail de status.

`planned` representa arquitetura, domínio ou fluxo candidato para revisão. Não define API, tabela, módulo implementado ou autorização para código de produto.

## 2. Estrutura

```text
docs/uml/
├── 01-context/
├── 02-business/
├── 03-application/
├── 04-domain/
├── 05-sequence/
└── 06-state/
```

## 3. Catálogo atual

### Phase 0 — operação do projeto

| Diagrama | Escopo |
| --- | --- |
| [project-context.puml](01-context/project-context.puml) | contexto operacional de Issue, GitHub, VS Code, Codex e documentação |
| [documentation-governance-components.puml](03-application/documentation-governance-components.puml) | componentes documentais da governança |
| [phase-0-delivery-flow.puml](02-business/phase-0-delivery-flow.puml) | lifecycle Issue → branch → PR → review → merge, originado na Phase 0 |
| [local-dev-environment.puml](03-application/local-dev-environment.puml) | ambiente local atual e integrações planejadas |
| [codex-continuous-slice-loop.puml](02-business/codex-continuous-slice-loop.puml) | lifecycle do envelope, outcomes exclusivos, retomada e separação entre draft, Review e Done |

### Produto planejado — Issues #22, #73, #88 e #89

| Diagrama | Tipo | Decisão/fluxo representado |
| --- | --- | --- |
| [erp-docflow-system-context-planned.puml](01-context/erp-docflow-system-context-planned.puml) | contexto | entradas documentais, estruturadas e manuais; fato gerencial, contador e integrações |
| [onprem-deployment-planned.puml](01-context/onprem-deployment-planned.puml) | deployment | Compose versus bundle; profiles core/Tika/OCR/Docling opcionais e isolados |
| [document-processing-activity-planned.puml](02-business/document-processing-activity-planned.puml) | atividade | evidência documental/estruturada/manual, texto/estrutura, review, fato e fechamento |
| [document-processing-components-planned.puml](03-application/document-processing-components-planned.puml) | componentes | intake/importação, evaluation, providers por capability, lineage, núcleo gerencial e entrega |
| [document-processing-domain-planned.puml](04-domain/document-processing-domain-planned.puml) | domínio | envelope, invocation/execution, artifacts textuais/estruturais, benchmark e promoção |
| [ingest-to-envelope-planned.puml](05-sequence/ingest-to-envelope-planned.puml) | sequência | materialização documental |
| [process-review-accept-planned.puml](05-sequence/process-review-accept-planned.puml) | sequência | provider, validação, revisão e aceite |
| [document-envelope-state-planned.puml](06-state/document-envelope-state-planned.puml) | estados | ciclo candidato do envelope |
| [processing-job-state-planned.puml](06-state/processing-job-state-planned.puml) | estados | ciclo candidato de job e retry |

## 4. Tipos previstos

- contexto e deployment;
- casos de uso e atividades;
- componentes;
- classes/conceitos de domínio;
- sequência;
- estados.

Novos diagramas devem responder uma pergunta concreta e evitar duplicar texto sem ganho visual.

## 5. Relação com ADRs e rastreabilidade

Diagramas não criam decisão. A decisão primária permanece no ADR aplicável.

Quando um fluxo, estado ou boundary mudar:

1. verificar se exige novo ADR;
2. atualizar documento canônico;
3. atualizar diagrama;
4. atualizar `docs/traceability/`;
5. registrar Issue/PR que introduziu a mudança.

## 6. Formato e validação

PlantUML é o formato preferencial neste baseline.

Antes do merge:

- verificar `@startuml` e `@enduml`;
- renderizar quando a ferramenta estiver disponível;
- revisar relações, nomes e legibilidade;
- confirmar que o status planejado/implementado está correto;
- conferir links no catálogo.

## 7. Documentos relacionados

- [North star do produto](../product/PRODUCT_NORTH_STAR.md)
- [Piloto vertical R1](../product/PILOT_VERTICAL_SLICE.md)
- [Jornadas e UX](../product/USER_JOURNEYS_AND_UX.md)
- [Entrega e aceite](../product/PRODUCT_DELIVERY_AND_ACCEPTANCE.md)
- [Arquitetura](../architecture/ARCHITECTURE.md)
- [Pipeline](../architecture/DOCUMENT_PIPELINE.md)
- [Baseline de dados](../architecture/DATA_MODEL_BASELINE.md)
- [Estratégia de providers](../architecture/PROVIDER_STRATEGY.md)
- [Contrato de perfil de processamento](../architecture/PROCESSING_PROFILE_CONTRACT.md)
- [Engenharia de experimentos e componentes de dados](../architecture/DATA_SCIENCE_ENGINEERING_LIFECYCLE.md)
- [Importação estruturada](../architecture/STRUCTURED_IMPORT_PIPELINE.md)
- [Domínio gerencial](../architecture/MANAGERIAL_FINANCIAL_DOMAIN.md)
- [Linhagem evidência → relatório](../architecture/EVIDENCE_TO_REPORT_LINEAGE.md)
- [Fechamento e entrega contábil](../architecture/ACCOUNTING_CLOSE_AND_DELIVERY.md)
- [Glossário](../architecture/GLOSSARIO_DOCUMENTAL.md)
