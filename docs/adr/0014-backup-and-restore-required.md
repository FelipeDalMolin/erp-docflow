# ADR-0014 — Backup e restore obrigatórios

Status: Aceito com revisão
Data: 2026-06-22
Decisores: FelipeDalMolin
Tags: backup, restore, onprem-lab, operação

## Contexto

O projeto armazenará documentos, metadados, logs relevantes, configurações e histórico operacional.

## Decisão

Backup e restore são obrigatórios antes de qualquer operação on-prem real. Esta ADR não cria scripts, jobs, deploy, storage ou automação de backup agora.

## Alternativas consideradas

Backup depois da produção; backup manual sem restore testado; exigir estratégia e teste antes da operação real.

## Consequências positivas

Reduz risco de perda de documentos e obriga validação de restore.

## Consequências negativas / trade-offs

Aumenta trabalho antes de produção e exige disciplina operacional.

## Impacto técnico

Documentação afetada: `docs/AMBIENTES.md`, `docs/ROADMAP.md`.
Módulos/entidades/rotas: futuros documentos, storage, banco, auditoria e dados persistidos.
Infra: PostgreSQL futuro, object storage futuro, onprem-lab e prod-onprem.
Testes necessários: teste real de restore quando houver dados e storage.

## Relações

Complementa: ADR-0001.
Relacionado a: ADR-0008, ADR-0010, ADR-0011.

## Revisão futura obrigatória

### Motivo da revisão futura
Definir estratégia concreta quando existirem banco, storage e onprem-lab.
### Fase ou condição de revisão
Antes de operação contínua em onprem-lab e antes de qualquer prod-onprem.
### Gatilhos que podem mudar a decisão
Mudança de banco, storage, volume de documentos, retenção ou exigência legal.
### Impactos previstos
Afeta infraestrutura, documentação operacional, testes, segurança e recuperação de desastre.

## Critérios para revisão futura

Revisar antes de automatizar backup ou declarar ambiente operacional.
