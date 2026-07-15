# ADR-0008 — Docker Compose para local e onprem-lab

Status: Aceito com revisão
Data: 2026-06-22
Decisores: FelipeDalMolin
Tags: docker-compose, local, onprem-lab

## Contexto

O projeto prevê execução local futura e validação em onprem-lab antes de produção on-prem.

## Decisão

Docker Compose será direção inicial para orquestração local e onprem-lab. Esta ADR não cria compose, serviços, volumes ou containers.

## Alternativas consideradas

Serviços manuais; Kubernetes desde o início; Docker Compose inicial.

## Consequências positivas

Facilita reprodução local e aproxima desenvolvimento de laboratório on-prem.

## Consequências negativas / trade-offs

Não substitui estratégia de produção madura e exige cuidado com volumes, secrets e backup.

## Impacto técnico

Documentação afetada: `docs/operations/AMBIENTES.md`, `docs/operations/WSL_MULTI_PROJETOS.md`, `docs/project/ROADMAP.md`.
Módulos/entidades/rotas: futuros backend, frontend, banco, storage e workers.
Infra: ambiente local e onprem-lab.
Testes necessários: futuro `docker compose config`.

## Relações

Complementa: ADR-0004.
Relacionado a: ADR-0010, ADR-0011, ADR-0014.

## Revisão futura obrigatória

### Motivo da revisão futura
Validar se Compose atende ao bootstrap app e ao onprem-lab.
### Fase ou condição de revisão
Phase 1, ao criar a aplicação mínima e o Compose inicial.
### Gatilhos que podem mudar a decisão
Serviços persistentes complexos, isolamento maior, limitações de Docker Desktop ou requisito operacional diferente.
### Impactos previstos
Afeta ambiente local, onprem-lab, documentação de execução, backup e restore.

## Critérios para revisão futura

Revisar quando existir o primeiro Compose funcional.
