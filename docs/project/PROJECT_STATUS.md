# Status do projeto

- **Classe:** snapshot operacional canônico
- **Estado:** vigente
- **Data de referência:** 2026-08-04
- **Issue de atualização:** [#109](https://github.com/FelipeDalMolin/erp-docflow/issues/109), sob o checkpoint governante [#104](https://github.com/FelipeDalMolin/erp-docflow/issues/104)
- **Atualizar quando:** uma fase, release, gate, Epic ou condição de execução mudar

Este documento responde apenas **onde o projeto está agora, qual é o próximo gate e quais evidências sustentam esse estado**. O escopo permanente está no [Roadmap](ROADMAP.md); o estado diário continua no GitHub Project, nas Issues e nos Pull Requests.

> **Reconciliação limitada — 2026-08-04:** esta atualização corrige o gate
> canônico depois da integração da #39/PR #103 e registra o checkpoint #104.
> O Roadmap, o contrato de persistência/storage, o mapa documental e o corpo da
> #40 ainda contêm linguagem anterior ao merge da #103; a correção coordenada
> permanece na etapa 4 da #104. Para o estado e o gate correntes deste
> checkpoint, prevalecem este snapshot e a #104.

## Resumo executivo

```text
Phase 0: encerrada e integrada à main
Phase 1 / R0: encerrada; entrega integrada e reproduzida
#33–#37: integradas pelos PRs #72, #90, #91, #94 e #98
#96: correção de portas integrada pelo PR #97 no commit 11342db
#37/#26: encerramento factual integrado pelo PR #102 no commit 0691aa5
R0 reproduzido no app-host: API/web healthy em 8100/5180, com Jubileu preservado em 8000/5173/8080
#39/PR #103: domínio, schema, migrations, PostgreSQL interno e repositórios PDF-first integrados à main no commit ec1b558
ADR-0019/#107/PR #108: limites do storage S3-compatible local sintético integrados no commit 372a3a6, com status Aceito com revisão
Checkpoint pré-S2.03 #104: aprovado e em execução; #109 corrige o snapshot canônico pós-merge
Próximo gate após #109: aceitar o ADR-0020 e seguir a sequência vinculante da #104
#40: aberta e bloqueada; branch e implementação permanecem proibidas até o gate final da #104
Protótipo PDF-first: camada relacional implementada e testada, ainda não conectada ao runtime HTTP; storage, upload, telas e interpretação não existem
R1 Golden Month: Epic #75 criada em Rascunho; não autorizada para implementação
Realinhamento documental/backlog: Issue #73 e PR #87 integrados; continua sendo documentação planejada
```

A `main` preserva a fundação técnica R0 e contém a primeira fatia de produto da
Phase 2 integrada pela #39/PR #103: domínio puro, PostgreSQL interno, migrations
e persistência transacional. A API HTTP continua expondo somente o R0 técnico e
ainda não aciona esses repositórios; suas portas reservadas não interrompem o
Jubileu.
Ainda não há original recuperável, endpoint de upload, telas,
interpretação ou review; `VerifiedOriginalDescriptor` contém somente metadados
sintéticos e não prova que um objeto existe. Cada slice posterior continua
sujeita às próprias condições verificadas e ao merge humano da anterior.

## Estado por frente

| Frente | Referência | Estado | Condição atual |
| --- | --- | --- | --- |
| Phase 0 — sistema do projeto | [#1](https://github.com/FelipeDalMolin/erp-docflow/issues/1) | concluída | baseline, hardening e organização documental integrados |
| Phase 1 / R0 — bootstrap técnico | [#26](https://github.com/FelipeDalMolin/erp-docflow/issues/26) | concluída | #33–#37 integradas, snapshot reconciliado e runtime/CI reproduzidos; outcome `STOP` |
| Phase 2 — GED e intake | [#27](https://github.com/FelipeDalMolin/erp-docflow/issues/27) / [#92](https://github.com/FelipeDalMolin/erp-docflow/issues/92) | em execução PDF-first | #39 materializa a camada de domínio/persistência relacional, ainda sem rota; #40–#42 continuam sequenciais e não implementadas |
| Phase 3 — processamento | [#28](https://github.com/FelipeDalMolin/erp-docflow/issues/28) | descoberta em paralelo | profile/dataset e harness com hardening integrado pelo PR #101; #82/#83 exigem refinamento próprio; nenhum provider foi promovido |
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
| CI de aplicação e runbooks reproduzíveis | #37 | PR #98, commit `7a39bac` |
| reconciliação e encerramento factual da Phase 1 | #37/#26 | PR #102, commit `0691aa5` |
| profile e dataset sintético PDF-first | #43 | PR #93, commit `26fef2f` |
| harness reproduzível de experimentos | #88 | PR #99, commit `1dbba5b` |
| hardening do harness | #88 | PR #101, commit `a9a0b247` |
| materialização relacional PDF-first | #39 | PR #103, commit `ec1b558`: domínio, migration inicial, repositórios e testes |
| limites do storage local sintético | #107 | ADR-0019 integrado pela PR #108 no commit `372a3a6`, com revisão futura obrigatória |

#65, #67 e #69 estão encerradas. Seus relatórios permanecem evidência histórica; não representam trabalho corrente.

## Reconciliação final da Phase 1

O gate Phase 0 → Phase 1 foi satisfeito e a entrega técnica do envelope da Epic
#26 foi integrada, reproduzida e encerrada. A reconciliação final registra:

- [x] #33 integrada pelo PR #72;
- [x] #34 integrada pelo PR #90;
- [x] #35 integrada pelo PR #91;
- [x] #36 integrada pelo PR #94;
- [x] correção de portas #96 integrada pelo PR #97 no commit `11342db`;
- [x] #37 integrada pelo squash merge do PR #98 no commit `7a39bac`;
- [x] Application CI e Structural CI verdes na entrega integrada;
- [x] imagens reconstruídas a partir da `main` com locks e pins vigentes;
- [x] API e web reproduzidas `healthy` em `127.0.0.1:8100` e `127.0.0.1:5180`;
- [x] API respondeu `{"status":"ok","service":"erp-docflow-api"}`;
- [x] web respondeu HTTP `200` em `/` e `/system`;
- [x] Jubileu permaneceu respondendo HTTP `200` em `5173`, `8000` e `8080`;
- [x] backend e frontend passaram lint, testes, typecheck e build locais;
- [x] snapshot pós-merge revisado pelo PR #100 no commit `c08d10c`;
- [x] fatos protegidos de `AGENTS.md` e `ROADMAP.md` reconciliados sob aprovação humana;
- [x] reconciliação final integrada pelo PR #102 no commit `0691aa5`;
- [x] #37/#26 encerradas com outcome `STOP`.

## Encadeamento concluído da Phase 1

```text
#33 workspace -- integrado pelo PR #72
  -> #34 backend -- integrado pelo PR #90
  -> #35 frontend -- integrado pelo PR #91
  -> #36 Compose -- integrado pelo PR #94
  -> #96 portas -- integrado pelo PR #97 / 11342db
  -> #37 CI, runbook, status e rastreabilidade -- integrado pelo PR #98 / 7a39bac
  -> reprodução concluída; snapshot integrado pelo PR #100 / c08d10c
  -> reconciliação factual final integrada pelo PR #102 / 0691aa5
  -> fechamento de #37/#26 e registro de STOP
```

| Issue | Especificação | Condição atual | Gate restante |
| --- | --- | --- | --- |
| #33 | fechada | integrada | nenhum |
| #34 | fechada | integrada | nenhum |
| #35 | fechada | integrada | nenhum |
| #36 | fechada | integrada | nenhum |
| #37 | fechada | entrega e reconciliação integradas | nenhum |

Com esta reconciliação, a Phase 1 encerra somente com o R0 técnico previsto na Epic #26.
O envelope #92 autoriza a direção PDF-first, mas não elimina o refinamento e os
gates de cada slice. A #39 foi integrada pela PR #103 no commit `ec1b558`,
satisfazendo somente o predecessor relacional. A #40 permanece bloqueada e sem
branch autorizada até o gate final do checkpoint governante #104.

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
- O harness da #88 foi integrado pelo PR #99 e endurecido pelo PR #101. #82/#83 ainda exigem refinamento próprio, e a avaliação Docling continua na #89. Nenhum provider foi promovido.
- Dados reais, secrets, deploy de produção e automerge continuam fora do escopo; ruleset/branch protection foi autorizado exclusivamente pelo checkpoint #104, mas ainda não foi aplicado.

## Regra de atualização

Atualizar este snapshot no mesmo PR que:

- autorizar, pausar ou encerrar um envelope;
- mudar o gate de uma Phase ou release;
- tornar uma slice elegível, iniciar Review ou concluir uma Epic;
- integrar a primeira evidência de código de produto;
- materializar taxonomia/automação aqui registrada como gap;
- criar ou substituir a release-alvo do produto.
