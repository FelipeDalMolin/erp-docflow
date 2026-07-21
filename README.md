# erp-docflow

Plataforma ERP/GED **on-prem first**, com arquitetura **cloud-like**, para transformar fontes heterogêneas em informação gerencial auditável, preservando evidências, revisão, aceite, fechamento e operação documental.

Status atual: **Phase 0 encerrada; Phase 1 autorizada para execução controlada**. A #33 está preparada no [PR #72](https://github.com/FelipeDalMolin/erp-docflow/pull/72), aguardando review e squash merge humanos; ainda não há código de produto integrado à `main`.

Consulte o [status do projeto](docs/project/PROJECT_STATUS.md) para o gate ativo e o [portal da documentação](docs/README.md) para escolher a fonte correta.

## Visão do fluxo

```text
fonte documental, estruturada, manual ou integrada
  -> conteúdo bruto e origem preservados
  -> interpretação candidata + evidências
  -> validação e revisão proporcional ao risco
  -> fato gerencial ou vínculo autorizado
  -> relatório com drill-through
  -> fechamento, pacote e auditoria
```

## Documentação principal

| Entrada | Finalidade |
| --- | --- |
| [Portal da documentação](docs/README.md) | trilhas de leitura, matriz de autoridade, classes e manutenção |
| [Direção do produto](docs/product/README.md) | north star, piloto Golden Month, jornadas e critérios de entrega |
| [Status do projeto](docs/project/PROJECT_STATUS.md) | fase atual, evidências, gate e fila candidata |
| [Roadmap](docs/project/ROADMAP.md) | escopo permanente, dependências e resultados das fases |
| [Arquitetura](docs/architecture/ARCHITECTURE.md) | visão lógica planejada, boundaries e dados |
| [ADRs](docs/adr/README.md) | decisões arquiteturais e seus status |
| [Rastreabilidade](docs/traceability/README.md) | relações derivadas entre decisões e artefatos |

## Guardrails

- não trabalhar diretamente na `main`;
- seguir Issue → branch → PR → CI → revisão humana → squash merge;
- permitir que o Codex puxe o próximo slice pronto dentro de envelope aprovado, sem nova autorização mecânica;
- não iniciar uma slice apenas porque sua Phase, release ou Epic está aberta: a slice deve estar especificada, com condições verificadas e dentro de envelope aprovado;
- não transformar proposta ou diagrama planejado em contrato implementado;
- não alterar ADR aceito como documento vivo;
- não usar dados reais, secrets ou providers externos sem decisão e controles aplicáveis.

O fim de um slice não é, sozinho, um gate. Mudança de direção, risco, dependência ou área protegida exige checkpoint; merge permanece humano.

Consulte [AGENTS.md](AGENTS.md) antes de executar uma Issue com Codex. O `README` apresenta o projeto; ele não substitui a fonte especializada de cada regra.
