# erp-docflow

Plataforma ERP/GED **on-prem first**, com arquitetura **cloud-like**, para materialização documental, versionamento, processamento assistido, revisão, aceite, auditoria e fluxos financeiros.

Status atual: **Phase 0 encerrada; Phase 1 aberta em refinamento, ainda sem execução de código autorizada**. Não há código de produto implementado.

Consulte o [status do projeto](docs/PROJECT_STATUS.md) para o gate ativo e o [portal da documentação](docs/README.md) para escolher a fonte correta.

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

| Entrada | Finalidade |
| --- | --- |
| [Portal da documentação](docs/README.md) | trilhas de leitura, matriz de autoridade, classes e manutenção |
| [Status do projeto](docs/PROJECT_STATUS.md) | fase atual, evidências, gate e fila candidata |
| [Roadmap](docs/ROADMAP.md) | escopo permanente, dependências e resultados das fases |
| [Arquitetura](docs/ARCHITECTURE.md) | visão lógica planejada, boundaries e dados |
| [ADRs](docs/adr/README.md) | decisões arquiteturais e seus status |
| [Rastreabilidade](docs/traceability/README.md) | relações derivadas entre decisões e artefatos |

## Guardrails

- não trabalhar diretamente na `main`;
- seguir Issue → branch → PR → CI → revisão humana → squash merge;
- permitir que o Codex puxe o próximo slice pronto dentro de envelope aprovado, sem nova autorização mecânica;
- não iniciar a Phase 1 apenas porque sua Epic está aberta: a slice deve estar especificada, com condições verificadas e dentro de envelope aprovado;
- não transformar proposta ou diagrama planejado em contrato implementado;
- não alterar ADR aceito como documento vivo;
- não usar dados reais, secrets ou providers externos sem decisão e controles aplicáveis.

O fim de um slice não é, sozinho, um gate. Mudança de direção, risco, dependência ou área protegida exige checkpoint; merge permanece humano.

Consulte [AGENTS.md](AGENTS.md) antes de executar uma Issue com Codex. O `README` apresenta o projeto; ele não substitui a fonte especializada de cada regra.
