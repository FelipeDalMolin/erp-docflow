# Estratégia de providers e modelos documentais

Status documental: proposta para decisão, não implementada  
Atualizado em: 2026-07-10  
Issue de origem: #22  
ADR relacionado: ADR-0016 (proposto)

## 1. Resposta arquitetural

Sim: integrações como Stirling PDF, Google Document AI, OpenAI, PaddleOCR e Tesseract devem ficar atrás de adapters/providers.

Mas o provider é vinculado a uma **capacidade**, não ao fluxo documental inteiro.

```text
errado: provider=google executa "processar documento"

planejado:
  normalize_pdf -> stirling
  detect_native_text -> tika
  recognize_text -> paddleocr
  extract_fields -> google-document-ai
  classify_semantically -> openai
  validate_business_rules -> engine interno
  decide -> humano/política
```

Isso permite combinar local e proprietário, substituir uma etapa sem reescrever o domínio e auditar qual ferramenta produziu cada artefato.

## 2. Capabilities planejadas

| Capability | Entrada | Saída normalizada |
| --- | --- | --- |
| `probe_document` | arquivo/versão | MIME, páginas, texto disponível, qualidade e flags |
| `extract_native_text` | arquivo digital | texto, estrutura e metadados existentes |
| `normalize_document` | original/derivado | novo arquivo derivado + relatório de transformação |
| `recognize_text` | PDF/imagem | texto, página, layout, coordenadas e confiança |
| `extract_layout` | PDF/imagem | blocos, tabelas, pares e relações |
| `extract_fields` | conteúdo + schema | campos tipados com evidência |
| `classify_document` | conteúdo | classes/rótulos e score |
| `summarize_document` | conteúdo | resumo referenciado |
| `embed_content` | chunks aceitos | vetores + referências |

Validação determinística, política de roteamento, review e aceite são responsabilidades internas. Mesmo que um serviço ofereça funções parecidas, ele só devolve sugestões/artefatos.

## 3. Catálogo inicial

| Provider/adapter | Implantação | Capacidades úteis | Papel recomendado | Limites |
| --- | --- | --- | --- | --- |
| Apache Tika | local | probe, texto nativo, metadados | primeira inspeção e bypass de OCR | não é OCR avançado nem extrator de negócio |
| Stirling PDF | self-hosted | normalização, split/merge/rotate/compress, OCR auxiliar | ferramenta/serviço de preparação de PDF | não substitui orquestração, domínio, validação ou auditoria |
| OCRmyPDF | local/self-hosted | limpeza e PDF pesquisável | normalização/OCR de PDFs escaneados | não entrega entendimento semântico |
| Tesseract | local | OCR | baseline simples e fallback por perfil | layout/tabelas complexos exigem componentes adicionais |
| PaddleOCR / PaddleOCR-VL | local, GPU/CPU conforme modelo | OCR, layout e entendimento documental | candidato local principal em perfis aprovados | operação, dependências e benchmark precisam ser validados |
| Google Document AI | cloud gerenciada | OCR, layout, key-value, tabelas, classificação e processors | escalation para perfis complexos ou processors específicos | custo, residência, credenciais, lock-in e schemas do provider |
| OpenAI multimodal/texto | cloud gerenciada | entendimento visual/semântico, extração estruturada, classificação, sumarização | inteligência seletiva após política; Structured Outputs quando aplicável | não é substituto do GED, da auditoria ou da validação determinística |
| AWS Textract | cloud gerenciada | forms, tables, queries e OCR | candidato futuro de capability | não selecionado |
| Azure Document Intelligence | cloud gerenciada | prebuilt/custom, layout, campos e tabelas | candidato futuro de capability | não selecionado |
| modelos especializados locais | local | LayoutLMv3, Donut, Table Transformer ou modelo treinado | especialização após dataset e benchmark | não entram no MVP sem caso, dados e MLOps definidos |

A presença no catálogo não torna o provider aprovado, configurado ou elegível para dados reais.

## 4. Provider != produto

O domínio conhece contratos normalizados, IDs de execução e artefatos. SDKs e formatos proprietários ficam no adapter.

```text
Document Processing Orchestrator
  -> Capability Registry
  -> Routing Policy
  -> Provider Adapter
  -> Raw Provider Response (artefato)
  -> Normalized Result
  -> Validators
  -> Review Policy
```

Respostas brutas devem ser preservadas conforme retenção e segurança para permitir auditoria, debugging e renormalização. O domínio não deve depender delas diretamente.

## 5. Contrato normalizado

Exemplo conceitual:

```json
{
  "schema_version": "document-analysis-result/v1alpha",
  "execution": {
    "execution_id": "pex_...",
    "job_id": "job_...",
    "attempt": 2,
    "capability": "extract_fields",
    "provider": "google-document-ai",
    "model_name": "custom-invoice",
    "model_version": "processor-version-ref",
    "deployment": "cloud",
    "started_at": "2026-07-10T12:00:00Z",
    "finished_at": "2026-07-10T12:00:03Z"
  },
  "source": {
    "document_id": "doc_...",
    "document_version_id": "dver_...",
    "file_object_id": "file_...",
    "sha256": "..."
  },
  "result": {
    "document_type": "invoice",
    "fields": [
      {
        "name": "supplier_tax_id",
        "raw_value": "12.345.678/0001-90",
        "normalized_value": "12345678000190",
        "confidence": 0.94,
        "evidence": {
          "page": 1,
          "text": "12.345.678/0001-90",
          "bounding_box": [0.1, 0.2, 0.4, 0.25]
        }
      }
    ],
    "warnings": []
  },
  "metrics": {
    "pages": 1,
    "latency_ms": 3000,
    "estimated_cost": {
      "currency": "USD",
      "amount": "0.00"
    }
  }
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
- política de timeout e cancelamento;
- erros normalizados e retryability;
- modelo/processor e versão;
- campos de proveniência disponíveis;
- medição de latência e custo;
- classificação de dados permitida;
- healthcheck;
- comportamento de idempotência;
- suporte a batch/assíncrono;
- política de retenção do serviço externo.

## 7. Configuração por ambiente e tenant

Credenciais e endpoints ficam fora do código. A configuração deve separar:

1. **catálogo**: adapters instalados e capabilities;
2. **elegibilidade do ambiente**: quais adapters podem rodar em local, CI, lab ou produção;
3. **política do tenant**: residência, sensibilidade e providers permitidos;
4. **perfil documental**: task graph, schemas, thresholds e fallback;
5. **orçamento**: custo, páginas, tempo e concorrência;
6. **estado operacional**: saúde, rate limit e circuit breaker.

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

## 13. O que permanece em aberto

- primeiro perfil documental e dataset de referência;
- PaddleOCR ou Tesseract como primeira opção em cada perfil;
- processor(s) do Google Document AI a avaliar;
- casos em que OpenAI recebe imagem, texto nativo ou resultado de OCR;
- uso de OCR do Stirling versus OCRmyPDF direto;
- thresholds, calibração e orçamento;
- providers externos permitidos por tenant/sensibilidade;
- modelo de contratação/custo;
- estratégia de GPU on-prem;
- retenção das respostas brutas.

Essas escolhas devem vir de spike/benchmark e decisão humana, não de preferência abstrata.
