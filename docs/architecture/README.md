# Arquitetura e domínio documental

Este diretório reúne **baselines planejados do produto**. Esses documentos explicam o desenho de destino, mas não provam implementação nem substituem ADRs.

| Documento | Responsabilidade exclusiva |
| --- | --- |
| [Arquitetura](ARCHITECTURE.md) | boundaries, componentes e visão lógica |
| [Pipeline documental](DOCUMENT_PIPELINE.md) | etapas, gates e artefatos do processamento |
| [Baseline de dados](DATA_MODEL_BASELINE.md) | conceitos e invariantes, sem schema físico |
| [Estratégia de providers](PROVIDER_STRATEGY.md) | capabilities, adapters e critérios de seleção |
| [Glossário](GLOSSARIO_DOCUMENTAL.md) | vocabulário canônico do domínio |

Em divergência, verificar o status do ADR aplicável em [`adr/`](../adr/README.md). UML é representação visual derivada; código e testes serão a evidência quando houver implementação.
