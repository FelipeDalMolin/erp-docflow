# Contrato de perfil de processamento documental

Status documental: contrato planejado, não implementado
Atualizado em: 2026-07-21
Issue de origem: #73
ADRs relacionados: ADR-0012, ADR-0013, ADR-0015 e ADR-0016 (proposto)

## 1. Finalidade e autoridade

Este documento define o conteúdo mínimo, o ciclo de vida e os critérios de validação de um **perfil de processamento documental**. Ele complementa o [pipeline documental](DOCUMENT_PIPELINE.md), a [estratégia de providers](PROVIDER_STRATEGY.md) e o [baseline de dados](DATA_MODEL_BASELINE.md).

Um perfil é configuração versionada de um caso documental. Ele descreve entradas, task graph, schemas, regras, candidates, budgets, gates e benchmark. Não é código arbitrário, provider global, autorização para dado real nem evidência de implementação.

Enquanto o [ADR-0016](../adr/0016-capability-based-document-processing-providers.md) permanecer `Proposto`, este contrato orienta discovery, fixtures e benchmark. A integração produtiva de um provider exige decisão e Issue próprias.

## 2. Posição do Tika no fluxo

O Apache Tika tem uma posição estável e restrita:

| Momento | Responsabilidade |
| --- | --- |
| Phase 1 | nenhuma; bootstrap de API, web, Compose de desenvolvimento e CI |
| Phase 2 | nenhuma execução profunda; intake preserva original, hash, origem e observações preliminares |
| Phase 3 inicial | `probe_document` e `extract_native_text`, com OCR interno desabilitado |
| Phase 3 evoluída | continua primeiro; somente conteúdo insuficiente segue para normalização/OCR |
| leitura de derivado | pode reler uma camada textual gerada por OCR, marcada como derivada, nunca como nativa do original |

O Tika observa MIME, metadados, parsers acionados e texto nativo. Ele não:

- decide suficiência do texto;
- produz confiança de negócio;
- mede sozinho qualidade visual, resolução ou deskew;
- substitui antivírus;
- executa regex, linking, validação ou aceite;
- transforma XLSX/CSV em fatos gerenciais.

A suficiência pertence a `NativeTextAssessment`, uma política interna versionada pelo perfil.

## 3. Observações de MIME não destrutivas

Três observações devem coexistir:

| Campo planejado | Origem | Momento |
| --- | --- | --- |
| `advertised_mime` | cliente/canal de entrada | intake |
| `intake_detected_mime` | inspeção leve aprovada | intake |
| `probe_detected_mime` | adapter de `probe_document`, inicialmente Tika | processamento |

`mime_mismatch` é uma divergência auditável. Um valor posterior não sobrescreve o anterior. O perfil define quando a divergência gera continuação, revisão ou quarentena.

## 4. Artefatos contratuais

### 4.1 DocumentProbe

Resultado normalizado de inspeção:

- referência ao original e SHA-256;
- MIME observado e parser utilizado;
- número de páginas quando disponível;
- metadados permitidos;
- presença e distribuição de texto nativo;
- criptografia, corrupção, limite excedido e warnings;
- adapter, versão, configuração e `ProviderExecution`;
- referência à resposta bruta, sujeita a retenção.

Observações que dependam de ferramentas próprias — qualidade visual, orientação, malware ou estrutura de página — devem identificar o inspector que as produziu.

### 4.2 RecognitionArtifact

Conteúdo textual/layout observado, com origem explícita:

| `origin` | Significado |
| --- | --- |
| `NATIVE` | texto extraído do original pelo parser nativo |
| `OCR` | texto reconhecido a partir de imagem/derivado |
| `FUSED` | composição por página/região, preservando todas as origens |
| `OCR_DERIVED_TEXT_LAYER` | camada textual de PDF derivado; não é texto nativo |

Bounding boxes e scores só existem quando a capability realmente os fornece. Um artefato nativo não deve inventar coordenadas nem confidence.

### 4.3 EvidenceRef

Referência mínima de evidência de campo:

- `evidence_id` e tipo;
- documento, versão e artefato de conteúdo;
- página e região, quando existentes;
- trecho permitido ou hash do trecho;
- regra/provider e versão;
- relação `derived_from` quando houver transformação.

A cadeia posterior até fatos e relatórios é definida em [EVIDENCE_TO_REPORT_LINEAGE.md](EVIDENCE_TO_REPORT_LINEAGE.md).

### 4.4 NativeTextAssessment

Decisão interna posterior ao probe:

```text
USE_NATIVE
OCR_REQUIRED
REVIEW_REQUIRED
QUARANTINE
```

Ela registra `policy_version`, sinais medidos, thresholds aplicados e reason codes. Exemplos de sinais, sempre calibrados por perfil:

- cobertura de páginas com texto;
- quantidade/distribuição de caracteres;
- proporção de caracteres inválidos;
- presença de campos/âncoras mínimas;
- divergência de MIME;
- conteúdo híbrido;
- proteção, corrupção ou limite excedido.

Não existe threshold universal de “texto suficiente”.

## 5. Estrutura mínima do perfil

Exemplo conceitual `v1alpha`; não é schema estabilizado:

```yaml
profile_id: payable_document_pt_br
profile_version: 1
status: candidate

applicability:
  accepted_mime: [application/pdf, image/png, image/jpeg]
  languages: [pt-BR]
  max_pages: 20
  data_classification: internal

schemas:
  extraction: payable_document/v1alpha
  taxonomy: document_type/v1alpha

task_graph:
  - id: probe
    capability: probe_document
    candidates: [tika]
  - id: native_text
    capability: extract_native_text
    candidates: [tika]
  - id: assess_native
    internal_policy: native_text_assessment/v1
  - id: recognize
    when: OCR_REQUIRED
    capability: recognize_text
    candidates: [candidate_from_benchmark]
  - id: extract
    internal_rule_pack: payable_document_rules/v1
  - id: classify
    internal_registry: document_classification/v1
    outcomes: [CLASSIFIED, UNKNOWN, ABSTAIN]
  - id: validate
    internal_rule_pack: payable_document_validators/v1
  - id: route
    internal_policy: document_routing/v1

gates:
  review_on: [required_field_missing, validation_conflict, hybrid_unresolved]
  quarantine_on: [encrypted_without_key, corrupt_input, resource_limit]

budgets:
  timeout_seconds: 120
  max_attempts: 2
  max_external_cost: {currency: BRL, amount: "0.00"}

benchmark:
  dataset_manifest: datasets/payable_document/v1/manifest.yaml
  acceptance_policy: benchmarks/payable_document/v1/acceptance.yaml
```

O manifesto real não deve conter segredo nem dado pessoal indevido. Paths são ilustrativos e só podem ser criados por slice autorizada.

## 6. Estratégias e algoritmos candidatos

| Etapa | Baseline/candidatos | Saída/controlador |
| --- | --- | --- |
| probe e texto nativo | Tika local | `DocumentProbe`, `RecognitionArtifact(NATIVE)` |
| normalização visual | OpenCV/OCRmyPDF/Stirling, conforme benchmark | derivado imutável + relatório de transformação |
| OCR | Tesseract via binding ou PaddleOCR como candidates | `RecognitionArtifact(OCR)` |
| extração determinística | Unicode NFKC, âncoras, regex nomeadas e parsers tipados | campos brutos/normalizados + `EvidenceRef` |
| validação | módulo 11, datas pt-BR, `Decimal`, totals e consistência | `PASS`, `WARN`, `FAIL`, `NOT_APPLICABLE` |
| classificação | regras/keywords; TF-IDF + modelo linear quando justificado | classe, alternativas e score calibrado |
| linking | identificador exato, aliases e fuzzy apenas como sugestão | candidates e ambiguidade explícita |
| roteamento | política interna versionada | `RoutingDecision` |

`pytesseract`, quando usado, é binding da engine Tesseract. Regex, parsers e validators são regras internas versionadas, não providers.

## 7. Benchmark antes da escolha

Nenhum provider padrão ou threshold é promovido antes de benchmark reproduzível. A spike inicial deve comparar, conforme o perfil:

- texto nativo disponível;
- Tesseract sem preprocessing;
- preprocessing aprovado + Tesseract;
- PaddleOCR ou outro challenger elegível;
- escalation externa somente quando o [gate de segurança](../adr/0015-auth-authorization-security-strategy.md) permitir.

O `DatasetManifest` registra:

- origem permitida, licença/finalidade e classificação;
- hashes e versão das fixtures;
- grupos born-digital, escaneado, híbrido e falhas;
- ground truth e protocolo de anotação;
- splits sem vazamento;
- hardware, SO, container/image digest e configuração;
- métricas e tolerâncias por campo/perfil.

Métricas mínimas: CER/WER, exact match/tolerância por campo, precision/recall/F1, taxa de revisão, latência, memória/CPU, falhas e custo. O benchmark final do task graph é regressão; não substitui a comparação anterior à escolha.

## 8. Execução isolada do Tika

A integração inicial planejada usa Tika Server interno chamado por worker:

- inacessível diretamente pela UI ou rede externa;
- sem credenciais de PostgreSQL ou object storage;
- OCR embutido explicitamente desabilitado;
- recursos embutidos desabilitados ou limitados pelo perfil;
- timeout, memória, CPU, tamanho, temporários e recursão limitados;
- usuário sem privilégio e filesystem temporário controlado;
- versão, configuração e image digest registrados;
- resposta bruta referenciada e resultado normalizado persistido;
- cancelamento, erro e retry normalizados.

A versão exata deve ser revalidada e fixada imediatamente antes da implementação. Este documento não seleciona tag nem digest.

## 9. Reason codes mínimos

```text
NATIVE_TEXT_SUFFICIENT
NATIVE_TEXT_ABSENT
NATIVE_TEXT_PARTIAL
HYBRID_CONTENT
MIME_MISMATCH
ENCRYPTED_INPUT
CORRUPT_INPUT
UNSUPPORTED_FORMAT
RESOURCE_LIMIT_EXCEEDED
PROVIDER_TIMEOUT
PROVIDER_OUTPUT_INVALID
REQUIRED_FIELD_MISSING
VALIDATION_CONFLICT
EXTERNAL_PROVIDER_FORBIDDEN
REVIEW_POLICY_TRIGGERED
```

Erro técnico, decisão de roteamento e validação de negócio são dimensões separadas. “Sucesso vazio” não é resultado válido.

## 10. Fixtures obrigatórias

Cada perfil candidato inclui, no mínimo:

- PDF born-digital;
- PDF somente imagem;
- PDF híbrido;
- imagem rotacionada ou degradada, se aplicável;
- arquivo criptografado;
- arquivo corrompido;
- MIME anunciado divergente;
- formato não suportado;
- limite de páginas/tamanho excedido;
- campo obrigatório ausente;
- duplicata por hash/idempotency key.

Fixtures reais exigem autorização. Preferir dados sintéticos ou anonimizados com manifestação de origem.

## 11. Versionamento e promoção

Versionar independentemente:

- perfil e task graph;
- schema de extração e taxonomia;
- rule packs e policies;
- adapter, engine/modelo e configuração;
- dataset e ground truth;
- política de aceitação do benchmark.

Mudança que pode alterar output cria nova versão. Promoção segue:

```text
DRAFT -> CANDIDATE -> BENCHMARKED -> APPROVED -> DEPRECATED -> RETIRED
```

Somente decisão humana registrada promove `BENCHMARKED` para `APPROVED`. Reprocessamento histórico nunca é automático.

## 12. Fronteira com importação estruturada

XLSX, CSV, OFX e CNAB usam parsers estruturados próprios. O arquivo-fonte pode ser materializado para integridade e evidência, mas o texto do Tika não é entrada para converter células ou movimentos em fatos. O contrato específico está em [STRUCTURED_IMPORT_PIPELINE.md](STRUCTURED_IMPORT_PIPELINE.md).

## 13. Definition of Ready para uma slice Codex

Uma implementação baseada neste contrato só pode ficar elegível quando a Issue informar:

- perfil, versão e caso de negócio;
- inputs, outputs e invariantes;
- paths e ownership;
- capability e tecnologia decidida versus candidate;
- fixture manifest permitido;
- artefatos persistidos e retenção;
- timeouts, retries e reason codes;
- métricas e targets verificáveis;
- comandos exatos de lint, testes, contract tests e benchmark;
- condições de `CONTINUE`, `AWAIT_DEPENDENCY`, `CHECKPOINT` e `STOP`;
- gates de segurança, dados e provider externo.

## 14. Critérios de aceite do contrato implementado

- [ ] Tika executa somente probe/texto nativo no baseline aprovado.
- [ ] OCR interno do Tika permanece desligado.
- [ ] `DocumentProbe`, artefato nativo, assessment e routing são objetos separados.
- [ ] raw output, normalizado, versão e configuração possuem proveniência.
- [ ] OCR só é executado por reason code/política observável.
- [ ] regras, parsers e validators têm versão e fixtures.
- [ ] benchmark anterior à escolha pode ser reproduzido.
- [ ] falhas não geram sucesso vazio nem apagam attempts.
- [ ] nenhum dado real ou provider externo é usado sem gate aplicável.
