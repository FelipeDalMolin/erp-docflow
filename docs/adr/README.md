# ADRs

- **Classe:** governança e catálogo de decisões
- **Estado:** vigente
- **Índice derivado:** [ADR Index](../traceability/adr-index.md)

Esta pasta armazena os Architecture Decision Records do projeto.

ADR significa Architecture Decision Record.

Um ADR registra uma decisão arquitetural relevante, explicando o contexto, a decisão, alternativas consideradas e consequências.

## 1. Objetivo

Os ADRs existem para responder:

- por que tomamos esta decisão?
- quais alternativas foram consideradas?
- quais consequências aceitamos?
- quais partes do sistema são afetadas?
- quando esta decisão deve ser revisada?

## 2. Quando criar um ADR

Criar ADR quando houver decisão relevante sobre:

- arquitetura geral;
- banco de dados;
- object storage;
- autenticação;
- autorização;
- CI/CD;
- deploy;
- uso do Codex;
- revisão humana;
- aceite documental;
- modelo de documentos;
- geração documental;
- integração bancária;
- integração contábil;
- segurança;
- LGPD;
- retenção;
- auditoria;
- rastreabilidade.

## 3. Quando não criar um ADR

Não é necessário criar ADR para:

- correção de typo;
- ajuste pequeno de texto;
- mudança visual sem impacto arquitetural;
- refatoração local sem mudança de decisão;
- reorganização simples de arquivo;
- atualização de documentação sem mudança de direção.

## 4. Alteração de decisões

ADRs não devem ser tratados como documentos vivos comuns.

Se a decisão mudou de forma relevante, criar novo ADR.

O ADR antigo deve permanecer no histórico.

O novo ADR deve referenciar o antigo.

O ADR antigo deve ser marcado como:

```text
Substituído
Complementado
Obsoleto
```

conforme o caso.

## 5. Status previstos

Status possíveis:

```text
Proposto
Aceito
Aceito com revisão
Rejeitado
Substituído
Complementado
Obsoleto
```

`Aceito com revisão` significa que a decisão está aceita como direção inicial do projeto, pode orientar implementação futura, mas deve ser reavaliada em uma fase, milestone ou condição futura explicitamente registrada.

Usar:

- `Aceito` para decisões já consolidadas e aplicadas;
- `Aceito com revisão` para decisões adotadas como direção inicial, mas dependentes de validação no MVP, capacidade operacional, experiência de uso ou evolução técnica;
- `Proposto` para hipóteses futuras que ainda não devem orientar implementação obrigatória.

Todo ADR com status `Aceito com revisão` deve conter:

```markdown
## Revisão futura obrigatória

### Motivo da revisão futura

### Fase ou condição de revisão

### Gatilhos que podem mudar a decisão

### Impactos previstos
```

## 6. Estrutura sugerida de ADR

```markdown
# ADR-000X — Título

Status:
Data:
Decisores:
Tags:

## Contexto

## Decisão

## Alternativas consideradas

## Consequências positivas

## Consequências negativas / trade-offs

## Impacto técnico

### Documentação afetada

### Módulos afetados

### Entidades afetadas

### Rotas afetadas

### Infra afetada

### Testes necessários

## Relações

Substitui:
Substituído por:
Complementa:
Complementado por:
Relacionado a:

## Critérios para revisão futura
```

## 7. Nome dos arquivos

Formato recomendado:

```text
0001-on-prem-first-cloud-like.md
0002-modular-monolith.md
0003-document-envelope.md
```

## 8. Relação com rastreabilidade

Todo ADR relevante deve ser listado em:

[ADR Index](../traceability/adr-index.md)

Quando aplicável, também deve aparecer em:

[Decision Map](../traceability/decision-map.md), [Module Map](../traceability/module-map.md), [Entity Map](../traceability/entity-map.md), [Route Map](../traceability/route-map.md) e [Impact Matrix](../traceability/impact-matrix.md).

## 9. Catálogo

| ADR | Status | Tema |
| --- | --- | --- |
| [ADR-0001](0001-on-prem-first-cloud-like.md) | Aceito | on-prem first e cloud-like |
| [ADR-0002](0002-phase-0-before-product-code.md) | Aceito | baseline operacional antes do código |
| [ADR-0003](0003-git-flow-issue-branch-pr-review.md) | Aceito | Issue, branch, PR e revisão |
| [ADR-0004](0004-local-dev-windows-wsl-vscode.md) | Aceito | Windows, WSL e VS Code |
| [ADR-0005](0005-controlled-codex-usage.md) | Aceito | uso controlado do Codex |
| [ADR-0006](0006-adr-and-traceability-governance.md) | Aceito | ADRs e rastreabilidade |
| [ADR-0007](0007-structural-ci-and-branch-protection.md) | Aceito com revisão | CI estrutural e branch protection |
| [ADR-0008](0008-docker-compose-for-local-and-onprem-lab.md) | Aceito com revisão | Docker Compose local/onprem-lab |
| [ADR-0009](0009-modular-monolith-initial-architecture.md) | Aceito com revisão | modular monolith |
| [ADR-0010](0010-postgresql-primary-relational-database.md) | Aceito com revisão | PostgreSQL |
| [ADR-0011](0011-s3-compatible-object-storage-minio.md) | Aceito com revisão | object storage S3-compatible |
| [ADR-0012](0012-document-envelope-ged-core.md) | Aceito com revisão | `DocumentEnvelope` |
| [ADR-0013](0013-human-review-acceptance-and-override.md) | Aceito com revisão | revisão, aceite e override |
| [ADR-0014](0014-backup-and-restore-required.md) | Aceito com revisão | backup e restore |
| [ADR-0015](0015-auth-authorization-security-strategy.md) | Proposto | autenticação, autorização e segurança |
| [ADR-0016](0016-capability-based-document-processing-providers.md) | Proposto | capabilities e providers |
| [ADR-0017](0017-codex-continuous-slice-loop.md) | Aceito | loop contínuo de slices |
| [ADR-0018](0018-codex-envelope-lifecycle-and-outcomes.md) | Aceito | lifecycle do envelope e outcomes exclusivos |

O catálogo oferece navegação. O [ADR Index](../traceability/adr-index.md) mantém relações, decisão curta e gatilho de revisão.

## 10. Diretriz final

ADRs preservam memória técnica.

O objetivo não é burocratizar o projeto, mas evitar decisões invisíveis, contraditórias ou difíceis de revisar.
