# Baseline conceitual do modelo documental

Status documental: modelo planejado, não implementado  
Atualizado em: 2026-07-21
Issues de origem: #22 e #73
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
score bruto != score calibrado
texto nativo != camada textual derivada de OCR
evidência != verdade automática
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
- `advertised_mime` informado pelo canal;
- `intake_detected_mime` preliminar;
- `mime_mismatch` preservado;
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
- `ProcessingProfileRef` com ID, versão e digest;
- estado, prioridade e correlação;
- attempts, provider executions e erros;
- idempotência;
- tempo, custo e retry;
- saída/artefatos produzidos.

Nova tentativa não altera resultados históricos.

### 3.5 ProviderInvocation e ProviderExecution

`ProviderInvocation` representa uma chamada física a SDK, CLI ou serviço. Ela registra:

- job, attempt, input/hash e runtime/image digest;
- toolkit/backend/engine/subengine/modelos em `components`;
- configuração comportamental e envelope operacional separados;
- status, timestamps, duração real, classificação cold/warm e observações brutas de CPU/memória/temporários;
- raw response/envelope, erro e retryability.

`ProviderExecution` representa exatamente uma capability normalizada produzida pela invocation. Ela referencia:

- `provider_invocation_ref`, capability e provider/adapter;
- input, configuração/policy version e componentes/modelos relevantes;
- commit, dependency lock e digests da configuração comportamental/modelos;
- `experiment_manifest_ref`, `benchmark_run_ref` e `promotion_decision_ref`;
- status, reason code, outputs declarados e estados `not_run`/`not_available`;
- raw artifact/envelope e resultado normalizado por referência;
- erro e retryability daquela capability.

Uma invocation composta cria um `ProviderExecution` por capability e os correlaciona pelo mesmo `provider_invocation_ref`. Retry da chamada física cria nova invocation; outputs anteriores não são sobrescritos. Se o toolkit não permitir retry parcial, a unidade indivisível e o custo repetido ficam explícitos.

### 3.5.1 Evidência de experimento e promoção

Artifacts de evaluation não são estado do documento nem efeito de negócio:

- `ExperimentManifest`: hipótese, commit, dataset/splits, configuração, hardware, runner e artifacts;
- `BenchmarkRun`: métricas de qualidade/recursos e diferenças contra baseline;
- `PromotionDecision`: refs a um ou mais benchmark runs, capability/profile, pacote/configuração/digests autorizados, limites, fallback e owner.

O runtime referencia a decisão/execução aprovada; não recria código a partir do notebook. O contrato completo está em [Engenharia de software para experimentos e componentes de dados](DATA_SCIENCE_ENGINEERING_LIFECYCLE.md).

### 3.6 DocumentProbe

Resultado da inspeção anterior ao OCR:

- `probe_detected_mime`, sem sobrescrever os MIME do intake;
- parser, versão/configuração/digest;
- páginas;
- texto/metadados nativos observados;
- proteção/corrupção;
- warnings, limites e reason codes;
- referência à resposta bruta e resultado normalizado.

Qualidade visual, orientação/resolução e malware pertencem a inspetores/controles próprios. `DocumentProbe` não carrega “confiança Tika”.

### 3.6.1 NativeTextAssessment

Decisão interna, separada do Tika, que aplica profile/policy às observações:

- `USE_NATIVE`;
- `OCR_REQUIRED`;
- `REVIEW_REQUIRED`;
- `QUARANTINE`;
- policy/threshold version;
- sinais e reason codes;
- escopo documento/página/região;
- próximo passo.

### 3.7 RecognitionArtifact

Texto observado em uma versão ou derivado:

- origem `NATIVE`, `OCR`, `FUSED` ou `OCR_DERIVED_TEXT_LAYER`;
- conteúdo por página;
- linhas/palavras e blocos textuais quando fornecidos pelo reconhecimento;
- bounding boxes;
- idioma e orientação;
- score bruto e, quando existir, score calibrado separados;
- provider execution;
- artefato de origem e `derived_from`;
- cadeia de transformações, algoritmo/configuração e versões.

Pode existir mais de um por versão.

### 3.7.1 DocumentStructureArtifact

Estrutura observada por capability separada de reconhecimento:

- capability `extract_layout` ou `extract_table_structure` e um `provider_execution_ref` produtor;
- blocos/classes, hierarchy e reading order;
- páginas, bounding boxes, origem/sistema de coordenadas e transformação interna;
- tabelas, linhas, colunas, células, spans e cabeçalhos;
- `provider_item_ref`/JSON Pointer e `charspan` quando disponíveis;
- vínculos com `RecognitionArtifact` quando disponíveis;
- provider invocation/execution, outputs produzidos ou `not_run`/`not_available`, raw artifact, warnings e confidence/grades brutos;
- source artifact, `derived_from`, modelo/configuração e versões.

Raw schemas como `DoclingDocument` permanecem na borda. Sua serialização pode preservar o modelo do provider sem representar o original, o envelope da conversão ou todos os intermediários; esses registros são correlacionados separadamente. O artifact normalizado não substitui `EvidenceRef`, snapshot aceito ou lineage operacional.

Existe um `DocumentStructureArtifact` por execution/capability. Quando uma invocation física gerar layout e tabela, ela origina artifacts distintos que podem compartilhar raw envelope; qualquer visão fusionada é novo artifact com `derived_from` explícito.

### 3.8 ExtractionResult

Conjunto de campos e entidades propostos para um schema.

Cada `ExtractedField` preserva:

- nome e tipo;
- valor bruto e normalizado;
- confiança;
- score bruto/calibrado separados quando aplicável;
- `EvidenceRef`;
- página/coordenadas;
- warnings;
- provider/rule de origem.

### 3.8.1 EvidenceRef

Referência verificável e tipada à origem de uma afirmação/campo. Pode apontar para:

- documento, versão e página/região/trecho;
- arquivo estruturado, lote, aba, linha e célula;
- lançamento manual, ator, horário e justificativa;
- evento/registro de integração;
- artefato derivado e cadeia `derived_from`.

Ela registra tipo de origem, IDs/hashes, localização, transformações, regra/profile/modelo e versão. `EvidenceRef` sustenta auditoria e drill-through; não declara que o valor está aceito.

### 3.9 ClassificationResult

Classes e rótulos propostos:

- taxonomy/schema version;
- classe;
- score;
- score bruto e calibrado separados;
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
  1 -> N NativeTextAssessment
  1 -> N RecognitionArtifact
  1 -> N DocumentStructureArtifact
  1 -> N ExtractionResult
  1 -> N ClassificationResult

ProcessingJob
  1 -> N ProcessingAttempt
ProcessingAttempt
  1 -> N ProviderInvocation
ProviderInvocation
  1 -> 1..N ProviderExecution

ExperimentManifest
  1 -> N BenchmarkRun
PromotionDecision
  1 -> 1..N BenchmarkRun (evidências)
  1 -> 0..N ProviderExecution (runtime elegível)

ExtractionResult / ClassificationResult
  1 -> N ValidationResult
  1 -> N EvidenceRef

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
INSPECTION_PENDING
PROCESSING
REVIEW_REQUIRED
ACCEPTED
LINKED
ARCHIVED
REJECTED
QUARANTINED
```

O desenho exato e transições estão em [document-envelope-state-planned.puml](../uml/06-state/document-envelope-state-planned.puml).

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

O desenho está em [processing-job-state-planned.puml](../uml/06-state/processing-job-state-planned.puml).

## 6. Versionamento

Quatro eixos precisam de versão independente:

| Eixo | Exemplo |
| --- | --- |
| conteúdo material | versão original ou derivado normalizado |
| interpretação | extraction/classification/accepted snapshot |
| configuração | processing profile, rule pack, routing policy e schema |
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
- qual representação mínima de `EvidenceRef` atende documento e linha estruturada?
- quais scores exigem calibração e como a versão é registrada?

Nenhuma migration deve ser criada antes de responder ao mínimo necessário para o primeiro slice da Phase 2.

Domínio gerencial, importação, lineage e fechamento possuem baselines especializados:

- [Domínio financeiro-gerencial](MANAGERIAL_FINANCIAL_DOMAIN.md)
- [Pipeline de importação estruturada](STRUCTURED_IMPORT_PIPELINE.md)
- [Lineage de evidência a relatório](EVIDENCE_TO_REPORT_LINEAGE.md)
- [Fechamento e entrega contábil](ACCOUNTING_CLOSE_AND_DELIVERY.md)
