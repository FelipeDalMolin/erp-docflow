# ADR Index

Lista dos ADRs existentes. Este mapa reflete decisões registradas em `docs/adr/`; não cria decisões nem autoriza implementação fora da fase correspondente.

| ADR | Título | Status | Data | Decisão curta | Relações principais | Revisão futura |
| --- | --- | --- | --- | --- | --- | --- |
| [ADR-0001](../adr/0001-on-prem-first-cloud-like.md) | On-prem first com práticas cloud-like | Aceito | 2026-06-22 | Operação principal local com práticas cloud-like. | ADR-0002, ADR-0014 | Se cloud/híbrido virar prioridade principal. |
| [ADR-0002](../adr/0002-phase-0-before-product-code.md) | Phase 0 antes de código de produto | Aceito | 2026-06-22 | Phase 0 mínima antes de código de produto. | ADR-0001, ADR-0003, ADR-0005, ADR-0006 | Ao iniciar Phase 1. |
| [ADR-0003](../adr/0003-git-flow-issue-branch-pr-review.md) | Fluxo Git por Issue, branch, PR e revisão | Aceito | 2026-06-22 | Issue → branch → PR → revisão humana → squash merge. | ADR-0002, ADR-0005, ADR-0007 | Se volume/maturidade exigir outro fluxo. |
| [ADR-0004](../adr/0004-local-dev-windows-wsl-vscode.md) | Desenvolvimento local com Windows, WSL e VS Code | Aceito | 2026-06-22 | Windows host + Ubuntu-20.04 WSL + VS Code em WSL. | ADR-0002, ADR-0005, ADR-0008 | Migração WSL ou onprem-lab próprio. |
| [ADR-0005](../adr/0005-controlled-codex-usage.md) | Uso controlado do Codex | Aceito | 2026-06-22 | Codex controlado por Issue, branch, PR e revisão humana. | ADR-0003, ADR-0004, ADR-0006 | Mudança no uso/configuração Codex. |
| [ADR-0006](../adr/0006-adr-and-traceability-governance.md) | Governança de ADRs e rastreabilidade | Aceito | 2026-06-22 | Decisões relevantes viram ADR; mapas mantêm rastreabilidade. | Todos os ADRs | Ao alterar mapas ou regra de ADR. |
| [ADR-0007](../adr/0007-structural-ci-and-branch-protection.md) | CI estrutural antes de branch protection | Aceito com revisão | 2026-06-22 | CI estrutural vem antes de branch protection. | ADR-0002, ADR-0003 | Reavaliado na #37; revisar novamente antes de branch protection. |
| [ADR-0008](../adr/0008-docker-compose-for-local-and-onprem-lab.md) | Docker Compose para local e onprem-lab | Aceito com revisão | 2026-06-22 | Compose como direção futura para local/onprem-lab. | ADR-0004, ADR-0010, ADR-0011, ADR-0014 | Compose local reavaliado na #36/#37; onprem-lab permanece pendente. |
| [ADR-0009](../adr/0009-modular-monolith-initial-architecture.md) | Arquitetura inicial como modular monolith | Aceito com revisão | 2026-06-22 | Modular monolith como direção inicial. | ADR-0001, ADR-0012, ADR-0013, ADR-0016 | Bootstrap reavaliado na #37; revisar após os primeiros módulos de produto. |
| [ADR-0010](../adr/0010-postgresql-primary-relational-database.md) | PostgreSQL como banco relacional principal | Aceito com revisão | 2026-06-22 | PostgreSQL como direção inicial de banco. | ADR-0001, ADR-0008, ADR-0012, ADR-0014 | Antes de schema/migrations. |
| [ADR-0011](../adr/0011-s3-compatible-object-storage-minio.md) | Object storage S3-compatible | Aceito com revisão | 2026-06-22 | S3-compatible; MinIO candidato on-prem. | ADR-0001, ADR-0008, ADR-0012, ADR-0014 | Antes de storage real. |
| [ADR-0012](../adr/0012-document-envelope-ged-core.md) | DocumentEnvelope como núcleo GED | Aceito com revisão | 2026-06-22 | Envelope como identidade/ciclo documental. | ADR-0009, ADR-0010, ADR-0011, ADR-0013, ADR-0016 | Antes das entidades do núcleo GED. |
| [ADR-0013](../adr/0013-human-review-acceptance-and-override.md) | Revisão humana, aceite e override | Aceito com revisão | 2026-06-22 | Decisão humana auditável no GED. | ADR-0012, ADR-0015, ADR-0016 | Antes do workflow de revisão. |
| [ADR-0014](../adr/0014-backup-and-restore-required.md) | Backup e restore obrigatórios | Aceito com revisão | 2026-06-22 | Backup/restore antes de operação on-prem real. | ADR-0001, ADR-0008, ADR-0010, ADR-0011 | Antes de automação/operação contínua. |
| [ADR-0015](../adr/0015-auth-authorization-security-strategy.md) | Estratégia futura de autenticação, autorização e segurança | Proposto | 2026-06-22 | Segurança exige ADR futuro antes da implementação. | ADR-0013, ADR-0016 | Antes de auth/security ou dados reais. |
| [ADR-0016](../adr/0016-capability-based-document-processing-providers.md) | Processamento documental por capabilities e providers | Proposto | 2026-07-10 | Adapters por capability, task graph, routing policy, benchmark e HITL. | ADR-0001, ADR-0009, ADR-0012, ADR-0013, ADR-0015 | Após primeiro perfil/benchmark e antes da Phase 3. |
| [ADR-0017](../adr/0017-codex-continuous-slice-loop.md) | Loop contínuo de slices pelo Codex | Aceito | 2026-07-10 | Plan aprova envelope; Codex puxa slices elegíveis e pede checkpoint em fronteiras reais. | ADR-0003, ADR-0005, ADR-0006, ADR-0007 | Se automação persistente, política de merge ou conflitos exigirem revisão. |
| [ADR-0018](../adr/0018-codex-envelope-lifecycle-and-outcomes.md) | Lifecycle do envelope e outcomes do Codex | Aceito | 2026-07-17 | Envelope tem lifecycle explícito; outcomes são exclusivos e distinguem espera, decisão e encerramento. | ADR-0003, ADR-0005, ADR-0006, ADR-0007, ADR-0017 | Se automação, política de merge ou uso dos outcomes mudar. |
| [ADR-0019](../adr/0019-local-synthetic-s3-compatible-object-storage.md) | Object storage S3-compatible no protótipo local sintético | Proposto | 2026-08-04 | Reservada a decisão sobre limites, provenance e revisão do backend local da #40. | ADR-0011 | Antes de implementar storage real na #40. |
| [ADR-0020](../adr/0020-main-ruleset-human-review-and-merge.md) | Ruleset, revisão humana e método de merge da main | Proposto | 2026-08-04 | Reservada a decisão sobre dois cutovers, checks, aprovação e squash-only. | ADR-0007 | Antes do Cutover A do ruleset. |
| [ADR-0021](../adr/0021-shared-dev-and-worktree-ownership.md) | Ownership do shared-dev e isolamento por worktrees | Proposto | 2026-08-04 | Reservada a decisão sobre owner por perfil, guards, rehearsal e rollback. | ADR-0004, ADR-0008 | Antes de implementar `devctl` ou trocar o runtime. |
| [ADR-0022](../adr/0022-living-documentation-and-implementation-traceability.md) | Documentação viva e rastreabilidade da implementação | Proposto | 2026-08-04 | Reservada a decisão sobre fontes, registries, referências, UML e site derivado. | ADR-0006 | Antes das referências de implementação e Documentation CI. |

## Avaliação dos gatilhos na Phase 1

| ADR | Evidência observada | Avaliação | Resultado |
| --- | --- | --- | --- |
| ADR-0007 | Structural CI integrado pelo PR #21; CI de aplicação integrada pela #37/PR #98 | a ordem CI antes de branch protection foi preservada; a #37 não autorizou nem configurou branch protection | decisão mantida; review obrigatório antes de futura proteção |
| ADR-0008 | primeiro Compose funcional de desenvolvimento integrado por #36/PR #94, com portas do `app-host` corrigidas por #96/PR #97 (`11342db`) | API/web stateless foram reproduzidos localmente; onprem-lab, persistência e produção não foram validados | decisão mantida para desenvolvimento local; revisão de onprem-lab continua pendente |
| ADR-0009 | workspace, API de healthcheck, shell web e Compose formam o bootstrap técnico da Phase 1 | não existem módulos de produto, domínio ou processamento; não há evidência que contrarie o modular monolith | decisão mantida; gatilho completo permanece para os primeiros módulos de produto |

Nenhuma dessas avaliações muda direção arquitetural, responsabilidade, fluxo
de revisão ou implantação. Portanto, elas não exigem ADR novo nem alteração
retroativa dos ADRs aceitos.

## Observações

- `Aceito com revisão` orienta direção inicial e exige reavaliação na condição registrada.
- `Proposto` não autoriza implementação obrigatória.
- ADR-0015 continua sendo gate para auth, autorização, dados reais e providers externos.
- ADR-0016 organiza a descoberta; provider padrão e thresholds dependem de benchmark.
- ADR-0017 preserva PR/review por slice e elimina aprovação mecânica entre itens do mesmo envelope.
- ADR-0018 complementa ADR-0017 com lifecycle, evidência durável, outcomes exclusivos e condições de retomada.
- ADR-0019 a ADR-0022 estão reservados pelo checkpoint #104; enquanto `Proposto`, não autorizam implementação obrigatória.
- Atualizar este índice quando ADRs forem criados, substituídos, complementados ou obsoletados.
