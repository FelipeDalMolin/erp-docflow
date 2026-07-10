# Decision Map

Mapa de relações entre decisões registradas nos ADRs. A fonte primária continua sendo `docs/adr/`.

## Fundação operacional

```text
ADR-0001 — On-prem first com práticas cloud-like
└── ADR-0002 — Phase 0 antes de código de produto
    ├── ADR-0003 — Fluxo Git por Issue, branch, PR e revisão
    ├── ADR-0005 — Uso controlado do Codex
    └── ADR-0006 — Governança de ADRs e rastreabilidade
```

## Ambiente e operação

```text
ADR-0004 — Desenvolvimento local com Windows, WSL e VS Code
├── ADR-0005 — Uso controlado do Codex
└── ADR-0008 — Docker Compose para local e onprem-lab

ADR-0001 — On-prem first
└── ADR-0014 — Backup e restore obrigatórios
```

## Arquitetura de produto

```text
ADR-0001 — On-prem first
└── ADR-0009 — Modular monolith
    ├── ADR-0010 — PostgreSQL
    ├── ADR-0011 — Object storage S3-compatible
    └── ADR-0012 — DocumentEnvelope
        └── ADR-0013 — Review, acceptance e override
```

## Processamento documental proposto

```text
ADR-0012 — DocumentEnvelope
├── ADR-0013 — Review, acceptance e override
└── ADR-0016 — Capabilities e providers [PROPOSTO]
    ├── complementa ADR-0001 — local first / cloud-like
    ├── opera dentro de ADR-0009 — modular monolith
    ├── depende de ADR-0015 — segurança e elegibilidade
    └── relaciona ADR-0010/0011/0014 — dados e operação
```

ADR-0016 não altera ADR aceito e não autoriza provider real enquanto estiver `Proposto`.

## Governança e segurança

```text
ADR-0003 — Fluxo Git/PR/revisão
├── ADR-0007 — CI antes de branch protection
└── ADR-0017 — Loop contínuo de slices pelo Codex
    └── complementa ADR-0005 — autonomia alta controlada

ADR-0013 — Review, acceptance e override
└── ADR-0015 — Auth, autorização e segurança [PROPOSTO / GATE]
```

ADR-0017 coordena seleção e continuidade do trabalho. Ele não altera a revisão humana nem autoriza merge automático.

## Regras de manutenção

- atualizar quando ADR criar, substituir, complementar ou obsoletar decisão;
- não justificar implementação sem consultar status e condições do ADR;
- não tratar diagrama ou review de chat como decisão superior ao ADR;
- decisões `Proposto` não orientam implementação obrigatória.

