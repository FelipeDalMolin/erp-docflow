# Document Map

Mapa entre documentos, ADRs, diagramas e fases. Registra vínculos documentais; não cria contratos de implementação.

| Documento | Papel | ADRs | UMLs/artefatos relacionados | Fase |
| --- | --- | --- | --- | --- |
| `AGENTS.md` | operação do Codex e guardrails | ADR-0002, 0005, 0015 | — | 0 |
| `.codex/config.toml` | configuração operacional Codex | ADR-0005 | — | 0 |
| `docs/MODELO_OPERACIONAL_DO_PROJETO.md` | governança e forma de trabalho | ADR-0001 a 0015 conforme seção | contexto operacional | 0 |
| `docs/ROADMAP.md` | fases, gates e resultados | ADR-0001, 0002, 0007–0016 | todos os planejados | 0–7 |
| `docs/ARCHITECTURE.md` | arquitetura lógica, boundaries, dados e operação | ADR-0001, 0008–0016 | contexto, deployment, componentes | 0 / destino |
| `docs/DOCUMENT_PIPELINE.md` | fluxo canônico e gates | ADR-0012, 0013, 0016 | atividade, sequências, estados | 0 / fases 2–5 |
| `docs/PROVIDER_STRATEGY.md` | capabilities, adapters, routing e benchmark | ADR-0016 | componentes e sequência de processamento | 0 / fase 3 |
| `docs/DATA_MODEL_BASELINE.md` | conceitos e invariantes, sem schema físico | ADR-0010–0013, 0015, 0016 | domínio e estados | 0 / fases 2–5 |
| `docs/GLOSSARIO_DOCUMENTAL.md` | vocabulário canônico | ADR-0012, 0013, 0016 | todos os diagramas de produto | 0 |
| `docs/reviews/GESTAO_DOCUMENTAL_INTELIGENTE.md` | origem, decisões, contradições e perguntas | ADR-0001, 0009–0016 | catálogo UML | 0 |
| `docs/AMBIENTES.md` | local, CI, on-prem, backup | ADR-0001, 0004, 0007, 0008, 0010, 0011, 0014 | deployment planejado | 0–produção |
| `docs/adr/README.md` | governança de decisões | ADR-0006 | — | 0 |
| `docs/adr/0016-capability-based-document-processing-providers.md` | proposta de providers por capability | ADR-0016 | componentes/processamento | 0 / fase 3 |
| `docs/traceability/README.md` | regras dos mapas | ADR-0006 | — | 0 |
| `docs/uml/README.md` | catálogo e status dos diagramas | ADR-0006, 0012, 0013, 0016 | `docs/uml/**/*.puml` | 0 / destino |

## Regras de manutenção

- atualizar quando documento canônico ou ADR surgir;
- ligar documento a UML apenas quando representarem o mesmo conceito;
- preservar status “planejado” enquanto não houver implementação;
- não listar rota, tabela ou módulo como real antes do código correspondente;
- registrar Issue/PR que altera fonte canônica.

