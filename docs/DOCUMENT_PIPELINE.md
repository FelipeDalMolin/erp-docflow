# Pipeline documental canônico

Status documental: fluxo planejado, não implementado  
Atualizado em: 2026-07-10  
Issue de origem: #22  
ADRs relacionados: ADR-0012, ADR-0013 e ADR-0016 (proposto)

## 1. Finalidade

Este documento define o vocabulário e o fluxo de referência da entrada documental até o uso operacional. Ele organiza etapas que apareceram em ordens diferentes no chat **Gestão Documental Inteligente** e evita que OCR, extração, classificação, revisão e aceite sejam tratados como uma única operação.

O fluxo é um **task graph orientado por política**. Algumas etapas podem ser dispensadas, repetidas ou mudar de ordem conforme perfil documental, mas os artefatos e decisões continuam separados.

## 2. Fluxo de alto nível

```text
capturar
  -> materializar documento e original
  -> inspecionar
  -> obter/normalizar conteúdo
  -> reconhecer
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
| 3. Probe | detectar MIME real, páginas, texto nativo, qualidade e riscos | `DocumentProbe` | não |
| 4. Native text | extrair texto já existente sem OCR | `RecognitionArtifact` de origem nativa | sim |
| 5. Normalize | corrigir rotação, páginas, PDF e imagem sem perder original | `DerivedFileObject` | sim |
| 6. Recognize | produzir texto, layout, palavras, páginas e coordenadas | `RecognitionArtifact` | sim, se texto nativo suficiente |
| 7. Extract | propor campos, tabelas e entidades com proveniência | `ExtractionResult` | conforme perfil |
| 8. Classify | propor tipo, rótulos e destino | `ClassificationResult` | conforme perfil |
| 9. Validate | executar regras, reconciliações e detectar conflitos | `ValidationResult` | não para campos operacionais |
| 10. Route | aplicar thresholds, risco, custo e política | `RoutingDecision` | não |
| 11. Review | aceitar, corrigir, override, rejeitar ou reprocessar | `ReviewDecision` | somente se política permitir |
| 12. Accept | congelar interpretação canônica aprovada | `AcceptedSnapshot` | não antes de uso oficial |
| 13. Link | propor/confirmar vínculo com fornecedor, conta, lançamento etc. | `EntityLink` | conforme caso |
| 14. Effectuate | criar efeito operacional autorizado | entidade do módulo de destino + auditoria | conforme caso |
| 15. Index/export | publicar read models, índice/RAG ou integração | referência de publicação | conforme caso |

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
3. Verificar idempotência e possível duplicidade sem apagar ocorrências legítimas.
4. Armazenar original como objeto imutável.
5. Criar `DocumentEnvelope` e versão original.
6. Registrar correlação e solicitar processamento.

Duplicidade de binário não significa necessariamente duplicidade de evento de negócio. A política pode reaproveitar o objeto físico, mantendo duas ocorrências/auditorias separadas.

## 5. Probe: texto nativo antes de OCR

O pipeline não deve rasterizar todos os PDFs.

Uma etapa de inspeção — com Apache Tika ou capacidade equivalente — deve verificar:

- MIME detectado, não apenas extensão;
- existência e qualidade de texto extraível;
- número de páginas;
- criptografia/senha;
- páginas vazias ou corrompidas;
- orientação e resolução;
- presença de formulários, tabelas e imagens;
- tamanho e limites operacionais;
- sinais de conteúdo ativo ou arquivo malicioso.

Se o texto nativo for suficiente para o perfil, OCR pode ser dispensado. Isso reduz custo, latência e perda de qualidade.

## 6. Normalização

Normalização produz um derivado; nunca substitui o original.

Capacidades possíveis:

- rotação e deskew;
- split/merge;
- remoção ou seleção de páginas;
- conversão para PDF/A ou formato aceito;
- compressão controlada;
- limpeza de imagem;
- geração de PDF pesquisável;
- saneamento de metadados conforme política.

Stirling PDF é adequado como serviço self-hosted de manipulação e normalização, inclusive com OCR Tesseract/OCRmyPDF em perfis específicos. Ele não executa o papel do orquestrador, do modelo de domínio, da validação ou da revisão humana.

## 7. Reconhecimento

`RecognitionArtifact` representa conteúdo observado, não verdade de negócio.

Ele pode conter:

- texto por página;
- palavras/linhas/blocos;
- bounding boxes e orientação;
- idioma;
- tabelas e estrutura de layout;
- confiança por elemento;
- referência ao arquivo/versão de entrada;
- provider, modelo, versão e tentativa.

Estratégias discutidas:

- PaddleOCR como OCR/layout local mais capaz em perfis selecionados;
- Tesseract como opção local simples ou fallback;
- Google Document AI para OCR/layout/processadores gerenciados;
- Stirling/OCRmyPDF como normalização e OCR auxiliar.

“PaddleOCR substitui Tesseract” é decisão de **perfil e benchmark**, não regra global. Ambos podem coexistir atrás do contrato de capacidade.

## 8. Extração e classificação

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

## 9. Validação determinística

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

## 10. Política de roteamento

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

Saídas possíveis:

```text
CONTINUE
ESCALATE_PROVIDER
REVIEW_REQUIRED
REPROCESS_ALLOWED
QUARANTINE
REJECT
```

Autoaceite só pode existir para perfis, campos e riscos explicitamente autorizados. A ausência de regra significa revisão, não permissão implícita.

## 11. Revisão humana

### 11.1 Ações planejadas

| Ação | Significado |
| --- | --- |
| `ACCEPT` | aceita integralmente a sugestão elegível |
| `CORRECT_AND_ACCEPT` | corrige valores e aceita o snapshot resultante |
| `OVERRIDE` | substitui conclusão com justificativa e permissão adequada |
| `REQUEST_REPROCESS` | solicita nova tentativa/perfil |
| `REJECT` | rejeita interpretação ou documento para o fluxo atual |
| `QUARANTINE` | bloqueia uso até análise especializada |

### 11.2 Regras

- sugestão e decisão humana permanecem armazenadas separadamente;
- correção registra antes/depois, autor, horário e motivo;
- override exige justificativa e, para casos sensíveis, permissão ou dupla aprovação;
- reprocessar cria nova tentativa e não apaga a anterior;
- revisão deve exibir original, evidência, confiança, validações e conflitos;
- ações financeiras ou pagamentos devem ter gates próprios.

## 12. Aceite, vínculo e efetivação

`AcceptedSnapshot` registra a interpretação documental aceita para uma versão, schema e finalidade. Ele pode ser substituído por snapshot posterior, mas continua auditável.

Depois do aceite:

1. o sistema pode sugerir fornecedor, conta, competência, lançamento ou pagamento;
2. um `EntityLink` registra a relação proposta/confirmada;
3. a política do módulo de destino define autorização;
4. a efetivação cria o efeito operacional;
5. o `DocumentEnvelope` referencia o efeito sem se tornar a entidade financeira.

O vínculo deve registrar origem, confiança, decisão e estado. Um pagamento nunca deve ser disparado apenas porque um campo foi extraído.

## 13. RAG e consulta

Indexação deve preservar:

- `document_id` e `document_version_id`;
- status de revisão;
- página, trecho e coordenadas;
- schema e data do snapshot;
- permissões e tenant;
- hash/referência do conteúdo de origem.

Conteúdo não revisado pode ser indexado apenas se estiver claramente marcado e se a política permitir. Resposta de RAG precisa citar a evidência; não altera dado canônico.

## 14. Falhas e reprocessamento

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

## 15. Idempotência e concorrência

- operações usam chaves de idempotência e correlation IDs;
- dois workers não devem finalizar a mesma tentativa;
- atualização de estado usa controle de versão/concorrência;
- eventos duplicados não podem duplicar efeitos financeiros;
- reprocessamento é nova tentativa explícita;
- publicação em integrações deve aplicar outbox ou mecanismo equivalente quando aprovado.

## 16. Critérios de saída por estágio

| Estágio | Critério mínimo |
| --- | --- |
| materializado | original íntegro, hash, envelope, versão e origem registrados |
| reconhecido | artefato de texto/layout referenciado e tentativa encerrada |
| extraído/classificado | output válido contra schema e proveniência completa |
| validado | regras aplicáveis executadas e conflitos registrados |
| pronto para revisão | evidências e ações disponíveis ao revisor |
| aceito | decisão/snapshot versionado e auditável |
| efetivado | autorização do módulo de destino e vínculo persistido |
| indexado | read model reconstruível e permissão preservada |

## 17. Overviews relacionados

- [Atividade do pipeline](uml/02-business/document-processing-activity-planned.puml)
- [Sequência de intake](uml/05-sequence/ingest-to-envelope-planned.puml)
- [Sequência de processamento e revisão](uml/05-sequence/process-review-accept-planned.puml)
- [Estado do DocumentEnvelope](uml/06-state/document-envelope-state-planned.puml)
- [Estado do ProcessingJob](uml/06-state/processing-job-state-planned.puml)

