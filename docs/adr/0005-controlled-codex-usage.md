# ADR-0005 — Uso controlado do Codex

Status: Aceito
Data: 2026-06-22
Decisores: FelipeDalMolin
Tags: codex, revisão, automação-controlada

## Contexto

O Codex apoia execução e revisão, mas o projeto exige rastreabilidade, escopo claro e revisão humana.

## Decisão

Usar Codex com autonomia alta controlada por Issue, branch, PR e revisão humana. O uso principal é a extension no VS Code remoto WSL; CLI é opcional.

## Alternativas consideradas

Não usar Codex; usar sem regras persistidas; usar com `AGENTS.md` e configuração operacional.

## Consequências positivas

Acelera escrita/revisão e preserva controle humano.

## Consequências negativas / trade-offs

Exige Issues claras, revisão humana e parada quando houver decisão arquitetural pendente.

## Impacto técnico

Documentação afetada: `AGENTS.md`, `.codex/config.toml`, `docs/MODELO_OPERACIONAL_DO_PROJETO.md`.
Módulos/entidades/rotas: nenhum produto criado agora.
Infra: ambiente local e fluxo de PR.
Testes necessários: validação documental e conferência da configuração Codex.

## Relações

Complementa: ADR-0003, ADR-0004.
Relacionado a: ADR-0006.

## Critérios para revisão futura

Revisar quando a configuração operacional do Codex ou o modelo de revisão humana mudar.
