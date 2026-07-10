# erp-docflow

Plataforma ERP/GED **on-prem first**, com arquitetura **cloud-like**, para materialização documental, versionamento, processamento assistido, revisão, aceite, auditoria e fluxos financeiros.

Status atual: **Phase 0 — sistema do projeto e arquitetura documental**. Não há código de produto implementado.

## Visão do fluxo

```text
entrada
  -> DocumentEnvelope + original versionado
  -> probe / normalização / OCR
  -> extração / classificação / validação
  -> revisão humana e aceite
  -> vínculos e efeitos operacionais autorizados
  -> auditoria, busca e integrações
```

## Documentação principal

| Documento | Finalidade |
| --- | --- |
| [Modelo operacional](docs/MODELO_OPERACIONAL_DO_PROJETO.md) | governança, fases e forma de trabalho |
| [Roadmap](docs/ROADMAP.md) | evolução incremental da Phase 0 às integrações |
| [Arquitetura](docs/ARCHITECTURE.md) | visão lógica, boundaries e dados |
| [Pipeline documental](docs/DOCUMENT_PIPELINE.md) | fluxo canônico, gates e artefatos |
| [Estratégia de providers](docs/PROVIDER_STRATEGY.md) | capabilities, adapters, roteamento e benchmark |
| [Baseline de dados](docs/DATA_MODEL_BASELINE.md) | conceitos e invariantes, sem schema físico |
| [Glossário documental](docs/GLOSSARIO_DOCUMENTAL.md) | terminologia canônica |
| [Revisão do chat](docs/reviews/GESTAO_DOCUMENTAL_INTELIGENTE.md) | decisões, contradições e perguntas abertas |
| [ADRs](docs/adr/README.md) | decisões arquiteturais e seus status |
| [Rastreabilidade](docs/traceability/README.md) | relações entre decisões e artefatos |
| [UML](docs/uml/README.md) | catálogo de diagramas operacionais e planejados |

## Guardrails

- não trabalhar diretamente na `main`;
- seguir Issue → branch → PR → CI → revisão humana → squash merge;
- permitir que o Codex puxe o próximo slice pronto dentro de envelope aprovado, sem nova autorização mecânica;
- não iniciar código de produto antes dos critérios da Phase 0;
- não transformar proposta ou diagrama planejado em contrato implementado;
- não alterar ADR aceito como documento vivo;
- não usar dados reais, secrets ou providers externos sem decisão e controles aplicáveis.

O fim de um slice não é, sozinho, um gate. Mudança de direção, risco, dependência ou área protegida exige checkpoint; merge permanece humano.

Consulte [AGENTS.md](AGENTS.md) antes de executar uma Issue com Codex.

