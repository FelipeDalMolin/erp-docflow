# Baseline conceitual do modelo documental

Status documental: modelo planejado, não implementado  
Atualizado em: 2026-07-10  
Issue de origem: #22  
ADRs relacionados: ADR-0010, ADR-0011, ADR-0012, ADR-0013, ADR-0015 e ADR-0016 (proposto)

## 1. Escopo

Este documento define identidades, responsabilidades e invariantes conceituais. Não define tabelas, colunas, ORM, migrations, endpoints ou payloads públicos.

## 2. Separações obrigatórias

```text
arquivo original != documento
documento != versão
versão != conteúdo reconhecido
resultado de modelo != dado aceito
dado aceito != lançamento financeiro
log técnico != trilha de auditoria
índice de busca != fonte da verdade
```

Essas separações são o mecanismo central para versionamento, auditoria e substituição de providers.

## 3. Agregados e entidades planejadas

### 3.1 DocumentEnvelope

Identidade e ciclo de vida do documento materializado.

Responsabilidades:

- possuir identidade estável;
- apontar versão corrente e snapshots aceitos;
- registrar origem e estado;
- agrupar versões, processamento, decisões e vínculos;
- preservar tenant e classificação de acesso;
- expor correlação sem incorporar blobs ou payloads extensos.

Invariantes:

- existe ao menos uma versão;
- original não é reescrito;
- mudança de estado é auditável;
- interpretação aceita referencia versão e evidência;
- vínculo financeiro não transfere propriedade do documento ao módulo financeiro.

### 3.2 DocumentVersion

Representa uma versão material do documento.

Pode ser:

- `ORIGINAL`;
- `NORMALIZED_DERIVATIVE`;
- `GENERATED`;
- `CORRECTED_RENDITION`, se futuramente permitido.

Cada versão referencia um ou mais `FileObject`, motivo de criação, versão anterior quando aplicável e ator/processo responsável.

### 3.3 FileObject

Referência a objeto binário armazenado.

Metadados conceituais:

- ID;
- storage key opaca;
- SHA-256;
- tamanho;
- MIME detectado;
- nome original separado da chave;
- criptografia/classificação;
- data e fonte;
- estado de integridade;
- referência de retenção.

O storage key não deve carregar dado sensível desnecessário.

### 3.4 ProcessingJob e ProcessingAttempt

`ProcessingJob` representa um objetivo de processamento para uma versão e perfil. `ProcessingAttempt` representa cada execução.

Responsabilidades:

- task graph e versão de política;
- estado, prioridade e correlação;
- attempts, provider executions e erros;
- idempotência;
- tempo, custo e retry;
- saída/artefatos produzidos.

Nova tentativa não altera resultados históricos.

### 3.5 ProviderExecution

Registra a execução de uma capability por adapter/modelo.

Precisa referenciar:

- job e attempt;
- capability;
- provider/adapter;
- modelo/processor e versão;
- input e hash;
- configuração/policy version;
- status, timestamps e latência;
- custo/uso;
- artefato bruto;
- resultado normalizado;
- erro e retryability.

### 3.6 DocumentProbe

Resultado da inspeção anterior ao OCR:

- MIME;
- páginas;
- texto nativo;
- qualidade;
- orientação;
- proteção/corrupção;
- sinais de tabelas/imagens;
- flags de segurança e limites.

### 3.7 RecognitionArtifact

Texto/layout observado em uma versão ou derivado:

- conteúdo por página;
- blocos/linhas/palavras;
- bounding boxes;
- idioma e orientação;
- confiança;
- provider execution;
- artefato de origem.

Pode existir mais de um por versão.

### 3.8 ExtractionResult

Conjunto de campos e entidades propostos para um schema.

Cada `ExtractedField` preserva:

- nome e tipo;
- valor bruto e normalizado;
- confiança;
- evidência;
- página/coordenadas;
- warnings;
- provider/rule de origem.

### 3.9 ClassificationResult

Classes e rótulos propostos:

- taxonomy/schema version;
- classe;
- score;
- evidências;
- alternativas;
- provider execution.

### 3.10 ValidationResult

Saída de regras determinísticas:

- regra e versão;
- escopo/field;
- `PASS`, `FAIL`, `WARN` ou `NOT_APPLICABLE`;
- evidência;
- severidade;
- mensagem segura;
- dados usados por referência.

### 3.11 RoutingDecision

Explica por que o fluxo continuou, escalou, solicitou revisão, reprocessou ou bloqueou:

- versão da política;
- sinais considerados;
- decisão;
- candidates elegíveis/ineligíveis;
- motivo;
- budgets;
- próximo passo.

### 3.12 ReviewCase e ReviewDecision

`ReviewCase` agrupa o trabalho humano. `ReviewDecision` registra uma ação imutável.

Uma decisão inclui:

- ação;
- revisor/ator;
- timestamp;
- valores antes/depois;
- justificativa;
- permissões/dupla aprovação aplicáveis;
- evidências vistas;
- policy/schema version;
- relação com decisão anterior.

### 3.13 AcceptedSnapshot

Interpretação canônica aceita para uma finalidade e versão.

O snapshot:

- copia ou referencia valores aceitos;
- registra decisão que o criou;
- é versionado;
- pode ser sucedido, não sobrescrito;
- não altera o original;
- é a fonte preferida para vínculos e read models.

### 3.14 EntityLink

Relaciona documento/snapshot a entidade externa ao núcleo documental.

Exemplos planejados:

- fornecedor;
- cliente;
- contrato;
- lançamento financeiro;
- pagamento;
- conta/centro de custo;
- documento relacionado.

O link tem tipo, estado (`SUGGESTED`, `CONFIRMED`, `REJECTED`, `SUPERSEDED`), origem, confiança/decisão e audit trail.

### 3.15 AuditEvent

Registro lógico append-only de fato relevante:

- quem/o quê;
- ação;
- alvo;
- quando;
- motivo;
- correlation/causation ID;
- antes/depois ou referências;
- origem técnica;
- classificação de acesso.

AuditEvent não deve ser confundido com log de aplicação. Logs podem expirar; auditoria segue retenção própria.

## 4. Relações conceituais

```text
DocumentEnvelope
  1 -> N DocumentVersion
  1 -> N ProcessingJob
  1 -> N ReviewCase
  1 -> N AcceptedSnapshot
  1 -> N EntityLink

DocumentVersion
  1 -> N FileObject
  1 -> N DocumentProbe
  1 -> N RecognitionArtifact
  1 -> N ExtractionResult
  1 -> N ClassificationResult

ProcessingJob
  1 -> N ProcessingAttempt
ProcessingAttempt
  1 -> N ProviderExecution

ExtractionResult / ClassificationResult
  1 -> N ValidationResult

ReviewCase
  1 -> N ReviewDecision
ReviewDecision
  0..1 -> 1 AcceptedSnapshot
```

## 5. Estado documental planejado

Estado do envelope e estado do processamento não devem ser misturados.

### 5.1 Envelope

```text
RECEIVED
MATERIALIZED
PROCESSING
REVIEW_REQUIRED
ACCEPTED
LINKED
ARCHIVED
REJECTED
QUARANTINED
```

O desenho exato e transições estão em [document-envelope-state-planned.puml](uml/06-state/document-envelope-state-planned.puml).

### 5.2 Job

```text
QUEUED
RUNNING
WAITING_RETRY
WAITING_REVIEW
SUCCEEDED
FAILED
CANCELLED
DEAD_LETTER
```

O desenho está em [processing-job-state-planned.puml](uml/06-state/processing-job-state-planned.puml).

## 6. Versionamento

Quatro eixos precisam de versão independente:

| Eixo | Exemplo |
| --- | --- |
| conteúdo material | versão original ou derivado normalizado |
| interpretação | extraction/classification/accepted snapshot |
| configuração | profile, routing policy e schema |
| executor | adapter, modelo e processor version |

Reproduzir um resultado exige registrar os quatro. “Processado em 10/07” sem modelo, policy e input hash não é proveniência suficiente.

## 7. Deduplicação

Camadas diferentes:

- **binária**: mesmo SHA-256;
- **documental**: mesmo documento em versões/arquivos diferentes;
- **negocial**: mesma nota, cobrança ou evento;
- **de ingestão**: mesma entrega repetida pelo canal.

Ações de merge/deduplicação precisam preservar ocorrências, origem e decisões. Hash igual ajuda, mas não resolve sozinho identidade documental ou de negócio.

## 8. Consistência e transações

Planejamento:

- banco relacional é fonte de estado;
- object storage mantém binários;
- alterações de estado e eventos usam mecanismo transacional/outbox quando implementados;
- fila é meio de entrega, não fonte única;
- efeitos operacionais usam idempotency key;
- concorrência usa version/optimistic locking ou estratégia equivalente;
- índices de busca são reconstruíveis.

## 9. Dados sensíveis

Todo conceito deverá suportar:

- `tenant_id`;
- classificação de acesso;
- política de retenção;
- data residency;
- actor/service principal;
- campos mascarados para observabilidade;
- deleção/anonimização quando legalmente aplicável;
- legal hold quando aplicável.

Definições finais dependem do ADR sucessor do ADR-0015.

## 10. Perguntas antes do schema físico

- qual é o primeiro tipo documental?
- qual granularidade de versionamento é necessária?
- payloads de layout ficam em JSONB ou object storage?
- quais estados são canônicos e quais são read models?
- qual regra de retenção e descarte?
- como representar tenant e segregação?
- quais decisões exigem dupla aprovação?
- um snapshot aceito pode servir a múltiplas finalidades?
- como modelar correções concorrentes?
- qual mecanismo de outbox/fila?
- quais campos precisam de índice relacional?

Nenhuma migration deve ser criada antes de responder ao mínimo necessário para o primeiro slice da Phase 2.

