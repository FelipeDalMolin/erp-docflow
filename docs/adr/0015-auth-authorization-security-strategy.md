# ADR-0015 — Estratégia futura de autenticação, autorização e segurança

Status: Proposto
Data: 2026-06-22
Decisores: FelipeDalMolin
Tags: autenticação, autorização, segurança

## Contexto

O ERP/GED terá documentos, dados sensíveis, revisão humana, aceite, auditoria e possível integração externa.

## Decisão

Autenticação, autorização e segurança exigem ADR próprio antes de implementação. Esta ADR não escolhe stack, RBAC, ABAC, login, sessão, criptografia ou política de permissões.

## Alternativas consideradas

Implementar autenticação sem ADR; escolher solução agora; registrar necessidade e bloquear implementação até decisão específica.

## Consequências positivas

Evita decisão precipitada e mantém segurança como gate explícito.

## Consequências negativas / trade-offs

Não resolve autenticação nesta fase e pode bloquear funcionalidades futuras até nova decisão.

## Impacto técnico

Documentação afetada: `docs/project/MODELO_OPERACIONAL_DO_PROJETO.md`, `docs/project/ROADMAP.md`, `AGENTS.md`.
Módulos/entidades/rotas: futuros usuários, autenticação, autorização, revisão, auditoria e rotas autenticadas.
Infra: secrets, configuração, logs, auditoria e operação futura.
Testes necessários: autenticação, autorização e segurança quando houver implementação.

## Relações

Relacionado a: ADR-0013.

## Critérios para revisão futura

Criar ADR específico antes de implementar autenticação, autorização ou política de segurança.
