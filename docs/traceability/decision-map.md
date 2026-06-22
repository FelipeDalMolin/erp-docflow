# Decision Map

Mapa inicial de relações entre decisões registradas nos ADRs.

Este arquivo não cria decisões novas. A fonte primária continua sendo `docs/adr/`.

## Fundação operacional

```text
ADR-0001 — On-prem first com práticas cloud-like
└── ADR-0002 — Phase 0 antes de código de produto
    ├── ADR-0003 — Fluxo Git por Issue, branch, PR e revisão
    ├── ADR-0005 — Uso controlado do Codex
    └── ADR-0006 — Governança de ADRs e rastreabilidade
```

## Ambiente local

```text
ADR-0004 — Desenvolvimento local com Windows, WSL e VS Code
├── ADR-0005 — Uso controlado do Codex
└── ADR-0008 — Docker Compose para local e onprem-lab
```

## Governança e operação futura

```text
ADR-0003 — Fluxo Git por Issue, branch, PR e revisão
└── ADR-0007 — CI estrutural antes de branch protection

ADR-0001 — On-prem first com práticas cloud-like
└── ADR-0014 — Backup e restore obrigatórios

ADR-0013 — Revisão humana, aceite e override
└── ADR-0015 — Estratégia futura de autenticação, autorização e segurança
```

## Arquitetura de destino

```text
ADR-0001 — On-prem first com práticas cloud-like
└── ADR-0009 — Arquitetura inicial como modular monolith
    ├── ADR-0012 — DocumentEnvelope como núcleo GED
    │   ├── ADR-0010 — PostgreSQL como banco relacional principal
    │   ├── ADR-0011 — Object storage S3-compatible
    │   └── ADR-0013 — Revisão humana, aceite e override
    └── ADR-0008 — Docker Compose para local e onprem-lab
```

## Regras de manutenção

- Atualizar este mapa quando um ADR criar, substituir, complementar ou obsoletar uma decisão.
- Não usar este mapa para justificar implementação sem consultar o ADR correspondente.
- Decisões com status `Proposto` não devem orientar implementação obrigatória.
