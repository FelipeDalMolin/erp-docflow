# ADR-0002 — Phase 0 antes de código de produto

Status: Aceito
Data: 2026-06-22
Decisores: FelipeDalMolin
Tags: phase-0, governança, produto

## Contexto

O projeto precisa de base operacional antes da implementação de produto.

## Decisão

Código de produto só deve começar depois da Phase 0 mínima: modelo operacional, Git, Codex, ADR baseline, rastreabilidade baseline, UML baseline, templates, CI estrutural e branch protection planejada ou configurada.

## Alternativas consideradas

Começar código imediatamente; documentar tudo antes de avançar; criar Phase 0 mínima e executável.

## Consequências positivas

Reduz decisões invisíveis, melhora rastreabilidade e cria base para revisão humana.

## Consequências negativas / trade-offs

Atrasa o início do código de produto e exige disciplina para evitar excesso documental.

## Impacto técnico

Documentação afetada: `docs/MODELO_OPERACIONAL_DO_PROJETO.md`, `docs/ROADMAP.md`, `AGENTS.md`.
Módulos/entidades/rotas: nenhum produto criado agora.
Infra: CI estrutural e branch protection futuros.
Testes necessários: validação documental.

## Relações

Complementa: ADR-0001.
Relacionado a: ADR-0003, ADR-0005, ADR-0006.

## Critérios para revisão futura

Revisar quando a Phase 0 for concluída e a Phase 1 começar.
