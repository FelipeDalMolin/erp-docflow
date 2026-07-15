# ADR-0010 — PostgreSQL como banco relacional principal

Status: Aceito com revisão
Data: 2026-06-22
Decisores: FelipeDalMolin
Tags: banco, postgresql, persistência

## Contexto

O projeto precisará persistir documentos, versões, auditoria, revisão, financeiro e integrações.

## Decisão

PostgreSQL é a direção inicial para banco relacional principal. Esta ADR não cria persistência, schema, migrations, ORM ou conexão com banco agora.

## Alternativas consideradas

SQLite como principal; NoSQL como principal; PostgreSQL como relacional principal.

## Consequências positivas

Boa base para dados relacionais, transacionais, auditoria e consistência.

## Consequências negativas / trade-offs

Exige operação, backup, restore, migrations e estratégia de ambiente.

## Impacto técnico

Documentação afetada: `docs/project/MODELO_OPERACIONAL_DO_PROJETO.md`, `docs/operations/AMBIENTES.md`, `docs/project/ROADMAP.md`.
Módulos/entidades/rotas: futuros módulos e entidades persistidas.
Infra: Docker Compose futuro, onprem-lab, backup e restore.
Testes necessários: migrations e persistência quando houver implementação.

## Relações

Complementa: ADR-0001.
Relacionado a: ADR-0008, ADR-0012, ADR-0014.

## Revisão futura obrigatória

### Motivo da revisão futura
Validar requisitos reais de persistência e operação.
### Fase ou condição de revisão
Antes ou durante a implementação de persistência do núcleo GED.
### Gatilhos que podem mudar a decisão
Operação local, volume, backup, performance, simplicidade de MVP ou restrições do onprem-lab.
### Impactos previstos
Afeta entidades, migrations, testes, backup, restore, Docker Compose e ambientes.

## Critérios para revisão futura

Revisar antes de criar schema ou migrations.
