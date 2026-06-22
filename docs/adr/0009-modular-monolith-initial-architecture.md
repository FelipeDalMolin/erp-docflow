# ADR-0009 — Arquitetura inicial como modular monolith

Status: Aceito com revisão
Data: 2026-06-22
Decisores: FelipeDalMolin
Tags: arquitetura, modular-monolith

## Contexto

O ERP/GED terá documentos, revisão, auditoria, financeiro, geração documental e integrações, mas não deve começar distribuído demais.

## Decisão

A arquitetura inicial será modular monolith, com módulos separados por responsabilidade e implantação inicialmente coesa.

## Alternativas consideradas

Monolito sem separação modular; microservices desde o início; modular monolith.

## Consequências positivas

Reduz complexidade operacional inicial e mantém limites internos claros.

## Consequências negativas / trade-offs

Exige disciplina para manter limites entre módulos e pode demandar extração futura.

## Impacto técnico

Documentação afetada: `docs/MODELO_OPERACIONAL_DO_PROJETO.md`, `docs/ROADMAP.md`.
Módulos/entidades/rotas: futuros, conforme produto surgir.
Infra: bootstrap app futuro.
Testes necessários: testes de módulo e integração quando houver código.

## Relações

Complementa: ADR-0001.
Relacionado a: ADR-0012, ADR-0013.

## Revisão futura obrigatória

### Motivo da revisão futura
Validar se os limites modulares reais estão claros no MVP.
### Fase ou condição de revisão
Após bootstrap app e primeiros módulos de produto.
### Gatilhos que podem mudar a decisão
Acoplamento excessivo, necessidade de separar workers/serviços ou crescimento de integrações.
### Impactos previstos
Afeta estrutura de pastas, módulos, testes, deploy futuro e rastreabilidade.

## Critérios para revisão futura

Revisar antes de qualquer decisão de extrair serviços.
