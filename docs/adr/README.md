# ADRs

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
Rejeitado
Substituído
Complementado
Obsoleto
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

```text
docs/traceability/adr-index.md
```

Quando aplicável, também deve aparecer em:

```text
docs/traceability/decision-map.md
docs/traceability/module-map.md
docs/traceability/entity-map.md
docs/traceability/route-map.md
docs/traceability/impact-matrix.md
```

## 9. Diretriz final

ADRs preservam memória técnica.

O objetivo não é burocratizar o projeto, mas evitar decisões invisíveis, contraditórias ou difíceis de revisar.