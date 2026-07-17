# ADR-0003 — Fluxo Git por Issue, branch, PR e revisão

Status: Aceito
Data: 2026-06-22
Decisores: FelipeDalMolin
Tags: git, issue, pull-request, revisão

## Contexto

O projeto precisa evoluir com histórico rastreável, PRs pequenos e revisão humana.

## Decisão

Usar o fluxo `Issue -> branch -> commits -> Pull Request -> CI quando existir -> review humana -> squash merge`. Trabalho direto na `main` não deve ocorrer.

## Alternativas consideradas

Commits diretos na `main`; branches longas; branch curta por Issue e PR pequeno.

## Consequências positivas

Facilita revisão, mantém histórico por slice e reduz risco de mudança fora de escopo.

## Consequências negativas / trade-offs

Exige PR até para mudanças pequenas e disciplina para manter um slice por PR.

## Impacto técnico

Documentação afetada: `docs/operations/ESTRATEGIA_GIT.md`, `docs/project/MODELO_OPERACIONAL_DO_PROJETO.md`.
Módulos/entidades/rotas: nenhum produto criado agora.
Infra: CI e branch protection futuros.
Testes necessários: validação documental.

## Relações

Complementa: ADR-0002.
Relacionado a: ADR-0005, ADR-0007.

## Critérios para revisão futura

Revisar se volume de PRs ou maturidade do projeto exigir outro fluxo.
