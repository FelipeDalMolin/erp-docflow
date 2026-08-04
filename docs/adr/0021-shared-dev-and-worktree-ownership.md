# ADR-0021 — Ownership do shared-dev e isolamento por worktrees

Status: Proposto
Data: 2026-08-04
Decisores: FelipeDalMolin
Tags: dev, compose, worktree, shared-dev, runtime

## Contexto

Os ADRs 0004 e 0008 definem perfis locais e Docker Compose, mas não determinam
quem pode controlar um runtime cumulativo quando existem múltiplas worktrees.
No app-host, o Compose atual usa nome, portas e bind mounts compartilháveis, o
que permite trocar o código montado sem mudar a identidade aparente do runtime.

O checkpoint #104 reservou esta decisão para distinguir checkout canônico,
worktrees de slice, checks descartáveis e cutover operacional.

## Pergunta decisória

Qual checkout é proprietário do `shared-dev` em cada perfil e quais guards,
labels, rehearsals e regras de rollback impedem uma worktree de assumir o
runtime ou banco compartilhado?

## Decisão pendente

Esta proposta não altera o runtime, Compose, portas, volumes ou worktrees. A
topologia somente orientará implementação após decisão e revisão humanas.

## Alternativas a avaliar

- checkout canônico em `main` como único owner do runtime cumulativo;
- worktree dedicada e imutável para o runtime integrado;
- nenhum runtime cumulativo, apenas ambientes descartáveis por execução.

## Impactos a decidir

- perfis `app-host` e `personal-wsl`, roots esperadas e paths proibidos;
- semântica de `shared status`, `preflight`, `up`, `migrate` e `restart`;
- checks/rehearsals isolados, portas e volumes nomeados descartáveis;
- identidade por labels, mounts, path, SHA e árvore limpa;
- dump/restore, cutover, forward-fix e rollback em volume separado.

## Relações

Substitui: nenhum.
Substituído por: —
Complementa: ADR-0004 e ADR-0008.
Complementado por: —
Relacionado a: ADR-0001, ADR-0003, ADR-0010 e ADR-0014.

## Critérios para aceitação

- inventário vivo dos perfis, worktrees e runtime atual;
- owner e guards fail-closed definidos por perfil;
- isolamento comprovável de rede, porta e volume;
- migration rehearsal e rollback sem reutilização cega do banco;
- revisão humana antes do primeiro cutover.
