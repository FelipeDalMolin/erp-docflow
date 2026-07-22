# Estratégia de providers e modelos documentais

Status documental: proposta para decisão, não implementada  
Atualizado em: 2026-07-21
Issues de origem: #22 e #73
ADR relacionado: ADR-0016 (proposto)

## 1. Resposta arquitetural

Sim: integrações como Stirling PDF, Docling, Google Document AI, OpenAI, PaddleOCR e Tesseract devem ficar atrás de adapters/providers.

Mas o provider é vinculado a uma **capacidade**, não ao fluxo documental inteiro.

```text
errado: provider=google executa "processar documento"

planejado:
  normalize_pdf -> stirling
  probe_document + extract_native_text -> tika (OCR interno desligado)
  recognize_text -> paddleocr
  extract_layout -> docling (candidato; OCR desligado no primeiro perfil)
  extract_table_structure -> docling (candidato; execution separada)
  extract_fields -> google-document-ai
  classify_semantically -> openai
  validate_business_rules -> engine interno
  decide -> humano/política
```

Isso permite combinar local e proprietário, substituir uma etapa sem reescrever o domínio e auditar qual ferramenta produziu cada artefato.

### 1.1 Papéis que não devem ser confundidos

| Papel | Exemplo | Contrato |
| --- | --- | --- |
| engine/serviço | Tika Server, Tesseract, PaddleOCR, Document AI | executa uma capability e produz observação/raw output |
| toolkit/pipeline composto | Docling SDK ou `docling-serve` | coordena backend/modelos/subengines; cada componente e output continua explícito |
| adapter | adapter HTTP do Tika, adapter CLI/worker do OCR | traduz contrato interno ↔ ferramenta e normaliza falhas |
| binding/biblioteca | `pytesseract`, OpenCV | invoca engine ou transforma imagem; não é provider de negócio |
| regra/parser interno | regex, parser de data/`Decimal`, CPF/CNPJ | lógica determinística versionada com evidência |
| policy de seleção | provider selection policy | escolhe adapter elegível para uma capability já decidida, usando profile, benchmark, saúde, custo e residência |
| policy de workflow | `NativeTextAssessment`, `RoutingDecision` e review policy | decide o próximo passo usando observações, validações, thresholds e risco; não escolhe capability de forma implícita |
| orquestrador | task graph do profile | coordena etapas, jobs e artefatos; não interpreta o domínio sozinho |

Regex não é provider; `pytesseract` não é uma engine distinta; OpenCV não aprova documento. O [contrato de profile](PROCESSING_PROFILE_CONTRACT.md) liga cada papel a versão, parâmetros, artefatos e métricas.

## 2. Capabilities planejadas

| Capability | Entrada | Saída normalizada |
| --- | --- | --- |
| `probe_document` | arquivo/versão | MIME observado, parser, páginas/metadados, criptografia, warnings e limites |
| `extract_native_text` | arquivo digital | texto e metadados nativos disponíveis |
| `normalize_document` | original/derivado | novo arquivo derivado + relatório de transformação |
| `recognize_text` | PDF/imagem | texto, página, coordenadas e confiança disponíveis |
| `extract_layout` | PDF/imagem | blocos, hierarchy, reading order e relações |
| `extract_table_structure` | PDF/imagem/regiões | tabelas, linhas, colunas, células, spans e cabeçalhos |
| `extract_fields` | conteúdo + schema | campos tipados com evidência |
| `classify_document` | conteúdo | classes/rótulos e score |
| `summarize_document` | conteúdo | resumo referenciado |
| `embed_content` | chunks aceitos | vetores + referências |

Validação determinística, política de roteamento, review e aceite são responsabilidades internas. Mesmo que um serviço ofereça funções parecidas, ele só devolve sugestões/artefatos.

## 3. Catálogo inicial

| Provider/adapter | Implantação | Capacidades úteis | Papel recomendado | Limites |
| --- | --- | --- | --- | --- |
| Apache Tika | local/isolado | probe, texto nativo, metadados | primeira inspeção da Phase 3; OCR interno desligado | não avalia suficiência, qualidade visual ou malware; não é fronteira de segurança |
| Stirling PDF | self-hosted | normalização, split/merge/rotate/compress, OCR auxiliar | ferramenta/serviço de preparação de PDF | não substitui orquestração, domínio, validação ou auditoria |
| OCRmyPDF | local/self-hosted | limpeza e PDF pesquisável | normalização/OCR de PDFs escaneados | não entrega entendimento semântico |
| Tesseract | local | OCR | engine baseline sob benchmark | `pytesseract` é apenas binding; layout/tabelas exigem componentes adicionais |
| Docling / `docling-serve` | local/self-hosted | layout, hierarchy, reading order, tabelas e conversão estruturada; OCR configurável | challenger de `extract_layout` e `extract_table_structure` após Tika/assessment; primeiro perfil born-digital com OCR desligado | toolkit composto, modelos/cache e cold start; raw schema próprio; não substitui probe, domínio ou benchmark da engine OCR |
| PaddleOCR / PaddleOCR-VL | local, GPU/CPU conforme modelo | OCR, layout e entendimento documental | candidato local principal em perfis aprovados | operação, dependências e benchmark precisam ser validados |
| Google Document AI | cloud gerenciada | OCR, layout, key-value, tabelas, classificação e processors | escalation para perfis complexos ou processors específicos | custo, residência, credenciais, lock-in e schemas do provider |
| OpenAI multimodal/texto | cloud gerenciada | entendimento visual/semântico, extração estruturada, classificação, sumarização | inteligência seletiva após política; Structured Outputs quando aplicável | não é substituto do GED, da auditoria ou da validação determinística |
| AWS Textract | cloud gerenciada | forms, tables, queries e OCR | candidato futuro de capability | não selecionado |
| Azure Document Intelligence | cloud gerenciada | prebuilt/custom, layout, campos e tabelas | candidato futuro de capability | não selecionado |
| modelos especializados locais | local | LayoutLMv3, Donut, Table Transformer ou modelo treinado | especialização após dataset e benchmark | não entram no MVP sem caso, dados e MLOps definidos |

A presença no catálogo não torna o provider aprovado, configurado ou elegível para dados reais.

O código Docling e `docling-serve` usa licença MIT, mas pesos/modelos e dependências mantêm licenças próprias que precisam entrar no inventário/SBOM. Versão, imagem e documentação devem ser revalidadas na spike; nenhuma tag é selecionada por este catálogo.

O catálogo registra candidatos, não uma ordem obrigatória. A #83 compara estratégias permitidas antes da integração produtiva; a #48 mede regressão E2E depois que o pipeline existir.

## 4. Provider != produto

O domínio conhece contratos normalizados, IDs de execução e artefatos. SDKs e formatos proprietários ficam no adapter.

```text
Document Processing Orchestrator
  -> Capability Registry
  -> Provider Selection Policy
  -> Provider Adapter
  -> Raw Provider Response (artefato)
  -> Normalized Result
  -> Validators
  -> Workflow Routing Policy
  -> Review / accepted flow
```

Respostas brutas devem ser preservadas conforme retenção e segurança para permitir auditoria, debugging e renormalização. O domínio não deve depender delas diretamente.

### 4.1 Provider composto e outputs separados

Uma chamada física composta pode satisfazer mais de uma capability sem reintroduzir `process_document` como caixa-preta. O contrato separa:

- `ProviderInvocation`: SDK/HTTP/CLI, input, componentes, configuração, recursos, raw response e unidade de retry;
- `ProviderExecution`: exatamente uma capability, seus outputs normalizados, status e reason codes;
- múltiplas executions correlacionadas pelo mesmo `provider_invocation_ref` quando uma chamada produzir mais de um output.

A invocation registra:

- toolkit/runtime, backend e adapter;
- engine/subengine de OCR quando habilitada;
- modelos, artifacts, versões, digests, idioma e parâmetros;
- input original/derivado e cada output normalizado;
- timings/warnings por componente quando disponíveis;
- raw response/envelope comum e `derived_from`.

Para Docling, a serialização JSON preserva o modelo `DoclingDocument`, não o original nem todos os intermediários. Envelope de `ConversionResult`, partial success, erros, timings, confidence report, opções e digests são preservados separadamente quando expostos. Hierarchy, reading order e tabelas viram `DocumentStructureArtifact` com refs ao item/charspan; a proveniência espacial do toolkit complementa, mas não substitui invocation, execution, attempt, configuração e lineage operacional.

Cada `ProviderExecution` estrutural produz seu próprio `DocumentStructureArtifact` com capability explícita. Se a mesma invocation entregar layout e tabela, os artifacts compartilham raw envelope; qualquer fusão posterior é novo derivado, nunca mutação dos outputs originais.

Texto incidental do perfil #89, com OCR desligado, permanece em spans estruturais/raw e não cria um segundo `RecognitionArtifact(NATIVE)`: Tika continua autoridade de `extract_native_text`. Texto só vira `RecognitionArtifact` quando uma capability textual estiver declarada. Se o perfil Docling composto não provar origem por elemento, a saída recebe `TEXT_ORIGIN_UNRESOLVED` e não é elegível para evidência canônica/autoaceite; as alternativas são `FUSED` com refs explícitas ou OCR separado.

Docling executa depois do Tika na orquestração, mas relê o original/derivado com backend próprio; o pipeline não presume que ele consome texto do Tika. Observações independentes e custo duplicado permanecem visíveis.

Retry é definido por invocation/task. Se o toolkit não permitir repetir apenas uma capability, todos os outputs da nova invocation são versionados e o custo recomputado; resultados anteriores não são sobrescritos.

## 5. Contrato normalizado

Exemplo conceitual:

```json
{
  "schema_version": "document-analysis-result/v1alpha",
  "invocation": {
    "invocation_id": "pinv_...",
    "job_id": "job_...",
    "attempt": 2,
    "provider": "docling",
    "components": ["docling", "pdf-backend", "layout-model", "table-model"],
    "behavior_config_digest": "sha256:...",
    "runtime_image_digest": "sha256:...",
    "raw_envelope_ref": "artifact://provider/pinv_...",
    "duration_ms": 3000,
    "cold_start": false
  },
  "source": {
    "document_id": "doc_...",
    "document_version_id": "dver_...",
    "file_object_id": "file_...",
    "sha256": "..."
  },
  "executions": [
    {
      "execution_id": "pex_layout_...",
      "provider_invocation_ref": "pinv_...",
      "capability": "extract_layout",
      "experiment_manifest_ref": "exp_...",
      "benchmark_run_ref": "bench_...",
      "promotion_decision_ref": "promotion_...",
      "status": "SUCCEEDED",
      "normalized_artifact_ref": "artifact://structure/layout_..."
    },
    {
      "execution_id": "pex_table_...",
      "provider_invocation_ref": "pinv_...",
      "capability": "extract_table_structure",
      "experiment_manifest_ref": "exp_...",
      "benchmark_run_ref": "bench_...",
      "promotion_decision_ref": "promotion_...",
      "status": "SUCCEEDED",
      "normalized_artifact_ref": "artifact://structure/table_..."
    }
  ]
}
```

O contrato real só deve ser estabilizado após escolher o primeiro perfil e coletar outputs reais. `v1alpha` comunica que o exemplo ainda é de descoberta.

## 6. Requisitos do adapter

Todo adapter precisa declarar:

- ID e versão;
- capabilities suportadas;
- formatos, idiomas e limites;
- implantação local/self-hosted/cloud;
- requisitos de CPU/GPU;
- workers, threads, batch, peak RSS, cold/warm start e model/cache footprint medidos;
- política de timeout e cancelamento;
- erros normalizados e retryability;
- modelo/processor e versão;
- campos de proveniência disponíveis;
- medição de latência e custo;
- classificação de dados permitida;
- healthcheck;
- comportamento de idempotência;
- suporte a batch/assíncrono;
- política de retenção do serviço externo;
- componentes/subengines e respectivas licenças/digests quando o provider for composto;
- remote services/plugins habilitados ou bloqueados;
- modo de prefetch/offline e comportamento sem rede.

O adapter Tika também precisa declarar OCR/recursão desligados ou limitados, digest/configuração, limites de processo e ausência de acesso direto a banco/storage. A policy interna — não o adapter — produz `NativeTextAssessment`.

Se `docling-serve` for escolhido, a configuração versionada deve substituir defaults e comprovar: nenhuma porta publicada diretamente na LAN; adapter como único caller; egress e conversão por URL bloqueados; CORS não tratado como controle de segurança; autenticação interna quando aplicável; allowlist de input, target, pipeline e preset; limites explícitos de arquivo, páginas, timeout, fila, worker, threads, batch, memória, PIDs e temporários; models prefetched; remote services/plugins/UI desligados. Número de workers e compartilhamento/cache de modelos são medidos na #89, não herdados silenciosamente.

## 7. Configuração por ambiente e tenant

Credenciais e endpoints ficam fora do código. A configuração deve separar:

1. **catálogo**: adapters instalados e capabilities;
2. **elegibilidade do ambiente**: quais adapters podem rodar em local, CI, lab ou produção;
3. **política do tenant**: residência, sensibilidade e providers permitidos;
4. **processing profile**: task graph, schemas, thresholds, fallback e paralelismo dentro do job;
5. **deployment profile/resource envelope**: workers, threads, memória, cache e concorrência agregada do host;
6. **orçamento**: custo, páginas e tempo por job/tenant;
7. **estado operacional**: saúde, rate limit, admission control e circuit breaker.

Configuração comportamental que pode alterar output — profile, parâmetros, modelo, idioma, preprocessing e thresholds — recebe versão/digest e participa da promoção. Endpoints, secrets, limites do container e referências de credencial pertencem à configuração de deployment; podem variar por ambiente dentro do envelope aprovado, nunca entram no Git/manifest sensível e exigem regressão quando puderem alterar output ou disponibilidade.

O admission control host-wide é compartilhado e fail-safe entre workers/profiles; não é uma variável local de cada container. O processing profile pode limitar tarefas paralelas do próprio job, mas não ampliar o `resource_envelope` do deployment.

Uma variável global `PROVIDER=...` é insuficiente. Variáveis de ambiente podem habilitar adapters e apontar credenciais, enquanto roteamento é configuração versionada e auditável.

Exemplo ilustrativo, não contrato:

```yaml
profiles:
  invoice_pt_br:
    policy_version: 1
    native_text:
      capability: extract_native_text
      candidates: [tika]
    recognition:
      candidates: [paddleocr, tesseract]
      escalation: [google-document-ai]
    structure:
      when: [layout_required, reading_order_required]
      candidates: [docling, paddleocr-structure]
    table_structure:
      when: [tables_required]
      candidates: [docling, paddleocr-structure]
    semantic_extraction:
      candidates: [rules, google-document-ai, openai]
    gates:
      require_review_on:
        - validation_conflict
        - low_confidence_required_field
        - external_provider_forbidden
```

## 8. Política local-first

Ordem padrão a validar:

1. inspecionar e extrair texto nativo localmente;
2. normalizar somente se necessário;
3. usar reconhecimento local compatível com o perfil;
4. validar deterministicamente;
5. escalar para provider mais caro/externo apenas se a política permitir e houver ganho esperado;
6. enviar para revisão quando confiança, conflito, risco ou sensibilidade exigirem.

Local-first é uma preferência de roteamento, não dogma. Um perfil pode usar Google Document AI diretamente se benchmark, custo total, prazo e política demonstrarem vantagem.

### 8.1 Conjuntos de solução para on-prem pequeno

| Conjunto | Ganho | Perda | Posição planejada |
| --- | --- | --- | --- |
| R1 estruturado/manual | menor footprint; entrega valor sem processamento documental | automação documental limitada | caminho obrigatório do Golden Month |
| Tika + OpenCV/Tesseract seletivo | separação clara, previsibilidade e baixo acoplamento | layout, ordem de leitura e tabelas exigem componentes adicionais | baseline local a validar |
| Tika + Docling CPU seletivo born-digital + OCR como capability independente | estrutura rica e proveniência espacial sem abandonar o probe | parse duplicado, modelos/cache, cold start; OCR externo não é injetado automaticamente no pipeline Docling | candidato prioritário para a spike avançada |
| Docling composto com OCR interno explícito | texto + estrutura integrados e menos glue code | retries/benchmark por etapa mais difíceis e acoplamento a subengines | variante de spike/profile separado |
| Docling-centric para toda entrada | representação uniforme | toda entrada paga o stack avançado; menor isolamento e margem no host | não recomendado como default inicial |
| PaddleOCR/VLM/GPU | potencial para casos complexos e escala futura | hardware/operação/dependências maiores | futuro, preferencialmente em worker/host separado |

No host `small-cpu-lab` — 4 processadores lógicos, aproximadamente 12 GB de RAM, NVMe e sem GPU presumida — um provider pesado começa com um job em voo, thread/batch explícitos e execução assíncrona. Não existe sizing oficial de RAM que dispense benchmark conjunto com API, banco e storage.

Para scan/híbrido, não se presume fusão direta de JSON/TSV de Tesseract/PaddleOCR no Standard PDF Pipeline. O profile precisa escolher e testar explicitamente: Docling composto com engine registrada; PDF pesquisável derivado/auditado e reprocessado; adapter/pipeline customizado; ou Docling somente estrutural com `RecognitionArtifact` produzido separadamente.

## 9. Fallback e ensemble

Fallback deve ter motivo explícito:

- erro transitório;
- output inválido;
- campo obrigatório ausente;
- conflito de validação;
- confiança calibrada abaixo do threshold;
- profile mismatch.

Não se deve:

- repetir indefinidamente;
- enviar dado sensível a provider não elegível;
- escolher maior score bruto entre engines não calibradas;
- ocultar divergência.

Um ensemble pode comparar outputs por campo e evidência, mas precisa de regra de reconciliação. Divergência relevante gera revisão.

## 10. Confidence e benchmark

Scores de Tesseract, PaddleOCR, Document AI e LLMs não são diretamente equivalentes.

Scores/grades de conversão do Docling também são sinais do provider. Na documentação consultada em 2026-07-21, cálculos/pesos numéricos podem mudar e `table_score` ainda não está implementado; a #89 deve revalidar isso contra a versão fixada. Nenhum grade/score vira autoaceite sem versão, dataset e calibração do profile.

Avaliação por perfil precisa de:

- dataset rotulado e versionado;
- split de treino/validação/teste quando houver aprendizado;
- ground truth por campo/página/tabela;
- CER/WER para OCR;
- precision, recall e F1 por classe/campo;
- exact match e tolerância para valores;
- taxa de documento sem intervenção;
- tempo médio de revisão;
- latência, custo e consumo de recursos;
- erros por qualidade, tipo, idioma e fornecedor.

Existem três gates diferentes:

1. **benchmark pré-implementação** (#83): compara reconhecimento — texto nativo, Tesseract cru, OpenCV+Tesseract e PaddleOCR — no mesmo manifest/splits e sustenta a decisão;
2. **spike estrutural Docling** (#89): compara layout/reading order/tabelas e envelope de recursos sem tratá-lo como mais uma engine OCR;
3. **benchmark E2E/regressão** (#48): mede o task graph implementado, incluindo falha, routing, revisão, custo e latência.

Provider não deve ser promovido para implementação produtiva apenas porque sua integração antecede a #48.

Thresholds devem ser calibrados por provider, modelo, campo e perfil. “0,90” não significa a mesma qualidade em todos os providers.

## 11. Segurança e governança

Antes de habilitar provider externo:

- definir base legal/finalidade e classificação de dados;
- verificar residência, retenção e uso para treinamento;
- minimizar/redigir payload quando possível;
- criptografar trânsito;
- proteger/rotacionar secrets;
- não logar documento ou resposta integral em log comum;
- registrar envio, provider, finalidade e resultado;
- limitar páginas, custo, concorrência e timeout;
- definir plano de indisponibilidade;
- garantir deleção de temporários;
- documentar versão do modelo e mudanças relevantes.

## 12. Ciclo de vida de modelos

Provider proprietário e modelo local obedecem ao mesmo controle lógico:

```text
registrar -> avaliar -> aprovar para perfil -> observar -> comparar -> retirar
```

Troca de modelo/processor que pode alterar output deve gerar nova versão de política e avaliação. Reprocessar documentos antigos é decisão explícita; nunca ocorre silenciosamente.

Notebook e relatório manual não são unidades promovíveis. A linhagem entre benchmark, adapter, E2E e release preserva commit, dependency lock, configuração e digests de dados/modelos. Um package artifact pode ser reutilizado; se package ou imagem forem reconstruídos, o build deve ser rastreável e a regressão precisa executar sobre a imagem final, conforme [Engenharia de software para experimentos e componentes de dados](DATA_SCIENCE_ENGINEERING_LIFECYCLE.md).

## 13. O que permanece em aberto

- primeiro perfil documental e dataset de referência;
- outputs estruturais exigidos pelo primeiro perfil — layout, reading order e/ou tabelas;
- Docling SDK dedicado versus `docling-serve-cpu` e respectivo envelope de recursos;
- PaddleOCR ou Tesseract como primeira opção em cada perfil;
- processor(s) do Google Document AI a avaliar;
- casos em que OpenAI recebe imagem, texto nativo ou resultado de OCR;
- uso de OCR do Stirling versus OCRmyPDF direto;
- thresholds, calibração e orçamento;
- providers externos permitidos por tenant/sensibilidade;
- modelo de contratação/custo;
- estratégia de GPU on-prem;
- retenção das respostas brutas.

As Issues #43, #82, #83, #88 e #89 materializam profile/dataset, Tika, benchmark de reconhecimento, harness reproduzível e spike estrutural Docling. #84, #85 e #86 separam rule packs, avaliação do texto nativo e routing posterior. Essas escolhas devem vir de spike/benchmark e decisão humana, não de preferência abstrata ou curso/tutorial.

## 14. Referências oficiais para a spike Docling

- [Docling — documentação e execução local](https://docling-project.github.io/docling/)
- [Arquitetura de pipelines e backends](https://docling-project.github.io/docling/concepts/architecture/)
- [Modelo `DoclingDocument`](https://docling-project.github.io/docling/concepts/docling_document/)
- [Referência de `ProvenanceItem`](https://docling-project.github.io/docling/reference/docling_document/#docling_core.types.doc.ProvenanceItem)
- [Serialização e formatos de saída](https://docling-project.github.io/docling/concepts/serialization/)
- [Scores de confiança](https://docling-project.github.io/docling/concepts/confidence_scores/)
- [Opções avançadas, operação offline e limites de recursos](https://docling-project.github.io/docling/usage/advanced_options/)
- [`docling-serve` — configuração versionada](https://github.com/docling-project/docling-serve/blob/main/docs/configuration.md)
- [`docling-serve` — REST API](https://docling-project.github.io/docling/usage/api_server/rest_api/)

Essas referências descrevem o candidato; o commit/tag, imagem, modelos, configuração e licenças efetivamente testados ficam no `ExperimentManifest` da #89.
