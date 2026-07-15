# ADR-0001 — On-prem first com práticas cloud-like

Status: Aceito
Data: 2026-06-22
Decisores: FelipeDalMolin
Tags: arquitetura, ambientes, on-prem, cloud-like

## Contexto

O `erp-docflow` precisa operar sob controle local, preservando documentos, auditoria, revisão humana, backup e evolução futura.

## Decisão

Adotar estratégia on-prem first com práticas cloud-like: containers, serviços separados, logs, healthchecks, variáveis de ambiente, object storage, CI/CD, backup e deploy reproduzível.

## Alternativas consideradas

Cloud first; aplicação local sem práticas cloud-like; on-prem first com práticas cloud-like.

## Consequências positivas

Maior controle operacional, caminho claro para onprem-lab/prod-onprem e evolução híbrida opcional.

## Consequências negativas / trade-offs

Maior responsabilidade local por backup, restore, segurança e operação.

## Impacto técnico

Documentação afetada: `docs/project/MODELO_OPERACIONAL_DO_PROJETO.md`, `docs/project/ROADMAP.md`, `docs/operations/AMBIENTES.md`.
Módulos/entidades/rotas: futuros; nada criado agora.
Infra: local, CI, onprem-lab e prod-onprem.
Testes necessários: validação documental nesta fase.

## Relações

Relacionado a: ADR-0002, ADR-0014.

## Critérios para revisão futura

Revisar se a operação deixar de ser prioritariamente local ou se a estratégia híbrida virar requisito principal.
