# UML

Esta pasta armazena diagramas do projeto.

Os diagramas ajudam a representar arquitetura, fluxos, entidades, estados e interações entre componentes.

## 1. Objetivo

Os diagramas existem para tornar o sistema mais compreensível antes, durante e depois da implementação.

Eles devem apoiar:

- entendimento arquitetural;
- revisão de decisões;
- onboarding futuro;
- análise de impacto;
- comunicação com Codex;
- documentação de fluxos;
- validação de estados;
- planejamento de entidades e rotas.

## 2. Tipos de diagramas previstos

Tipos previstos:

```text
contexto
deployment
casos de uso
atividades
componentes
classes de domínio
sequência
estados
```

## 3. Estrutura prevista

Estrutura esperada:

```text
docs/uml/
├── 01-context/
├── 02-business/
├── 03-application/
├── 04-domain/
├── 05-sequence/
└── 06-state/
```

## 4. Diagramas de contexto

Representam o sistema em relação a usuários, ferramentas externas e integrações.

Exemplos:

- usuário operacional;
- administrador;
- contador;
- Google Drive;
- OneDrive;
- e-mail;
- banco;
- storage externo.

## 5. Diagramas de deployment

Representam onde os componentes rodam.

Exemplos:

- ambiente local;
- onprem-lab;
- prod-onprem;
- NGINX;
- API;
- frontend;
- workers;
- PostgreSQL;
- Redis;
- MinIO.

## 6. Diagramas de atividades

Representam fluxos de negócio.

Exemplos:

- upload documental;
- OCR;
- extração;
- classificação;
- revisão humana;
- aceite;
- geração de lançamento;
- arquivamento como evidência.

## 7. Diagramas de componentes

Representam blocos técnicos da aplicação.

Exemplos futuros:

- frontend;
- backend;
- documents module;
- files module;
- review module;
- audit module;
- finance module;
- OCR worker;
- generation worker.

## 8. Diagramas de classes de domínio

Representam entidades principais.

Exemplos futuros:

- DocumentEnvelope;
- DocumentVersion;
- FileObject;
- OCRResult;
- ExtractionResult;
- ClassificationResult;
- ReviewDecision;
- AcceptanceCheck;
- FinancialEntry;
- PaymentIntent;
- AuditEvent.

## 9. Diagramas de sequência

Representam interações entre usuário, frontend, backend, workers, banco e storage.

Exemplos futuros:

- upload até DocumentEnvelope;
- OCR, Extract e Classify;
- Review, Override e Acceptance;
- criação de FinancialEntry;
- geração de recibo ou contrato.

## 10. Diagramas de estados

Representam ciclos de vida.

Exemplos futuros:

- DocumentEnvelope;
- ProcessingJob;
- ReviewDecision;
- AcceptanceCheck;
- FinancialEntry;
- PaymentIntent;
- GeneratedDocument.

## 11. Relação com ADRs

Sempre que possível, diagramas devem indicar ADRs relacionados.

Exemplo:

```plantuml
' Related ADRs:
' - ADR-0004 DocumentEnvelope
' - ADR-0005 Human review and acceptance
```

## 12. Relação com rastreabilidade

Diagramas relevantes devem ser citados nos mapas de rastreabilidade.

Especialmente em:

```text
decision-map.md
module-map.md
entity-map.md
document-map.md
impact-matrix.md
```

## 13. Formato

O formato preferencial será PlantUML ou Mermaid.

A escolha final pode variar conforme a ferramenta e a facilidade de renderização no GitHub ou no VS Code.

## 14. Diretriz final

Diagramas não devem ser desenhos decorativos.

Eles devem ajudar a entender, revisar e manter o sistema.