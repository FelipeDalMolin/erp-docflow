# ADR-0016 — Processamento documental por capabilities e providers

Status: Proposto  
Data: 2026-07-10  
Decisores: FelipeDalMolin (aprovação pendente)  
Tags: ocr, providers, processamento-documental, roteamento, ml, human-in-the-loop

## Contexto

O projeto precisa combinar preparação de PDF, OCR, layout, extração de campos, classificação, sumarização e validação. O material de descoberta menciona soluções locais/self-hosted e gerenciadas — Apache Tika, Stirling PDF, OCRmyPDF, Tesseract, PaddleOCR, Google Document AI e OpenAI — com custos, capacidades, riscos e formatos diferentes.

Tratar uma delas como “provider do documento” acoplaria o domínio a um workflow proprietário e confundiria normalização, reconhecimento, interpretação, validação e decisão humana.

ADR-0012 estabelece `DocumentEnvelope` como direção do núcleo GED. ADR-0013 estabelece revisão, aceite e override. Falta uma decisão explícita sobre como integrar e trocar mecanismos de processamento sem transferir a eles o controle do domínio.

## Decisão proposta

Adotar, após aprovação e benchmark do primeiro perfil documental:

1. um contrato interno orientado a **capabilities**;
2. adapters/providers que implementam somente as capabilities declaradas;
3. um orquestrador com task graph e política versionada por perfil;
4. roteamento local-first, com escalation quando qualidade, risco, prazo e política justificarem;
5. resultados normalizados e respostas brutas referenciadas;
6. proveniência por execução, modelo/processor, versão, input, configuração e tentativa;
7. validação determinística separada dos providers;
8. human-in-the-loop conforme confiança calibrada, conflito, sensibilidade e efeito operacional;
9. elegibilidade por ambiente, tenant, classificação de dados, custo e disponibilidade;
10. benchmark antes de definir provider padrão ou threshold.

Este ADR, enquanto `Proposto`, documenta a direção candidata e **não autoriza implementação, credenciais, contratação, envio de dados reais ou escolha definitiva de provider**.

## Capabilities iniciais candidatas

- `probe_document`;
- `extract_native_text`;
- `normalize_document`;
- `recognize_text`;
- `extract_layout`;
- `extract_fields`;
- `classify_document`;
- `summarize_document`;
- `embed_content`.

Review, acceptance, override, auditoria, linking e validação de negócio permanecem responsabilidades internas.

## Alternativas consideradas

### Provider único para todo o fluxo

Exemplo: escolher Google Document AI ou OpenAI e delegar “processar documento”.

Rejeição proposta: aumenta acoplamento, obscurece proveniência por etapa, dificulta fallback e mistura tarefas.

### Pipeline local fixo

Exemplo: Stirling + Tesseract para todos os documentos.

Rejeição proposta: reduz custo e exposição, mas não cobre igualmente layouts, tabelas, idiomas e extrações complexas.

### Microservices por provider desde o início

Rejeição proposta: adiciona complexidade operacional antes de haver volume, benchmark e boundaries validados.

### Adapters por capability no modular monolith

Alternativa proposta: preserva limites, permite workers/processos separados e evita distribuição prematura.

## Consequências positivas

- troca de provider por tarefa/perfil;
- combinação local + proprietário;
- fallback e experimentos controlados;
- auditoria detalhada;
- custos e latência observáveis;
- proteção do domínio contra SDKs proprietários;
- caminho para modelos especializados locais;
- revisão humana baseada em sinais explícitos.

## Consequências negativas / trade-offs

- contrato normalizado exige desenho e manutenção;
- outputs ricos podem perder detalhes se o schema for simplificado demais;
- router e policy versioning adicionam complexidade;
- scores precisam de calibração;
- preservar outputs brutos aumenta necessidade de storage/retenção;
- testes de contrato e fixtures por provider tornam-se obrigatórios;
- local-first pode exigir GPU e operação de modelos.

## Impacto técnico

### Documentação afetada

- `docs/architecture/ARCHITECTURE.md`;
- `docs/architecture/DOCUMENT_PIPELINE.md`;
- `docs/architecture/PROVIDER_STRATEGY.md`;
- `docs/architecture/DATA_MODEL_BASELINE.md`;
- `docs/architecture/GLOSSARIO_DOCUMENTAL.md`;
- `docs/reviews/GESTAO_DOCUMENTAL_INTELIGENTE.md`;
- `docs/project/ROADMAP.md`;
- `docs/uml/`;
- `docs/traceability/`.

### Módulos afetados

Planejados: `processing`, `providers`, `validation`, `review`, `audit`, `documents` e `files`.

Nenhum módulo está implementado nesta ADR.

### Entidades afetadas

Planejadas: `ProcessingJob`, `ProcessingAttempt`, `ProviderExecution`, `RecognitionArtifact`, `ExtractionResult`, `ClassificationResult`, `ValidationResult`, `RoutingDecision` e `ReviewDecision`.

Nenhuma entidade ou tabela é criada nesta ADR.

### Rotas afetadas

Nenhuma rota definida. Contratos HTTP só devem ser propostos no slice de implementação aplicável.

### Infra afetada

Futuros workers, CPU/GPU, fila, object storage, secrets, observabilidade e conectividade controlada com providers externos.

### Testes necessários

- contract tests por adapter;
- golden fixtures;
- outputs inválidos e erros normalizados;
- idempotência/retry/cancelamento;
- routing policy;
- segurança e provider eligibility;
- benchmark por perfil/campo;
- calibração de confiança;
- fallback e conflito;
- auditoria e proveniência;
- custo e latência.

## Relações

Substitui: nenhum.  
Substituído por: —  
Complementa: ADR-0001, ADR-0009, ADR-0012 e ADR-0013.  
Complementado por: —  
Relacionado a: ADR-0008, ADR-0010, ADR-0011, ADR-0014 e ADR-0015.

## Condições para aprovação

1. selecionar o primeiro perfil documental;
2. definir dataset/ground truth e métricas;
3. definir classificação de dados e providers elegíveis;
4. comparar ao menos uma opção local e uma alternativa de escalation quando permitida;
5. revisar custo total, latência, taxa de intervenção e operação on-prem;
6. definir schema mínimo do resultado normalizado;
7. decidir política de retenção do raw output;
8. confirmar gates humanos e relação com o ADR de segurança futuro.

## Gatilhos que podem mudar a proposta

- um único serviço demonstrar vantagem operacional decisiva sem comprometer portabilidade;
- restrição legal proibir processamento externo;
- hardware local inviabilizar modelos candidatos;
- volume/latência exigir serviço separado;
- schemas dos providers não admitirem normalização útil;
- custo de manter múltiplos adapters superar o benefício;
- primeiro perfil exigir modelo especializado.

## Revisão futura obrigatória

### Motivo da revisão futura

O desenho foi consolidado em Phase 0 sem benchmark do primeiro perfil.

### Fase ou condição de revisão

Antes de implementar integração real de OCR/ML na Phase 3 e após spike com documentos sintéticos ou autorizados.

### Impactos previstos

A aprovação, rejeição ou substituição afeta módulos, schemas, workers, infraestrutura, segurança, custos, métricas, UMLs e rastreabilidade.

