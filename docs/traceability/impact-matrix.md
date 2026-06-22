# Impact Matrix

Matriz inicial para avaliar impacto de mudanças em decisões do projeto.

Esta matriz é um guia de revisão. Ela não substitui ADRs.

| Tema de mudança | ADRs afetados | Docs afetados | Mapas a atualizar | Exige novo ADR? |
| --- | --- | --- | --- | --- |
| Estratégia on-prem/cloud-like | ADR-0001, ADR-0014 | `docs/MODELO_OPERACIONAL_DO_PROJETO.md`, `docs/AMBIENTES.md`, `docs/ROADMAP.md` | `decision-map.md`, `document-map.md`, `impact-matrix.md` | Sim, se mudar direção. |
| Iniciar código antes do fim da Phase 0 | ADR-0002 | `docs/ROADMAP.md`, `docs/MODELO_OPERACIONAL_DO_PROJETO.md`, `AGENTS.md` | `decision-map.md`, `impact-matrix.md` | Sim. |
| Fluxo Git/PR/revisão | ADR-0003, ADR-0007 | `docs/ESTRATEGIA_GIT.md`, `docs/MODELO_OPERACIONAL_DO_PROJETO.md` | `decision-map.md`, `document-map.md`, `impact-matrix.md` | Sim, se mudar regra. |
| Ambiente WSL local | ADR-0004, ADR-0008 | `docs/AMBIENTES.md`, `docs/WSL_MULTI_PROJETOS.md` | `document-map.md`, `impact-matrix.md` | Sim, se mudar ambiente oficial. |
| Uso ou configuração Codex | ADR-0005 | `AGENTS.md`, `.codex/config.toml`, `docs/MODELO_OPERACIONAL_DO_PROJETO.md` | `document-map.md`, `impact-matrix.md` | Sim, se mudar política. |
| CI ou branch protection | ADR-0007, ADR-0003 | `docs/ESTRATEGIA_GIT.md`, `docs/AMBIENTES.md`, `docs/ROADMAP.md` | `decision-map.md`, `impact-matrix.md` | Sim, se mudar ordem ou regra. |
| Docker Compose | ADR-0008, ADR-0004 | `docs/AMBIENTES.md`, `docs/WSL_MULTI_PROJETOS.md`, `docs/ROADMAP.md` | `decision-map.md`, `module-map.md`, `impact-matrix.md` | Sim, se mudar direção operacional. |
| Modular monolith | ADR-0009 | `docs/MODELO_OPERACIONAL_DO_PROJETO.md`, `docs/ROADMAP.md` | `decision-map.md`, `module-map.md`, `impact-matrix.md` | Sim, se mudar arquitetura. |
| PostgreSQL | ADR-0010, ADR-0014 | `docs/AMBIENTES.md`, `docs/ROADMAP.md` | `entity-map.md`, `module-map.md`, `impact-matrix.md` | Sim, antes de trocar banco. |
| Object storage | ADR-0011, ADR-0014 | `docs/AMBIENTES.md`, `docs/ROADMAP.md` | `entity-map.md`, `module-map.md`, `impact-matrix.md` | Sim, antes de declarar storage definitivo. |
| DocumentEnvelope | ADR-0012 | `docs/ROADMAP.md`, `docs/uml/README.md` | `entity-map.md`, `module-map.md`, `route-map.md`, `impact-matrix.md` | Sim, se mudar núcleo GED. |
| Revisão/aceite/override | ADR-0013, ADR-0015 | `docs/ROADMAP.md`, `docs/uml/README.md`, `AGENTS.md` | `entity-map.md`, `module-map.md`, `route-map.md`, `impact-matrix.md` | Sim, se mudar fluxo. |
| Backup/restore | ADR-0014, ADR-0010, ADR-0011 | `docs/AMBIENTES.md`, `docs/ROADMAP.md` | `impact-matrix.md`, `decision-map.md` | Sim, antes de operação real. |
| Auth/security | ADR-0015 | `AGENTS.md`, `docs/MODELO_OPERACIONAL_DO_PROJETO.md`, `docs/ROADMAP.md` | `module-map.md`, `entity-map.md`, `route-map.md`, `impact-matrix.md` | Sim; ADR-0015 está Proposto. |

## Regras de manutenção

- Atualizar quando um ADR mudar status ou relação.
- Atualizar quando módulos, entidades, rotas ou documentos reais surgirem.
- Não usar esta matriz para criar código fora da fase correspondente.
