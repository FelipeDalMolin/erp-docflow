# Status do projeto

- **Classe:** snapshot operacional canônico
- **Estado:** vigente
- **Data de referência:** 2026-07-21
- **Issue de atualização:** [#73](https://github.com/FelipeDalMolin/erp-docflow/issues/73)
- **Atualizar quando:** uma fase, release, gate, Epic ou condição de execução mudar

Este documento responde apenas **onde o projeto está agora, qual é o próximo gate e quais evidências sustentam esse estado**. O escopo permanente está no [Roadmap](ROADMAP.md); o estado diário continua no GitHub Project, nas Issues e nos Pull Requests.

## Resumo executivo

```text
Phase 0: encerrada e integrada à main
Phase 1 / R0: execução controlada autorizada pela Epic #26
#33: entrega técnica no PR #72, ready for review e com Structural CI verde
Próximo gate: review humano + squash merge do PR #72
#34 e #35: especificadas, bloqueadas até o merge da #33
R1 Golden Month: Epic #75 criada em Rascunho; não autorizada para implementação
Realinhamento documental/backlog: PR #87 draft, mergeable e com Structural CI verde; aguardando review humano
```

A autorização da Phase 1 não transforma todas as suas slices em elegíveis. A #33 é a única entrega preparada; #34–#37 continuam obedecendo suas dependências. Também não autoriza automaticamente a Phase 2 nem a release R1.

## Estado por frente

| Frente | Referência | Estado | Condição atual |
| --- | --- | --- | --- |
| Phase 0 — sistema do projeto | [#1](https://github.com/FelipeDalMolin/erp-docflow/issues/1) | concluída | baseline, hardening e organização documental integrados |
| Phase 1 / R0 — bootstrap técnico | [#26](https://github.com/FelipeDalMolin/erp-docflow/issues/26) | execução controlada | #33 em Review; #34–#37 bloqueadas por dependências |
| Phase 2 — GED e intake | [#27](https://github.com/FelipeDalMolin/erp-docflow/issues/27) | backlog | envelope não aprovado; deve terminar em materialização + `INSPECTION_PENDING` |
| Phase 3 — processamento | [#28](https://github.com/FelipeDalMolin/erp-docflow/issues/28) | backlog/descoberta | perfil, Tika, benchmark e ADR-0016 ainda precisam de evidência/decisão |
| Phase 4 — review e acceptance | [#29](https://github.com/FelipeDalMolin/erp-docflow/issues/29) | backlog | deve cobrir documento, importação, vínculos e fatos propostos |
| Phase 5 — domínio gerencial | [#30](https://github.com/FelipeDalMolin/erp-docflow/issues/30) | backlog a refinar | #54–#57 serão reorientadas para fatos multiorigem e reconciliação |
| Phase 6 — geração documental | [#31](https://github.com/FelipeDalMolin/erp-docflow/issues/31) | backlog | `GeneratedDocument` não é pacote contábil nem release do produto |
| Phase 7 — integrações | [#32](https://github.com/FelipeDalMolin/erp-docflow/issues/32) | backlog | XLSX/CSV local pertence ao R1; OFX/webhooks ficam nesta trilha |
| R1 — Golden Month | [#75](https://github.com/FelipeDalMolin/erp-docflow/issues/75) | Rascunho | discovery/refinamento; sem envelope aprovado |
| Alinhamento produto/processamento | [#73](https://github.com/FelipeDalMolin/erp-docflow/issues/73) / [PR #87](https://github.com/FelipeDalMolin/erp-docflow/pull/87) | checkpoint de revisão | entrega técnica em draft, mergeable e com Structural CI verde; não implementa produto |

As Phases 2–7 organizam maturidade/capabilities. Elas não constituem uma waterfall obrigatória para releases: o R1 compõe o menor conjunto de capabilities necessário e não depende de OCR.

## Evidências integradas

| Entrega | Issue | Evidência |
| --- | --- | --- |
| Phase 0 administrativa | #1 | PRs #12–#21 |
| arquitetura documental consolidada | #22 | PR #23 |
| loop contínuo do Codex | #24 | PR #25 |
| hardening do backlog/documentação | #65 | PR #68 |
| organização física e auditoria | #69 | PR #70 |
| lifecycle de envelope/outcomes | #67 | PR #71 e ADR-0018 |
| autorização do R0/Phase 1 | #26 | registro de 2026-07-17 na própria Epic |

#65, #67 e #69 estão encerradas. Seus relatórios permanecem evidência histórica; não representam trabalho corrente.

## Gate corrente da Phase 1

O gate Phase 0 → Phase 1 foi satisfeito e o envelope da Epic #26 está **Aprovado**. O gate operacional corrente é concluir a #33:

- [x] runtimes, gerenciadores, layout e ownership definidos;
- [x] #33 com `Condições Verificadas`;
- [x] entrega técnica publicada no PR #72;
- [x] Structural CI verde;
- [x] PR #72 fora de draft e mergeable;
- [ ] review humano do PR #72;
- [ ] squash merge humano;
- [ ] fechamento automático/manual da #33 reconciliado no Project.

O PR #72 ainda não está integrado à `main`; portanto, a árvore principal continua sem código de produto.

## Fila autorizada da Phase 1

```text
#33 workspace -- PR #72 aguardando review/merge
  -> #34 backend e #35 frontend, paralelos após merge da #33
  -> #36 Compose de desenvolvimento, após #34 e #35
  -> #37 CI/runbook/status, após #36
  -> concluir #26 como R0
```

| Issue | Especificação | Condição atual | Desbloqueio |
| --- | --- | --- | --- |
| #33 | fechada | Review | squash merge do PR #72 |
| #34 | fechada | bloqueada | merge da #33 |
| #35 | fechada | bloqueada | merge da #33 |
| #36 | fechada | bloqueada | merges de #34 e #35 |
| #37 | fechada | bloqueada | merges de #33–#36 |

Depois do merge da #33, #34 e #35 podem avançar em paralelo somente a partir da nova `main`, com ownership sem sobreposição. A #73 deve ser mergeada ou reconciliada antes de qualquer slice que toque os mesmos documentos.

## Release R1 em descoberta

A [Epic #75](https://github.com/FelipeDalMolin/erp-docflow/issues/75) registra o piloto **Golden Month** com envelope `Rascunho`. Sua criação organiza o trabalho; não autoriza código.

Dependências principais:

- [#74](https://github.com/FelipeDalMolin/erp-docflow/issues/74): decisão do núcleo de produto;
- [#76](https://github.com/FelipeDalMolin/erp-docflow/issues/76): arquitetura de informação/UX;
- [#77](https://github.com/FelipeDalMolin/erp-docflow/issues/77): importação XLSX/CSV;
- [#78](https://github.com/FelipeDalMolin/erp-docflow/issues/78): reporting e lineage;
- [#79](https://github.com/FelipeDalMolin/erp-docflow/issues/79): fechamento e pacote;
- [#80](https://github.com/FelipeDalMolin/erp-docflow/issues/80): autoridade contábil;
- [#81](https://github.com/FelipeDalMolin/erp-docflow/issues/81): bundle instalável no `onprem-lab`;
- refinamento/reuso de #39–#40, #49–#57.

Tika/OCR (#82–#86 e Epic #28) evoluem em trilha paralela e não bloqueiam o caminho import-first.

## Gaps operacionais conhecidos

- A taxonomia alvo ainda não está materializada; trabalho registrado na [#66](https://github.com/FelipeDalMolin/erp-docflow/issues/66).
- As opções reais do GitHub Project ainda precisam ser confrontadas com o vocabulário documental antes de automação.
- Os modelos em `docs/templates/` continuam referências, não templates nativos do GitHub.
- ADR-0015 e ADR-0016 permanecem `Proposto`; não autorizam segurança/providers reais.
- O princípio de produto exige decisão durável na #74 antes de schema/efeito.
- O Tika exige spike #82 e benchmark #83 antes de decisão/integração produtiva.
- Dados reais, secrets, deploy de produção, automerge e branch protection continuam fora dos envelopes atuais.

## Regra de atualização

Atualizar este snapshot no mesmo PR que:

- autorizar, pausar ou encerrar um envelope;
- mudar o gate de uma Phase ou release;
- tornar uma slice elegível, iniciar Review ou concluir uma Epic;
- integrar a primeira evidência de código de produto;
- materializar taxonomia/automação aqui registrada como gap;
- criar ou substituir a release-alvo do produto.
