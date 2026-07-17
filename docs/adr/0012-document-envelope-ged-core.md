# ADR-0012 — DocumentEnvelope como núcleo GED

Status: Aceito com revisão
Data: 2026-06-22
Decisores: FelipeDalMolin
Tags: ged, documento, documentenvelope

## Contexto

O GED precisa materializar documentos, versões, arquivos, metadados, revisão, aceite e auditoria de forma rastreável.

## Decisão

`DocumentEnvelope` será direção inicial para o núcleo de materialização documental. Esta ADR não cria código, entidade, tabela, rota ou workflow agora.

## Alternativas consideradas

Arquivos soltos; entidades específicas por tipo documental desde o início; envelope documental comum.

## Consequências positivas

Cria conceito central para versionamento, rastreabilidade, revisão, aceite, OCR e vínculos futuros.

## Consequências negativas / trade-offs

Pode exigir refinamento quando casos reais surgirem; um núcleo mal definido pode acoplar módulos demais.

## Impacto técnico

Documentação afetada: `docs/project/MODELO_OPERACIONAL_DO_PROJETO.md`, `docs/project/ROADMAP.md`, `docs/uml/README.md`.
Módulos/entidades/rotas: futuros documentos, arquivos, revisão, OCR, auditoria, upload e consulta.
Infra: banco, object storage, workers e backup futuros.
Testes necessários: domínio e integração quando houver implementação.

## Relações

Complementa: ADR-0009.
Relacionado a: ADR-0010, ADR-0011, ADR-0013.

## Revisão futura obrigatória

### Motivo da revisão futura
Validar o modelo com o primeiro fluxo real de upload e materialização documental.
### Fase ou condição de revisão
Phase 2, ao modelar entidades e fluxo inicial do núcleo GED.
### Gatilhos que podem mudar a decisão
Casos de uso reais, tipos documentais diferentes, versionamento ou revisão.
### Impactos previstos
Afeta entidades, módulos, rotas, UMLs, testes e mapas de rastreabilidade.

## Critérios para revisão futura

Revisar antes de implementar entidades do núcleo GED.
