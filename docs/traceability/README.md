# Rastreabilidade

Esta pasta armazena os mapas de rastreabilidade do projeto.

A rastreabilidade conecta decisões, documentação, módulos, entidades, rotas, diagramas, Issues e Pull Requests.

## 1. Objetivo

A rastreabilidade existe para responder:

- qual decisão justifica esta parte do sistema?
- qual ADR afeta este módulo?
- qual entidade está relacionada a este fluxo?
- qual rota altera esta entidade?
- qual diagrama representa este comportamento?
- qual documentação precisa ser atualizada se esta decisão mudar?
- qual Issue ou PR introduziu determinada alteração?

## 2. Por que isso importa

Este projeto combina ERP e GED.

Isso significa que teremos:

- documentos;
- arquivos;
- versões;
- OCR;
- extrações;
- revisões;
- aceite humano;
- auditoria;
- lançamentos financeiros;
- pagamentos;
- geração documental;
- integrações.

Sem rastreabilidade, o sistema pode virar um conjunto de arquivos, rotas, tabelas e decisões difíceis de relacionar.

## 3. Mapas previstos

Arquivos previstos:

```text
adr-index.md
decision-map.md
module-map.md
route-map.md
entity-map.md
document-map.md
impact-matrix.md
```

## 4. adr-index.md

Lista todos os ADRs, seus status e relacionamentos.

Deve responder:

- quais ADRs existem?
- quais estão aceitos?
- quais foram substituídos?
- quais foram complementados?

## 5. decision-map.md

Mostra relações entre decisões.

Exemplo:

```text
ADR-0001 — On-prem first
├── ADR-0003 — Object storage
├── ADR-0008 — Docker Compose
└── ADR-0010 — Backup
```

## 6. module-map.md

Relaciona módulos do sistema com responsabilidades, ADRs e documentação.

Exemplo futuro:

```text
documents
├── Responsabilidade: DocumentEnvelope
├── ADRs: ADR-0003, ADR-0005
├── Docs: DOCUMENT_WORKFLOW.md
└── Entidades: DocumentEnvelope, DocumentVersion
```

## 7. route-map.md

Relaciona rotas com módulos, entidades e ADRs.

Exemplo futuro:

```text
POST /documents/upload
├── Módulo: documents/files
├── Entidades: DocumentEnvelope, FileObject
├── ADRs: ADR-0003, ADR-0004
└── Descrição: cria documento materializado
```

## 8. entity-map.md

Relaciona entidades com tabelas, módulos, state machines e ADRs.

Exemplo futuro:

```text
DocumentEnvelope
├── Tabela: documents
├── Módulo: documents
├── State machine: sim
└── ADRs: ADR-0004
```

## 9. document-map.md

Relaciona documentos de arquitetura com ADRs, UMLs, módulos e fases.

Exemplo futuro:

```text
DOCUMENT_WORKFLOW.md
├── ADRs: ADR-0004, ADR-0005
├── UMLs: document-workflow-activity.puml
└── Módulos: documents, review, audit
```

## 10. impact-matrix.md

Ajuda a avaliar impacto de mudanças.

Exemplo futuro:

```text
Mudança: storage oficial
Afeta:
- ADR de storage
- FileObject
- DocumentVersion
- upload
- backup
- restore
- MinIO
```

## 11. Quando atualizar rastreabilidade

Atualizar rastreabilidade quando houver mudança em:

- ADR;
- módulo;
- entidade;
- rota;
- fluxo;
- diagrama UML;
- infraestrutura;
- workflow documental;
- CI/CD;
- segurança;
- integração.

## 12. Diretriz final

A rastreabilidade deve ser leve, mas constante.

Não precisa ser perfeita no início, mas deve existir desde a Phase 0 para evitar perda de contexto.