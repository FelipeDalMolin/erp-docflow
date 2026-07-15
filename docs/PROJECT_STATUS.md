# Status do projeto

- **Classe:** snapshot operacional canônico
- **Estado:** vigente
- **Data de referência:** 2026-07-14
- **Issue de revisão:** [#65](https://github.com/FelipeDalMolin/erp-docflow/issues/65)
- **Atualizar quando:** uma fase, gate, Epic ou condição de execução mudar

Este documento responde apenas **onde o projeto está agora, qual é o próximo gate e quais evidências sustentam esse estado**. O escopo permanente das fases continua no [Roadmap](ROADMAP.md), e o estado diário dos itens continua no GitHub Project, nas Issues e nos Pull Requests.

## Resumo executivo

```text
Phase 0: concluída administrativamente e integrada à main
Hardening documental pós-Phase 0: em andamento na Issue #65
Phase 1: Epic aberta, em refinamento; execução de código ainda não autorizada
Próxima candidata: #33, somente após especificação e gate 0 → 1 registrados
```

O fechamento histórico da Phase 0 não será reescrito. As inconsistências encontradas depois do fechamento são tratadas como hardening rastreável. Enquanto o gate abaixo não estiver satisfeito, a Epic aberta da Phase 1 representa backlog organizado, não um envelope de execução aprovado.

## Estado por fase

| Fase | Epic | Estado | Condição atual |
| --- | --- | --- | --- |
| Phase 0 — sistema do projeto | [#1](https://github.com/FelipeDalMolin/erp-docflow/issues/1) | concluída | S0.01–S0.10 integradas; #22 e S0.11 foram hardening posterior. |
| Phase 1 — bootstrap app | [#26](https://github.com/FelipeDalMolin/erp-docflow/issues/26) | em refinamento | #33–#37 estão abertas e ainda precisam de especificação; não há código de produto. |
| Phase 2 — núcleo GED e intake | [#27](https://github.com/FelipeDalMolin/erp-docflow/issues/27) | backlog | depende da conclusão da Phase 1 e dos gates de persistência/storage/acesso. |
| Phase 3 — processamento documental | [#28](https://github.com/FelipeDalMolin/erp-docflow/issues/28) | backlog | depende do intake e da escolha de perfil/dataset na #43. |
| Phase 4 — review e acceptance | [#29](https://github.com/FelipeDalMolin/erp-docflow/issues/29) | backlog | depende dos artefatos de processamento e das políticas da #49. |
| Phase 5 — núcleo financeiro | [#30](https://github.com/FelipeDalMolin/erp-docflow/issues/30) | backlog | depende de snapshot aceito e autorização explícita. |
| Phase 6 — geração documental | [#31](https://github.com/FelipeDalMolin/erp-docflow/issues/31) | backlog | depende do núcleo GED e da política de templates. |
| Phase 7 — integrações | [#32](https://github.com/FelipeDalMolin/erp-docflow/issues/32) | backlog | depende dos boundaries e controles das fases consumidas. |

## Evidências da Phase 0

| Entrega | Issue | Evidência integrada |
| --- | --- | --- |
| documentação operacional inicial | #2 | PR #12 |
| fluxo GitHub Project e runbook local | #3 e #4 | PR #18; WSL complementado pelo PR #13 |
| orientação e configuração Codex | #5 | PR #14 |
| ADR baseline | #6 | PR #15 |
| traceability baseline | #7 | PR #16 |
| UML baseline | #8 | PR #17 |
| templates de referência | #9 e #10 | PRs #19 e #20 |
| Structural CI inicial | #11 | PR #21 |
| arquitetura documental consolidada | #22 | PR #23 |
| loop contínuo do Codex | #24 | PR #25 |

A Epic #1 foi encerrada em 2026-06-23. As Issues #22 e #24 foram integradas em 2026-07-10 e são registradas como hardening pós-fechamento, sem reabrir ou apagar o marco histórico.

## Gate Phase 0 → Phase 1

O gate possui duas dimensões diferentes:

1. **baseline histórica concluída:** os artefatos mínimos definidos pelo ADR-0002 foram entregues;
2. **autorização do próximo envelope:** a primeira slice da Phase 1 só pode iniciar quando estiver especificada e o envelope registrar revisão humana.

Para autorizar execução da Phase 1, registrar na Epic #26 ou no plano aprovado:

- [ ] Issue #65 revisada e integrada, ou exceção explícita sem contradição bloqueante;
- [ ] revisão do gatilho do ADR-0002 ao iniciar código de produto;
- [ ] revisão do ADR-0007 após o CI estrutural e antes de eventual branch protection;
- [ ] runtimes, gerenciadores de pacotes e layout mínimo definidos para a #33;
- [ ] #33 com escopo, paths, validações e `Condições Verificadas`;
- [ ] envelope com estado `Aprovado`, responsável, data/referência, dependências e paths permitidos;
- [ ] nenhuma decisão de segurança, persistência ou deploy sendo antecipada.

Escolher o primeiro perfil documental **não** pertence a este gate. Essa decisão é a entrada da Phase 3 e está representada pela [Issue #43](https://github.com/FelipeDalMolin/erp-docflow/issues/43).

## Fila candidata da Phase 1

```text
#65 — coerência documental e do backlog
  -> #33 — workspace e monorepo mínimo
       ├── #34 — backend FastAPI + /health
       └── #35 — frontend React/Vite mínimo
            -> #36 — Docker Compose de desenvolvimento
                 -> #37 — CI da aplicação + documentação de execução
                      -> concluir #26
```

#34 e #35 podem seguir em paralelo apenas depois do merge da #33, com ownership de arquivos sem sobreposição registrado no envelope.

| Issue | Condição | Dependência | Próximo refinamento obrigatório |
| --- | --- | --- | --- |
| #33 | Precisa Especificação | #65/gate 0 → 1 | layout, runtimes, package managers, paths e comandos de validação |
| #34 | Precisa Especificação | #33 mergeada | contrato do `/health`, estrutura FastAPI e testes mínimos |
| #35 | Precisa Especificação | #33 mergeada | estrutura Vite/React, build e teste mínimo sem dados reais |
| #36 | Precisa Especificação | #34 e #35 mergeadas | serviços, portas, healthchecks, rede e configuração sem secrets |
| #37 | Precisa Especificação | #33–#36 mergeadas | matriz de CI, comandos reproduzíveis e atualização do status |

Nenhuma dessas slices deve receber `codex:eligible` ou ser tratada como `Condições Verificadas` apenas porque a Epic existe.

## Gaps operacionais conhecidos

- A taxonomia `type:*`, `phase:*`, `status:*`, `codex:*` e `area:*` está documentada como alvo, mas não está aplicada às Issues legadas; materialização rastreada na [#66](https://github.com/FelipeDalMolin/erp-docflow/issues/66).
- As opções reais dos campos do GitHub Project ainda precisam ser confrontadas com o vocabulário canônico da documentação.
- Os modelos em `docs/templates/` são referências, não templates nativos do GitHub.
- Nenhuma milestone é usada atualmente; `Fase` deve permanecer campo do Project/título até decisão diferente, evitando duas fontes concorrentes.
- ADRs propostos, em especial ADR-0015 e ADR-0016, continuam sem autorizar segurança/providers reais.
- A precisão durável dos outcomes/envelope do Codex será decidida na [#67](https://github.com/FelipeDalMolin/erp-docflow/issues/67), sem reescrever silenciosamente o ADR-0017.

Esses gaps devem ser tratados por Issues próprias ou pelo escopo explícito da #65. Eles não devem ser ocultados por labels ou estados que ainda não existem.

## Regra de atualização

Atualizar este snapshot no mesmo PR que:

- autorizar ou encerrar um gate de fase;
- tornar uma slice `Condições Verificadas`;
- iniciar ou concluir uma Epic;
- materializar taxonomia/automação que aqui apareça como gap;
- introduzir a primeira evidência de implementação de produto.
