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
    └── ADR-0021 — Ownership do shared-dev e worktrees [ACEITO]
        ├── app-host — owner exato /srv/apps/erp-docflow
        ├── personal-wsl — owner configurado; default ~/projetos/erp-docflow
        ├── worktrees — check/rehearsal descartáveis
        └── shared-dev — identidade, migration e rollback controlados

ADR-0001 — On-prem first
└── ADR-0014 — Backup e restore obrigatórios
```

ADR-0021 complementa os perfis do ADR-0004 e o Compose do ADR-0008 sem
substituí-los. O runtime legado ainda nasce da worktree `phase1-reproduction`;
aceitar a decisão não aplica o cutover. A futura implementação deverá provar
owner por realpath, `main` sincronizada, labels, mounts, source SHA, configuração
não secreta e health. Worktrees não controlam o runtime cumulativo.

## Arquitetura de produto

```text
ADR-0001 — On-prem first
└── ADR-0009 — Modular monolith
    ├── ADR-0010 — PostgreSQL
    ├── ADR-0011 — Object storage S3-compatible
    │   └── ADR-0019 — MinIO no protótipo local sintético [ACEITO COM REVISÃO]
    └── ADR-0012 — DocumentEnvelope
        └── ADR-0013 — Review, acceptance e override
```

ADR-0019 complementa a direção S3-compatible com uma exceção temporária para
MinIO OSS single-node, isolado e com dados sintéticos. Commit, patchset,
toolchain, digests, SBOM, scans e provas de runtime permanecem evidências da
#40; ampliar ambiente, classe de dados ou distribuição exige nova revisão.

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
│   └── ADR-0020 — Ruleset da main em dois cutovers [ACEITO]
│       ├── Cutover A — checks existentes; aprovações formais = 0
│       └── Cutover B — Evaluation + Documentation; aprovação = 1 quando houver segundo Write+
└── ADR-0017 — Loop contínuo de slices pelo Codex
    ├── complementa ADR-0005 — autonomia alta controlada
    └── ADR-0018 — Lifecycle do envelope e outcomes exclusivos

ADR-0013 — Review, acceptance e override
└── ADR-0015 — Auth, autorização e segurança [PROPOSTO / GATE]
```

ADR-0020 complementa a ordem definida pelo ADR-0007 com um ruleset
`main-governance`, squash-only, checks estritos e conversas resolvidas. O
Cutover A mantém zero aprovações formais enquanto só existe o autor; o Cutover B
exige uma aprovação quando houver segundo colaborador Write+. Aceitar o ADR não
aplica o ruleset.

ADR-0017 coordena seleção e continuidade do trabalho. ADR-0018 o complementa
com estados, evidência, outcomes exclusivos e condições de retomada. Nenhum
deles autoriza merge automático.

## Regras de manutenção

- atualizar quando ADR criar, substituir, complementar ou obsoletar decisão;
- não justificar implementação sem consultar status e condições do ADR;
- não tratar diagrama ou review de chat como decisão superior ao ADR;
- decisões `Proposto` não orientam implementação obrigatória.
