# ADR Index

Lista baseline dos ADRs existentes na Phase 0.

Este mapa reflete decisões registradas em `docs/adr/`. Ele não cria decisões novas e não autoriza implementação fora da fase correspondente.

| ADR | Título | Status | Data | Decisão curta | Relações principais | Revisão futura |
| --- | --- | --- | --- | --- | --- | --- |
| ADR-0001 | On-prem first com práticas cloud-like | Aceito | 2026-06-22 | Operação principal local com práticas cloud-like. | ADR-0002, ADR-0014 | Se cloud/híbrido virar prioridade principal. |
| ADR-0002 | Phase 0 antes de código de produto | Aceito | 2026-06-22 | Phase 0 mínima antes de código de produto. | ADR-0001, ADR-0003, ADR-0005, ADR-0006 | Ao iniciar Phase 1. |
| ADR-0003 | Fluxo Git por Issue, branch, PR e revisão | Aceito | 2026-06-22 | Issue -> branch -> PR -> revisão humana -> squash merge. | ADR-0002, ADR-0005, ADR-0007 | Se volume/maturidade exigir outro fluxo. |
| ADR-0004 | Desenvolvimento local com Windows, WSL e VS Code | Aceito | 2026-06-22 | Windows host + Ubuntu-20.04 WSL + VS Code em WSL. | ADR-0002, ADR-0005, ADR-0008 | Migração WSL ou onprem-lab próprio. |
| ADR-0005 | Uso controlado do Codex | Aceito | 2026-06-22 | Codex com autonomia controlada por Issue, branch, PR e revisão humana. | ADR-0003, ADR-0004, ADR-0006 | Mudança no uso/configuração Codex. |
| ADR-0006 | Governança de ADRs e rastreabilidade | Aceito | 2026-06-22 | Decisões relevantes viram ADR; mapas mantêm rastreabilidade. | Todos os ADRs do baseline | Ao criar/alterar mapas ou regra de ADR. |
| ADR-0007 | CI estrutural antes de branch protection | Aceito com revisão | 2026-06-22 | CI estrutural vem antes de branch protection. | ADR-0002, ADR-0003 | Após CI estrutural e antes de branch protection. |
| ADR-0008 | Docker Compose para local e onprem-lab | Aceito com revisão | 2026-06-22 | Docker Compose como direção futura para local/onprem-lab. | ADR-0004, ADR-0010, ADR-0011, ADR-0014 | Quando existir Compose inicial. |
| ADR-0009 | Arquitetura inicial como modular monolith | Aceito com revisão | 2026-06-22 | Modular monolith como direção inicial. | ADR-0001, ADR-0012, ADR-0013 | Após bootstrap app e primeiros módulos. |
| ADR-0010 | PostgreSQL como banco relacional principal | Aceito com revisão | 2026-06-22 | PostgreSQL como direção inicial de banco. | ADR-0001, ADR-0008, ADR-0012, ADR-0014 | Antes de schema, migrations ou persistência. |
| ADR-0011 | Object storage S3-compatible | Aceito com revisão | 2026-06-22 | S3-compatible como direção futura; MinIO como candidato on-prem. | ADR-0001, ADR-0008, ADR-0012, ADR-0014 | Antes de integração real com object storage. |
| ADR-0012 | DocumentEnvelope como núcleo GED | Aceito com revisão | 2026-06-22 | DocumentEnvelope como direção inicial do núcleo GED. | ADR-0009, ADR-0010, ADR-0011, ADR-0013 | Antes de entidades do núcleo GED. |
| ADR-0013 | Revisão humana, aceite e override | Aceito com revisão | 2026-06-22 | Revisão/aceite/override como direção futura do GED. | ADR-0012, ADR-0015 | Antes do workflow de revisão. |
| ADR-0014 | Backup e restore obrigatórios | Aceito com revisão | 2026-06-22 | Backup/restore obrigatórios antes de operação on-prem real. | ADR-0001, ADR-0008, ADR-0010, ADR-0011 | Antes de automação ou operação contínua. |
| ADR-0015 | Estratégia futura de autenticação, autorização e segurança | Proposto | 2026-06-22 | Auth/security exigem ADR futuro antes de implementação. | ADR-0013 | Antes de implementar auth/security. |

## Observações

- `Aceito com revisão` orienta direção inicial, mas exige reavaliação na condição registrada no ADR.
- `ADR-0015` está `Proposto`; ele não autoriza implementação de autenticação, autorização ou segurança.
- Este índice deve ser atualizado quando ADRs forem criados, substituídos, complementados ou obsoletados.
