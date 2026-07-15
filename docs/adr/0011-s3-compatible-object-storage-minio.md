# ADR-0011 — Object storage S3-compatible

Status: Aceito com revisão
Data: 2026-06-22
Decisores: FelipeDalMolin
Tags: object-storage, s3-compatible, minio, documentos

## Contexto

O projeto precisa armazenar documentos originais, arquivos gerados, versões e objetos associados ao GED.

## Decisão

S3-compatible como direção futura; MinIO como candidato preferencial on-prem. Esta ADR não torna MinIO obrigatório para o MVP e não cria object storage agora.

## Alternativas consideradas

Filesystem local; storage proprietário de nuvem desde o início; interface S3-compatible com candidato on-prem.

## Consequências positivas

Mantém portabilidade entre on-prem e nuvem e apoia versionamento, backup e restore de objetos.

## Consequências negativas / trade-offs

Exige operação de storage, backup/restore de objetos e cuidado com credenciais.

## Impacto técnico

Documentação afetada: `docs/project/MODELO_OPERACIONAL_DO_PROJETO.md`, `docs/operations/AMBIENTES.md`, `docs/project/ROADMAP.md`.
Módulos/entidades/rotas: futuros arquivos, versões, upload e download.
Infra: Docker Compose futuro, onprem-lab, backup e restore.
Testes necessários: upload, download, versionamento, backup e restore quando houver implementação.

## Relações

Complementa: ADR-0001.
Relacionado a: ADR-0008, ADR-0012, ADR-0014.

## Revisão futura obrigatória

### Motivo da revisão futura
Validar se S3-compatible e MinIO atendem ao MVP e ao onprem-lab.
### Fase ou condição de revisão
Antes do upload documental real e dos testes de backup/restore.
### Gatilhos que podem mudar a decisão
Limitações operacionais do MinIO, storage existente, restrições de backup ou necessidade híbrida.
### Impactos previstos
Afeta storage, entidades de arquivo, upload, download, backup, restore e documentação operacional.

## Critérios para revisão futura

Revisar antes de criar integração real com object storage.
