# ADR-0013 — Revisão humana, aceite e override

Status: Aceito com revisão
Data: 2026-06-22
Decisores: FelipeDalMolin
Tags: revisão-humana, aceite, override, ged

## Contexto

O projeto prevê automação documental, mas decisões sensíveis precisam de revisão humana, aceite ou override rastreável.

## Decisão

Revisão humana, aceite e override serão parte estrutural do fluxo GED. Esta ADR não cria workflow, tela, rota, entidade ou automação agora.

## Alternativas consideradas

Aceitar automação sem revisão; revisar tudo manualmente; combinar automação com revisão humana.

## Consequências positivas

Reduz risco de automação cega e apoia auditoria e rastreabilidade.

## Consequências negativas / trade-offs

Adiciona complexidade de estados e pode aumentar tempo operacional.

## Impacto técnico

Documentação afetada: `docs/MODELO_OPERACIONAL_DO_PROJETO.md`, `docs/ROADMAP.md`, `docs/uml/README.md`.
Módulos/entidades/rotas: futuros revisão, documentos, auditoria, usuários, aceite e override.
Infra: auditoria, logs e permissões futuras.
Testes necessários: estado, permissão e auditoria quando houver implementação.

## Relações

Complementa: ADR-0012.
Relacionado a: ADR-0015.

## Revisão futura obrigatória

### Motivo da revisão futura
Validar ergonomia e segurança do fluxo real de revisão.
### Fase ou condição de revisão
Phase 4, ao implementar workflow de revisão e aceite.
### Gatilhos que podem mudar a decisão
Experiência ruim, volume operacional, auditoria, segurança ou LGPD.
### Impactos previstos
Afeta entidades, estados, permissões, rotas, auditoria, UI e testes.

## Critérios para revisão futura

Revisar antes de implementar workflow de revisão.
