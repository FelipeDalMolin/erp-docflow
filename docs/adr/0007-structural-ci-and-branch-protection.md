# ADR-0007 — CI estrutural antes de branch protection

Status: Aceito com revisão
Data: 2026-06-22
Decisores: FelipeDalMolin
Tags: ci, branch-protection, phase-0

## Contexto

A Phase 0 prevê CI estrutural inicial e branch protection planejada ou configurada antes de código de produto.

## Decisão

Criar CI estrutural antes de configurar branch protection. Esta ADR não configura CI nem branch protection.

## Alternativas consideradas

Branch protection antes do CI; CI completo desde o início; CI estrutural mínimo e revisão depois.

## Consequências positivas

Evita proteção sem checks úteis e permite amadurecer validações aos poucos.

## Consequências negativas / trade-offs

A `main` ainda depende de disciplina humana até a proteção ser aplicada.

## Impacto técnico

Documentação afetada: `docs/AMBIENTES.md`, `docs/ESTRATEGIA_GIT.md`, `docs/ROADMAP.md`.
Módulos/entidades/rotas: nenhum produto criado agora.
Infra: GitHub Actions e branch protection futuros.
Testes necessários: validação documental; testes de CI virão em slice própria.

## Relações

Complementa: ADR-0003.
Relacionado a: ADR-0002.

## Revisão futura obrigatória

### Motivo da revisão futura
Confirmar se os checks estruturais são suficientes para proteger a `main`.
### Fase ou condição de revisão
Após criação do CI estrutural inicial e antes de branch protection.
### Gatilhos que podem mudar a decisão
CI instável, checks insuficientes, necessidade de proteção imediata ou mudança no fluxo Git.
### Impactos previstos
Afeta PRs, merges, CI, documentação Git e critérios de saída da Phase 0.

## Critérios para revisão futura

Revisar junto da slice de CI estrutural ou branch protection.
