# Document Map

Mapa inicial entre documentos existentes e ADRs relacionados.

Este mapa registra vínculos documentais, não contratos de implementação.

| Documento | Tipo de vínculo | ADRs relacionados | Observação |
| --- | --- | --- | --- |
| `AGENTS.md` | Codex, operação, revisão humana | ADR-0002, ADR-0005, ADR-0015 | Define regras operacionais do Codex e pontos de parada. |
| `.codex/config.toml` | Codex, configuração local | ADR-0005 | Configuração operacional do Codex no projeto. |
| `docs/MODELO_OPERACIONAL_DO_PROJETO.md` | operação, governança, arquitetura futura | ADR-0001, ADR-0002, ADR-0003, ADR-0005, ADR-0006, ADR-0009, ADR-0010, ADR-0011, ADR-0012, ADR-0013, ADR-0015 | Fonte de fluxo, papéis e decisões estruturais. |
| `docs/ROADMAP.md` | fases, produto futuro | ADR-0001, ADR-0002, ADR-0007, ADR-0008, ADR-0009, ADR-0010, ADR-0011, ADR-0012, ADR-0013, ADR-0014, ADR-0015 | Define Phase 0 e fases futuras. |
| `docs/ESTRATEGIA_GIT.md` | Git, PR, revisão | ADR-0003, ADR-0007 | Define fluxo Git e branch protection futura. |
| `docs/AMBIENTES.md` | ambientes, on-prem, CI, backup | ADR-0001, ADR-0004, ADR-0007, ADR-0008, ADR-0010, ADR-0011, ADR-0014 | Define local, CI, onprem-lab e prod-onprem. |
| `docs/WSL_MULTI_PROJETOS.md` | ambiente local, WSL, Codex | ADR-0004, ADR-0005, ADR-0008 | Define Windows/WSL/VS Code e isolamento por projeto. |
| `docs/adr/README.md` | ADR, governança | ADR-0006 | Define estrutura e status dos ADRs. |
| `docs/traceability/README.md` | rastreabilidade | ADR-0006 | Define mapas previstos e quando atualizar rastreabilidade. |
| `docs/uml/README.md` | UML, arquitetura futura | ADR-0012, ADR-0013 | Define tipos de diagramas futuros e relação com ADRs. |

## Regras de manutenção

- Atualizar quando documento novo entrar no projeto.
- Atualizar quando documento existente passar a depender de novo ADR.
- Não listar arquivos de código de produto enquanto eles não existirem.
