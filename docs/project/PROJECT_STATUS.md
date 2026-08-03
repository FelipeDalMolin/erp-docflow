# Status do projeto

- **Classe:** snapshot operacional canônico
- **Estado:** vigente
- **Data de referência:** 2026-08-02
- **Issue de atualização:** [#37](https://github.com/FelipeDalMolin/erp-docflow/issues/37)
- **Atualizar quando:** uma fase, release, gate, Epic ou condição de execução mudar

Este documento responde apenas **onde o projeto está agora, qual é o próximo gate e quais evidências sustentam esse estado**. O escopo permanente está no [Roadmap](ROADMAP.md); o estado diário continua no GitHub Project, nas Issues e nos Pull Requests.

## Resumo executivo

```text
Phase 0: encerrada e integrada à main
Phase 1 / R0: execução controlada autorizada pela Epic #26
#33–#36: integradas pelos PRs #72, #90, #91 e #94
#96: correção de portas integrada pelo PR #97 no commit 11342db
#37: entrega técnica no draft PR #98; Application CI e Structural CI verdes
Próximo gate: review e squash merge humanos do PR #98, reprodução e reconciliação da Epic #26
Protótipo PDF-first: envelope específico #92 aprovado; artefatos de preparação existem, runtime de produto não
R1 Golden Month: Epic #75 criada em Rascunho; não autorizada para implementação
Realinhamento documental/backlog: Issue #73 e PR #87 integrados; continua sendo documentação planejada
```

A `main` contém a fundação técnica R0: workspace, API limitada a healthcheck,
shell web e Compose de desenvolvimento para API/web. Isso não constitui ERP,
GED, intake, interpretação PDF-first, review ou fluxo de produto funcional. A
conclusão técnica da Phase 1 ainda depende da #37, de review e merge humanos e
da reconciliação da Epic #26. O envelope PDF-first #92 foi aprovado
separadamente, mas cada slice de código continua sujeita às suas próprias
condições verificadas e dependências; a release R1 permanece não autorizada.

## Estado por frente

| Frente | Referência | Estado | Condição atual |
| --- | --- | --- | --- |
| Phase 0 — sistema do projeto | [#1](https://github.com/FelipeDalMolin/erp-docflow/issues/1) | concluída | baseline, hardening e organização documental integrados |
| Phase 1 / R0 — bootstrap técnico | [#26](https://github.com/FelipeDalMolin/erp-docflow/issues/26) | conclusão técnica em execução | #33–#36 integradas; #37 é a slice corrente e ainda requer CI, review, merge e reconciliação |
| Phase 2 — GED e intake | [#27](https://github.com/FelipeDalMolin/erp-docflow/issues/27) / [#92](https://github.com/FelipeDalMolin/erp-docflow/issues/92) | backlog com envelope PDF-first específico aprovado | contrato de persistência/storage ratificado; #39 ainda precisa de especificação executável e do fechamento da Phase 1; não há schema, storage, endpoint ou intake implementado |
| Phase 3 — processamento | [#28](https://github.com/FelipeDalMolin/erp-docflow/issues/28) | backlog/descoberta | profile/dataset sintético PDF-first existe como candidato; não há processamento, interpretação ou provider funcional |
| Phase 4 — review e acceptance | [#29](https://github.com/FelipeDalMolin/erp-docflow/issues/29) | backlog | deve cobrir documento, importação, vínculos e fatos propostos |
| Phase 5 — domínio gerencial | [#30](https://github.com/FelipeDalMolin/erp-docflow/issues/30) | backlog a refinar | #54–#57 serão reorientadas para fatos multiorigem e reconciliação |
| Phase 6 — geração documental | [#31](https://github.com/FelipeDalMolin/erp-docflow/issues/31) | backlog | `GeneratedDocument` não é pacote contábil nem release do produto |
| Phase 7 — integrações | [#32](https://github.com/FelipeDalMolin/erp-docflow/issues/32) | backlog | XLSX/CSV local pertence ao R1; OFX/webhooks ficam nesta trilha |
| R1 — Golden Month | [#75](https://github.com/FelipeDalMolin/erp-docflow/issues/75) | Rascunho | discovery/refinamento; sem envelope aprovado |
| Alinhamento produto/processamento | [#73](https://github.com/FelipeDalMolin/erp-docflow/issues/73) / [PR #87](https://github.com/FelipeDalMolin/erp-docflow/pull/87) | integrado | baseline documental integrado; não implementa produto |

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
| realinhamento documental de produto/processamento | #73 | PR #87 |
| workspace mínimo | #33 | PR #72 |
| API FastAPI limitada a `GET /health` | #34 | PR #90 |
| shell React/Vite com rotas técnicas | #35 | PR #91 |
| Compose de desenvolvimento API/web | #36 | PR #94 |
| reserva de portas no `app-host` | #96 | PR #97, commit `11342db` |

#65, #67 e #69 estão encerradas. Seus relatórios permanecem evidência histórica; não representam trabalho corrente.

## Gate corrente da Phase 1

O gate Phase 0 → Phase 1 foi satisfeito e o envelope da Epic #26 está
**Aprovado**. Os pré-requisitos da #37 estão integrados, mas a Phase 1 ainda não
está concluída:

- [x] #33 integrada pelo PR #72;
- [x] #34 integrada pelo PR #90;
- [x] #35 integrada pelo PR #91;
- [x] #36 integrada pelo PR #94;
- [x] correção de portas #96 integrada pelo PR #97 no commit `11342db`;
- [x] #37 com `Condições Verificadas` e branch baseada em `11342db`;
- [x] CI de aplicação, runbook, status e rastreabilidade da #37 validados localmente;
- [x] entrega da #37 publicada no draft PR #98 com Application CI e Structural CI verdes;
- [ ] review humano e squash merge da #37;
- [ ] ambiente reproduzido e Issue #37/Epic #26 reconciliadas após o merge.

## Fila autorizada da Phase 1

```text
#33 workspace -- integrado pelo PR #72
  -> #34 backend -- integrado pelo PR #90
  -> #35 frontend -- integrado pelo PR #91
  -> #36 Compose -- integrado pelo PR #94
  -> #96 portas -- integrado pelo PR #97 / 11342db
  -> #37 CI, runbook, status e rastreabilidade -- em execução
  -> review + squash merge humanos
  -> reprodução, reconciliação e encerramento da #26 com STOP
```

| Issue | Especificação | Condição atual | Gate restante |
| --- | --- | --- | --- |
| #33 | fechada | integrada | nenhum |
| #34 | fechada | integrada | nenhum |
| #35 | fechada | integrada | nenhum |
| #36 | fechada | integrada | nenhum |
| #37 | fechada | em execução | CI, PR, review, merge e reconciliação |

O encerramento da Phase 1 entrega somente o R0 técnico previsto na Epic #26.
O envelope #92 autoriza a direção PDF-first, mas não elimina o refinamento e os
gates de cada slice. A implementação de produto começa apenas quando #39 tiver
especificação executável e as dependências da Phase 1 estiverem satisfeitas.

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

Tika/OCR/estrutura (#82–#86 e #88–#89, na Epic #28) evoluem em trilha paralela e não bloqueiam o caminho import-first.

## Gaps operacionais conhecidos

- A taxonomia alvo ainda não está materializada; trabalho registrado na [#66](https://github.com/FelipeDalMolin/erp-docflow/issues/66).
- As opções reais do GitHub Project ainda precisam ser confrontadas com o vocabulário documental antes de automação.
- Os modelos em `docs/templates/` continuam referências, não templates nativos do GitHub.
- ADR-0015 e ADR-0016 permanecem `Proposto`; não autorizam segurança/providers reais.
- O princípio de produto exige decisão durável na #74 antes de schema/efeito.
- Tika/OCR exigem #82/#83; o lifecycle reproduzível e a avaliação Docling estão em #88/#89. Nenhum provider foi promovido.
- Dados reais, secrets, deploy de produção, automerge e branch protection continuam fora dos envelopes atuais.

## Regra de atualização

Atualizar este snapshot no mesmo PR que:

- autorizar, pausar ou encerrar um envelope;
- mudar o gate de uma Phase ou release;
- tornar uma slice elegível, iniciar Review ou concluir uma Epic;
- integrar a primeira evidência de código de produto;
- materializar taxonomia/automação aqui registrada como gap;
- criar ou substituir a release-alvo do produto.
