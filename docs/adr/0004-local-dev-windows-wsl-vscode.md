# ADR-0004 — Desenvolvimento local com Windows, WSL e VS Code

Status: Aceito
Data: 2026-06-22
Decisores: FelipeDalMolin
Tags: ambiente-local, windows, wsl, vscode

## Contexto

O desenvolvimento ocorre em Windows com WSL compartilhada entre múltiplos projetos.

## Decisão

O ambiente oficial atual é Windows host, Ubuntu-20.04 WSL compartilhada, VS Code em WSL e Docker Desktop com integração WSL2 quando necessário.

## Alternativas consideradas

Código no filesystem Windows; uma WSL por projeto; WSL Ubuntu compartilhada com isolamento por projeto.

## Consequências positivas

Melhor previsibilidade para Git, Python, Node, testes e Codex, com menor duplicação de distros.

## Consequências negativas / trade-offs

Exige manter ferramentas na WSL e separar corretamente código de dados fora do Git.

## Impacto técnico

Documentação afetada: `docs/operations/AMBIENTES.md`, `docs/operations/WSL_MULTI_PROJETOS.md`, `AGENTS.md`.
Módulos/entidades/rotas: nenhum produto criado agora.
Infra: ambiente local e Docker Compose futuro.
Testes necessários: validação documental e conferência dos paths.

## Relações

Complementa: ADR-0002.
Relacionado a: ADR-0005, ADR-0008.

## Critérios para revisão futura

Revisar em eventual migração para Ubuntu-24.04, WSL dedicada ou onprem-lab próprio.
