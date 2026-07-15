# UML

Esta pasta armazena diagramas operacionais da Phase 0 e diagramas de produto **planejado/não implementado**.

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
| [codex-continuous-slice-loop.puml](02-business/codex-continuous-slice-loop.puml) | Plan aprova envelope; Codex puxa slices e pede checkpoint em fronteiras reais |

### Produto planejado — Issue #22

| Diagrama | Tipo | Decisão/fluxo representado |
| --- | --- | --- |
| [erp-docflow-system-context-planned.puml](01-context/erp-docflow-system-context-planned.puml) | contexto | atores, entradas, providers e integrações |
| [onprem-deployment-planned.puml](01-context/onprem-deployment-planned.puml) | deployment | destino on-prem com API, workers, dados e providers |
| [document-processing-activity-planned.puml](02-business/document-processing-activity-planned.puml) | atividade | intake → processamento → review → efeito |
| [document-processing-components-planned.puml](03-application/document-processing-components-planned.puml) | componentes | boundaries lógicos no modular monolith |
| [document-processing-domain-planned.puml](04-domain/document-processing-domain-planned.puml) | domínio | envelope, versões, tentativas, resultados e decisões |
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

- [Arquitetura](../ARCHITECTURE.md)
- [Pipeline](../DOCUMENT_PIPELINE.md)
- [Baseline de dados](../DATA_MODEL_BASELINE.md)
- [Estratégia de providers](../PROVIDER_STRATEGY.md)
- [Glossário](../GLOSSARIO_DOCUMENTAL.md)
