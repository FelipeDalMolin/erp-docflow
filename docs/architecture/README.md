# Arquitetura e domínio documental

Este diretório reúne **baselines planejados do produto**. Esses documentos explicam o desenho de destino, mas não provam implementação nem substituem ADRs.

| Documento | Responsabilidade exclusiva |
| --- | --- |
| [Arquitetura](ARCHITECTURE.md) | boundaries, componentes e visão lógica |
| [Pipeline documental](DOCUMENT_PIPELINE.md) | etapas, gates e artefatos do processamento |
| [Baseline de dados](DATA_MODEL_BASELINE.md) | conceitos e invariantes, sem schema físico |
| [Estratégia de providers](PROVIDER_STRATEGY.md) | capabilities, adapters e critérios de seleção |
| [Contrato de processing profile](PROCESSING_PROFILE_CONTRACT.md) | profile, task graph, rules, routing, fixtures e promoção |
| [Pipeline de importação estruturada](STRUCTURED_IMPORT_PIPELINE.md) | XLSX/CSV, mapping, raw/normalized row, validação e replay |
| [Domínio financeiro-gerencial](MANAGERIAL_FINANCIAL_DOMAIN.md) | fatos multiorigem, obrigações, settlements e reconciliação |
| [Lineage de evidência a relatório](EVIDENCE_TO_REPORT_LINEAGE.md) | `EvidenceRef`, drill-through, coverage e read models |
| [Fechamento e entrega contábil](ACCOUNTING_CLOSE_AND_DELIVERY.md) | `PeriodClose`, pacote, protocolo e relação com a release |
| [Glossário](GLOSSARIO_DOCUMENTAL.md) | vocabulário canônico do domínio |

O resultado desejado permanece em [`product/`](../product/README.md). Em divergência, verificar o status do ADR aplicável em [`adr/`](../adr/README.md). UML é representação visual derivada; código e testes serão a evidência quando houver implementação.
