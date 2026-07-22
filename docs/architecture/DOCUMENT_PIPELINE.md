# Pipeline documental canônico

Status documental: fluxo planejado, não implementado  
Atualizado em: 2026-07-21
Issues de origem: #22 e #73
ADRs relacionados: ADR-0012, ADR-0013 e ADR-0016 (proposto)

## 1. Finalidade

Este documento define o ramo **documental** da entrada até o uso autorizado. XLSX/CSV e outras fontes estruturadas seguem o [pipeline de importação estruturada](STRUCTURED_IMPORT_PIPELINE.md); lançamento manual e integrações também preservam origem sem imitar OCR.

O fluxo é um **task graph orientado por política**. Algumas etapas podem ser dispensadas, repetidas ou mudar de ordem conforme perfil documental, mas os artefatos e decisões continuam separados.

## 2. Fluxo de alto nível

```text
capturar
  -> materializar documento e original
  -> Tika: probe + texto nativo
  -> política: avaliar suficiência
      -> usar nativo
      -> normalizar + OCR seletivo
      -> revisão ou quarentena
  -> compor artefato nativo/OCR/híbrido
  -> extrair estrutura/layout/tabelas quando o perfil exigir
  -> extrair e classificar
  -> validar
  -> decidir rota
      -> autoaceite permitido
      -> revisão humana
      -> reprocessamento
      -> rejeição/quarentena
  -> registrar snapshot aceito
  -> sugerir vínculos
  -> autorizar efeito operacional
  -> indexar/integrar
```

## 3. Etapas e saídas

| Etapa | Objetivo | Saída persistida | Pode ser pulada? |
| --- | --- | --- | --- |
| 1. Capture | receber upload ou referência de uma fonte | `IngestionRecord` planejado | não |
| 2. Materialize | criar envelope, versão original, objeto e hash | `DocumentEnvelope`, `DocumentVersion`, `FileObject` | não |
| 3. Probe | observar MIME, metadados, páginas, criptografia, parser e texto nativo | `DocumentProbe` + raw response referenciada | não |
| 4. Native text | extrair texto já existente sem OCR | `RecognitionArtifact` de origem nativa | sim |
| 5. Assess | avaliar suficiência por profile/policy, sem inventar confiança do Tika | `NativeTextAssessment` | não |
| 6. Normalize | corrigir rotação, páginas, PDF e imagem sem perder original | `DerivedFileObject` + transformação/versionamento | sim |
| 7. Recognize | produzir texto e coordenadas disponíveis por OCR | `RecognitionArtifact` de origem OCR | sim, se `USE_NATIVE` |
| 8. Fuse | compor por página/região sem sobrescrever origens | `RecognitionArtifact` de origem `FUSED` | sim |
| 9. Structure | observar blocos, hierarchy, reading order e tabelas/células | `DocumentStructureArtifact` + raw response referenciada | conforme saídas exigidas pelo perfil |
| 10. Extract | propor campos e entidades com proveniência | `ExtractionResult` | conforme perfil |
| 11. Classify | propor tipo, rótulos e destino | `ClassificationResult` | conforme perfil |
| 12. Validate | executar regras, reconciliações e detectar conflitos | `ValidationResult` | não para campos operacionais |
| 13. Route | aplicar thresholds, risco, custo e política | `RoutingDecision` | não |
| 14. Review | aceitar, corrigir, override, rejeitar ou reprocessar | `ReviewDecision` | somente se política permitir |
| 15. Accept | congelar interpretação canônica aprovada | `AcceptedSnapshot` | não antes de uso oficial |
| 16. Link/effectuate | propor vínculo ou criar efeito autorizado | relação/entidade de destino + auditoria | conforme caso |
| 17. Index/export | publicar read models, índice/RAG ou integração | referência de publicação | conforme caso |

Nomes de entidades são baseline conceitual, não schema ou classes implementadas.

## 4. Intake e materialização documental

### 4.1 Canais planejados

- upload pela Inbox Documental;
- pasta monitorada;
- e-mail;
- Google Drive;
- OneDrive;
- API ou integração futura.

Somente upload precisa existir no primeiro slice de produto. Os demais canais entram pelas mesmas portas lógicas e não podem contornar hash, versionamento, política ou auditoria.

### 4.2 Regras de entrada

1. Identificar fonte, ator técnico/humano, tenant e horário.
2. Calcular SHA-256 do conteúdo recebido.
3. Registrar `advertised_mime` informado pelo canal e `intake_detected_mime` por inspeção preliminar segura.
4. Preservar `mime_mismatch`; não sobrescrever um valor com o outro.
5. Verificar idempotência e possível duplicidade sem apagar ocorrências legítimas.
6. Armazenar original como objeto imutável.
7. Criar `DocumentEnvelope` e versão original.
8. Encerrar o intake como `INSPECTION_PENDING` e registrar correlação.

Duplicidade de binário não significa necessariamente duplicidade de evento de negócio. A política pode reaproveitar o objeto físico, mantendo duas ocorrências/auditorias separadas.

## 5. Probe Tika e avaliação de texto nativo

O pipeline não deve rasterizar todos os PDFs.

O Tika nasce na Phase 3 e permanece no início do ramo documental. Um worker chama um Tika Server interno para as capabilities `probe_document` e `extract_native_text`, com OCR interno desabilitado.

O `DocumentProbe` registra observações como:

- `probe_detected_mime`, sem apagar os MIME anteriores;
- texto extraível e parser utilizado;
- número de páginas;
- criptografia/senha;
- warnings, falha/corrupção observada e limites;
- metadados e presença de recursos embutidos quando permitidos;
- tamanho e limites operacionais;
- versão, configuração e digest do serviço.

Orientação, resolução e qualidade visual pertencem a inspetores de imagem. Malware pertence a controle de segurança separado. Tika não é antivírus, não é fronteira de segurança e não produz “confiança Tika”.

O serviço deve operar:

- apenas em rede interna e de forma assíncrona;
- sem credenciais ou acesso direto a PostgreSQL/object storage;
- com timeout, CPU, memória, tamanho, temporários e recursão limitados;
- com recursos embutidos desabilitados ou limitados por profile;
- com resposta bruta referenciada e saída normalizada;
- sem transformar vazio, parcial ou limite excedido em sucesso silencioso.

Uma policy interna avalia o conteúdo observado e persiste `NativeTextAssessment`:

```text
USE_NATIVE
OCR_REQUIRED
REVIEW_REQUIRED
QUARANTINE
```

Se o texto nativo for suficiente para o perfil, OCR pode ser dispensado. Isso reduz custo, latência e perda de qualidade.

Posteriormente, o mesmo Tika continua primeiro. A avaliação pode evoluir para página/região; somente unidades insuficientes seguem ao OCR seletivo. Quando OCRmyPDF/Stirling gerar camada pesquisável, texto relido pelo Tika recebe origem `OCR_DERIVED_TEXT_LAYER`, nunca `NATIVE`.

## 6. Normalização

Normalização produz um derivado; nunca substitui o original.

Capacidades possíveis:

- OpenCV: grayscale, deskew, denoise, contraste, threshold Otsu/adaptativo e morfologia, conforme profile/benchmark;
- rotação e seleção de orientação por inspetor próprio;
- split/merge;
- remoção ou seleção de páginas;
- conversão para PDF/A ou formato aceito;
- compressão controlada;
- limpeza de imagem;
- geração de PDF pesquisável;
- saneamento de metadados conforme política.

Cada transformação registra operação, parâmetros, versão, entrada, saída e `derived_from`. OpenCV é biblioteca de transformação, não provider de negócio.

Stirling PDF é candidato self-hosted de manipulação/normalização e OCR auxiliar em adapter separado. Ele não executa o papel do orquestrador, do modelo de domínio, da validação ou da revisão humana.

## 7. Reconhecimento

`RecognitionArtifact` representa conteúdo observado, não verdade de negócio.

Origens canônicas planejadas:

```text
NATIVE | OCR | FUSED | OCR_DERIVED_TEXT_LAYER
```

Ele pode conter:

- texto por página;
- palavras/linhas;
- bounding boxes e orientação;
- idioma;
- confiança por elemento;
- referência ao arquivo/versão de entrada;
- provider, modelo, versão e tentativa.

Estratégias de reconhecimento discutidas:

- PaddleOCR como OCR local e possível toolkit estrutural em perfis selecionados;
- Tesseract como opção local simples ou fallback;
- Google Document AI para OCR/layout/processadores gerenciados;
- Stirling/OCRmyPDF como normalização e OCR auxiliar.

“PaddleOCR substitui Tesseract” é decisão de **perfil e benchmark**, não regra global. Ambos podem coexistir atrás do contrato de capacidade.

`pytesseract` é binding Python da engine Tesseract; não é engine ou capability distinta. O benchmark pré-implementação compara, no mesmo dataset: texto nativo, Tesseract cru, OpenCV+Tesseract e PaddleOCR. A [estratégia de providers](PROVIDER_STRATEGY.md) define promoção e regressão.

## 8. Estrutura, layout e tabelas

`recognize_text`, `extract_layout` e `extract_table_structure` são capabilities diferentes. Texto pode ser suficiente para rule packs simples, enquanto documentos com colunas, tabelas, cabeçalhos ou ordem de leitura complexa exigem estrutura adicional. Um toolkit pode produzi-las na mesma invocation, mas cada execution/output permanece declarado.

`DocumentStructureArtifact` representa observação estrutural e pode conter:

- blocos e classes de elemento;
- hierarchy e reading order;
- páginas, bounding boxes, origem/sistema de coordenadas e transformação interna;
- tabelas, linhas, colunas, células, spans e cabeçalhos;
- `provider_item_ref`/JSON Pointer e `charspan` quando disponíveis;
- vínculos entre texto reconhecido/nativo e estrutura;
- `provided_outputs` e `produced`/`not_run`/`not_available` por saída;
- warnings, confidence/grade do provider e coverage;
- source artifact, `derived_from`, `ProviderInvocation` e `ProviderExecution`.

O Docling entra como candidato local para layout, estrutura de tabelas e conversão estruturada. A serialização JSON preserva o modelo `DoclingDocument`, não o original nem todos os intermediários; ela é mantida como raw provider artifact e normalizada ao contrato interno. Envelope de `ConversionResult`, partial success, erros, timings, confidence report, opções e digests são preservados separadamente quando expostos. Markdown/HTML são derivados e não fonte canônica.

Docling executa depois do probe por decisão de orquestração, mas não recebe implicitamente o texto do Tika: ele relê o original ou derivado suportado com seu próprio backend. As duas observações permanecem independentes, e o benchmark contabiliza o custo duplicado.

O primeiro perfil Docling deve usar PDF born-digital e OCR desligado. Texto incidental fica em spans estruturais/raw; não cria outro `RecognitionArtifact(NATIVE)`. Se uma variante habilitar OCR interno, ela é invocation composta e registra Docling, backend, engine OCR real, modelos, versões e parâmetros. Esse texto nunca é rotulado `NATIVE`. Sem origem por elemento verificável, recebe `TEXT_ORIGIN_UNRESOLVED` e não sustenta evidência canônica/autoaceite; `FUSED` exige refs explícitas.

Para scan/híbrido, o pipeline não promete injetar diretamente JSON/TSV de OCR externo no Standard PDF Pipeline. A spike deve escolher e provar Docling composto, PDF pesquisável derivado/auditado, pipeline customizado ou Docling somente estrutural com reconhecimento separado.

PaddleOCR/PP-Structure, Document AI e modelos especializados podem competir pela mesma capability. Não são empilhados automaticamente. Métricas estruturais — ordem de leitura, elementos, células/tabelas e downstream field accuracy — só são obrigatórias quando o perfil declarar essas saídas.

## 9. Extração e classificação

Extração e classificação são tarefas diferentes:

- **extração** propõe campos e entidades;
- **classificação** propõe tipo, rótulo e destino;
- **sumarização** produz uma visão derivada;
- **linking** sugere relação com entidades internas.

A ordem pode variar:

```text
classificar -> escolher schema -> extrair campos
```

ou:

```text
extrair sinais comuns -> classificar -> completar schema específico
```

O router deve representar essa ordem no task graph do perfil. Não se deve esconder as duas tarefas em uma chamada opaca.

Cada campo proposto precisa, quando tecnicamente possível, de:

- valor bruto;
- valor normalizado;
- tipo;
- confiança;
- página e coordenadas;
- trecho/evidência;
- provider execution;
- regra/modelo responsável;
- warnings.

Extração determinística usa rule packs versionados:

- normalização Unicode NFKC;
- âncoras textuais e espaciais;
- regex com grupos nomeados;
- parsers tipados para data, `Decimal`, CPF/CNPJ, linha digitável e tipos do profile;
- alternativas e conflitos preservados;
- `EvidenceRef` por campo, página, linha ou região.

Regex é regra interna, não provider e não substitui parser/checksum. Rule packs, schemas, thresholds e fixtures pertencem ao [contrato de profile](PROCESSING_PROFILE_CONTRACT.md).

## 10. Validação determinística

Modelos reconhecem e sugerem; validators testam propriedades verificáveis.

Exemplos:

- formato e dígitos verificadores de CNPJ/CPF;
- parsing e coerência de datas;
- soma de itens, impostos e total;
- vencimento posterior à emissão quando aplicável;
- moeda e separadores;
- linha digitável;
- fornecedor existente ou candidato;
- consistência entre texto, tabela e campo;
- duplicidade provável;
- campos obrigatórios por tipo documental.

Um campo pode ter alta confiança do modelo e falhar na regra. O conflito deve aumentar risco e direcionar revisão, não ser ocultado.

Validators retornam estados distinguíveis, por exemplo:

```text
PASS | FAIL | WARN | NOT_APPLICABLE
```

## 11. Política de roteamento

A decisão de rota considera:

- tipo/perfil documental;
- qualidade e modalidade;
- idioma;
- sensibilidade e residência de dados;
- capacidades elegíveis;
- confiança calibrada;
- validações e conflitos;
- orçamento de custo e latência;
- disponibilidade/saúde do provider;
- número máximo de tentativas;
- criticidade do efeito operacional.

`NativeTextAssessment` decide se o ramo precisa de OCR. `RoutingDecision` decide o próximo passo do workflow. Não fundir os dois em um output opaco.

Saídas possíveis de routing:

```text
PROCEED_WITH_RESULT
TRY_FALLBACK_PROVIDER
OPEN_REVIEW
SCHEDULE_REPROCESSING
QUARANTINE_INPUT
REJECT_RESULT
```

Esses nomes pertencem ao pipeline e não reutilizam `CONTINUE`, `AWAIT_DEPENDENCY`, `CHECKPOINT` ou `STOP`, reservados pelo ADR-0018 ao lifecycle do envelope do Codex.

Autoaceite só pode existir para perfis, campos e riscos explicitamente autorizados. A ausência de regra significa revisão, não permissão implícita.

## 12. Revisão humana

### 12.1 Ações planejadas

| Ação | Significado |
| --- | --- |
| `ACCEPT` | aceita integralmente a sugestão elegível |
| `CORRECT_AND_ACCEPT` | corrige valores e aceita o snapshot resultante |
| `OVERRIDE` | substitui conclusão com justificativa e permissão adequada |
| `REQUEST_REPROCESS` | solicita nova tentativa/perfil |
| `REJECT` | rejeita interpretação ou documento para o fluxo atual |
| `QUARANTINE` | bloqueia uso até análise especializada |

### 12.2 Regras

- sugestão e decisão humana permanecem armazenadas separadamente;
- correção registra antes/depois, autor, horário e motivo;
- override exige justificativa e, para casos sensíveis, permissão ou dupla aprovação;
- reprocessar cria nova tentativa e não apaga a anterior;
- revisão deve exibir original, evidência, confiança, validações e conflitos;
- ações financeiras ou pagamentos devem ter gates próprios.

## 13. Aceite, vínculo e efetivação

`AcceptedSnapshot` registra a interpretação documental aceita para uma versão, schema e finalidade. Ele pode ser substituído por snapshot posterior, mas continua auditável.

Depois do aceite:

1. o sistema pode sugerir fornecedor, conta, competência, lançamento ou pagamento;
2. um `EntityLink` registra a relação proposta/confirmada;
3. a política do módulo de destino define autorização;
4. a efetivação cria o efeito operacional;
5. o `DocumentEnvelope` referencia o efeito sem se tornar a entidade financeira.

O vínculo deve registrar origem, confiança, decisão e estado. Um pagamento nunca deve ser disparado apenas porque um campo foi extraído.

Fatos também podem nascer de importação estruturada ou lançamento manual auditado. Nesses casos, a fonte e o `EvidenceRef` substituem a obrigatoriedade de `DocumentEnvelope`; autorização, idempotência e audit trail permanecem.

## 14. RAG e consulta

Indexação deve preservar:

- `document_id` e `document_version_id`;
- status de revisão;
- página, trecho e coordenadas;
- schema e data do snapshot;
- permissões e tenant;
- hash/referência do conteúdo de origem.

Conteúdo não revisado pode ser indexado apenas se estiver claramente marcado e se a política permitir. Resposta de RAG precisa citar a evidência; não altera dado canônico.

## 15. Falhas e reprocessamento

Falhas devem ser classificadas:

- entrada inválida;
- arquivo protegido/corrompido;
- erro transitório de provider;
- timeout/rate limit;
- capability incompatível;
- output inválido para o schema;
- validação de negócio;
- política/segurança;
- intervenção humana necessária.

Retry automático só é permitido para erros transitórios e com limite. Troca de provider segue a política. Após o limite, o job vai para revisão ou dead letter/quarentena com contexto suficiente.

## 16. Idempotência e concorrência

- operações usam chaves de idempotência e correlation IDs;
- dois workers não devem finalizar a mesma tentativa;
- atualização de estado usa controle de versão/concorrência;
- eventos duplicados não podem duplicar efeitos financeiros;
- reprocessamento é nova tentativa explícita;
- publicação em integrações deve aplicar outbox ou mecanismo equivalente quando aprovado.

## 17. Critérios de saída por estágio

| Estágio | Critério mínimo |
| --- | --- |
| materializado | original íntegro, hash, envelope, versão e origem registrados |
| inspecionado | MIME observado, metadados, raw/normalizado, limites e reason codes registrados |
| texto avaliado | `NativeTextAssessment` versionado e explicável |
| reconhecido | artefato de texto referenciado e tentativa encerrada |
| estruturado | `DocumentStructureArtifact` e raw output referenciados quando o perfil exigir layout/tabelas |
| extraído/classificado | output válido contra schema e proveniência completa |
| validado | regras aplicáveis executadas e conflitos registrados |
| pronto para revisão | evidências e ações disponíveis ao revisor |
| aceito | decisão/snapshot versionado e auditável |
| efetivado | autorização do módulo de destino, evidência e relação tipada persistidas |
| indexado | read model reconstruível e permissão preservada |

## 18. Matriz técnica inicial

| Etapa | Estratégia baseline/candidata | Evidência e métrica | Falha explícita |
| --- | --- | --- | --- |
| intake | SHA-256 incremental + MIME preliminar seguro | hash, tamanho, origem, idempotência | MIME divergente, limite, duplicidade candidata |
| probe/nativo | Tika isolado, OCR desligado | cobertura nativa, latência, parser/config/digest | criptografado, corrompido, parcial, timeout |
| imagem | OpenCV por profile | transformação/parâmetros + impacto em CER/campo | derivado inválido ou degradação |
| OCR | Tesseract baseline e PaddleOCR challenger | CER/WER, cobertura de campo, latência/recursos | abstention, output inválido, indisponível |
| estrutura | Docling CPU e toolkits equivalentes como challengers de layout/tabela | métricas por output declarado, downstream field accuracy, cold/warm e RSS pico | output `not_run`/`not_available`, origem não resolvida, limite ou provider indisponível |
| extração | regex/parsers tipados/rule packs | exatidão normalizada por campo + `EvidenceRef` | ausente, ambíguo, conflito |
| validação | dígitos, datas, `Decimal`, totais e coerência | PASS/FAIL/WARN por regra/versão | regra não aplicável ou erro de configuração |
| linking | identificador → alias → fuzzy apenas como candidato | precision/top-k e ambiguidade | nenhum candidato ou múltiplos próximos |
| routing | policy versionada | taxa de review/erro, custo e reason code | nenhuma rota elegível → review/quarentena |

Targets, candidatos e fixtures são definidos no profile e nas Issues #43, #82–#86, #88 e #89; esta tabela não promove tecnologia antes do benchmark.

## 19. Overviews relacionados

- [Atividade do pipeline](../uml/02-business/document-processing-activity-planned.puml)
- [Sequência de intake](../uml/05-sequence/ingest-to-envelope-planned.puml)
- [Sequência de processamento e revisão](../uml/05-sequence/process-review-accept-planned.puml)
- [Estado do DocumentEnvelope](../uml/06-state/document-envelope-state-planned.puml)
- [Estado do ProcessingJob](../uml/06-state/processing-job-state-planned.puml)
