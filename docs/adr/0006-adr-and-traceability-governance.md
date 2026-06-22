# ADR-0006 — Governança de ADRs e rastreabilidade

Status: Aceito
Data: 2026-06-22
Decisores: FelipeDalMolin
Tags: adr, rastreabilidade, governança

## Contexto

O projeto precisa preservar memória técnica e relacionar decisões com documentação, módulos, entidades, rotas, diagramas, Issues e PRs.

## Decisão

Decisões relevantes devem virar ADR. ADR aceito não é documento vivo comum; mudança relevante exige novo ADR relacionado ao anterior.

## Alternativas consideradas

Decisões apenas no chat; editar ADRs aceitos livremente; registrar ADRs e manter mapas.

## Consequências positivas

Preserva contexto, evita decisões invisíveis e facilita análise de impacto.

## Consequências negativas / trade-offs

Exige manutenção documental contínua.

## Impacto técnico

Documentação afetada: `docs/adr/README.md`, `docs/traceability/README.md`.
Módulos/entidades/rotas: futuros, quando existirem.
Infra: CI, deploy, ambientes e segurança deverão ser rastreados quando mudarem.
Testes necessários: validação documental.

## Relações

Complementa: ADR-0002.
Relacionado a: todos os ADRs do baseline.

## Follow-up S0.06

A S0.06 deve criar ou atualizar `adr-index.md`, `decision-map.md`, `document-map.md`, `impact-matrix.md`, `module-map.md`, `entity-map.md` e `route-map.md`.

Esta ADR não cria mapas de rastreabilidade.

## Critérios para revisão futura

Revisar quando os mapas forem criados ou quando a regra de evolução de ADRs mudar.
