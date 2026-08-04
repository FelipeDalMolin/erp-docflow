# ADR-0020 — Ruleset, revisão humana e método de merge da main

Status: Proposto
Data: 2026-08-04
Decisores: FelipeDalMolin
Tags: github, ruleset, review, ci, merge

## Contexto

O ADR-0007 determinou CI estrutural antes de branch protection. O repositório
já possui CI estrutural e CI da aplicação, mas reviews acionáveis recentes
foram registrados depois de merges. O checkpoint #104 reservou esta decisão
para transformar o fluxo documentado em proteção efetiva sem exigir checks ou
aprovações que ainda não possam ser satisfeitos.

## Pergunta decisória

Qual ruleset deve proteger a `main`, como ocorrerão os dois cutovers e qual
evidência comprova revisão humana, checks recentes, resolução de conversas e
squash-only?

## Decisão pendente

Nenhuma configuração do GitHub é alterada por esta reserva. O status
`Proposto` não autoriza branch protection, bypass ou mudança nos métodos de
merge.

## Alternativas a avaliar

- ruleset em dois cutovers, começando pelos checks existentes;
- proteção única somente após todos os novos checks e segundo revisor;
- branch protection clássica em vez de ruleset, se a capacidade disponível exigir.

## Impactos a decidir

- PR obrigatório, branch atualizada, conversas resolvidas e histórico linear;
- checks obrigatórios e requisito de execução verde recente;
- uma aprovação humana, dismiss de aprovações obsoletas e permissão mínima do revisor;
- squash-only, auto-merge, force-push, deleção e política de bypass;
- snapshots, teste do ruleset e rollback de configuração.

## Relações

Substitui: nenhum.
Substituído por: —
Complementa: ADR-0007.
Complementado por: —
Relacionado a: ADR-0003, ADR-0005, ADR-0017 e ADR-0018.

## Critérios para aceitação

- inventário vivo de checks, colaboradores e configuração atual;
- delta exato dos Cutovers A e B;
- dependência organizacional do segundo revisor explicitada;
- procedimento de emergência sem bypass cotidiano;
- revisão humana antes de qualquer mutação do ruleset.
