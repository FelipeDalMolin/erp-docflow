# Glossário documental

Status: vocabulário canônico planejado  
Atualizado em: 2026-07-21
Issues de origem: #22 e #73

| Termo | Uso canônico |
| --- | --- |
| aceite | decisão que autoriza uma interpretação/snapshot para determinada finalidade |
| adapter/provider | integração que implementa uma ou mais capabilities normalizadas |
| AccountingDeliveryPackage | pacote versionado de fechamento entregue ao contador/responsável; não é release de software |
| artefato derivado | arquivo ou payload produzido a partir de uma versão, sem substituir o original |
| auditoria | histórico durável de fatos e decisões relevantes; não é sinônimo de log técnico |
| capability | tarefa atômica declarada por um provider, como OCR ou extração de campos |
| captura/ingestão | recebimento de arquivo ou referência por um canal |
| classificação | sugestão de tipo, taxonomia, rótulo ou destino |
| conteúdo reconhecido | texto observado por extração nativa ou OCR; ainda não é verdade de negócio |
| correção | alteração humana de valor sugerido, com antes/depois e autoria |
| DocumentEnvelope | identidade e ciclo de vida do documento materializado |
| DocumentVersion | versão material original, derivada ou gerada de um documento |
| DocumentStructureArtifact | output estrutural de uma execution de `extract_layout` ou `extract_table_structure`; fusão é derivado explícito |
| efeito/efetivação operacional | criação autorizada de vínculo, lançamento, pagamento ou ação em outro módulo |
| ensemble | uso reconciliado de mais de um resultado/modelo para a mesma tarefa |
| escalonamento | mudança para outro provider/capability por política, qualidade, falha ou risco |
| evidência | referência verificável a documento, região, linha/célula, evento ou ação manual que sustenta uma interpretação |
| EvidenceRef | referência tipada à origem, localização, hashes e cadeia de transformação de uma evidência |
| ExperimentManifest | registro reproduzível de hipótese, código, dataset, configuração, hardware, comando e artifacts |
| BenchmarkRun | execução versionada de qualidade e recursos contra manifest/política de aceitação |
| PromotionDecision | decisão humana que autoriza pacote/configuração/digests para capability, profile e ambiente |
| extração | proposta de campos, tabelas e entidades tipadas |
| FileObject | referência ao objeto binário e seus metadados de integridade/storage |
| human-in-the-loop | participação humana prevista na política de decisão, não correção informal fora do sistema |
| importação estruturada | parsing de XLSX/CSV/OFX ou formato com mapping, raw/normalized row e erros; não é OCR |
| Inbox Documental | espaço operacional de entradas, pendências e estados documentais |
| materialização documental | criação de envelope, versão, arquivo, hash e origem na entrada |
| fato gerencial | ocorrência analisável e multiorigem, aceita para finalidade gerencial; não implica escrituração oficial |
| obrigação | compromisso `PAYABLE` ou `RECEIVABLE`, separado de sua liquidação |
| settlement | liquidação, recebimento, pagamento, estorno ou compensação relacionado a obrigações/fatos |
| reconciliação | comparação e vínculo controlado entre fontes, fatos, settlements e totais, com diferenças explícitas |
| fechamento de período | snapshot versionado com checklist, cobertura, pendências, pacote e protocolo |
| normalização | transformação técnica que produz derivado apropriado para processamento |
| OCR/reconhecimento | produção de texto e coordenadas disponíveis a partir de imagem ou PDF escaneado |
| layout/estrutura | observação de blocos, ordem de leitura, hierarchy e tabelas, separada de OCR |
| notebook | cliente de exploração/relatório; nunca unidade de runtime, deploy ou fonte canônica de regra |
| original | conteúdo recebido, preservado de forma imutável |
| override | substituição deliberada de uma conclusão, com permissão e justificativa |
| perfil documental | task graph, schema, providers elegíveis, thresholds, budgets e gates de um caso |
| ProviderInvocation | chamada física a SDK/CLI/serviço, com componentes, configuração, recursos, raw envelope e unidade de retry |
| ProviderExecution | resultado normalizado de exatamente uma capability, correlacionado à invocation e à decisão de promoção |
| processing profile | contrato versionado que liga input, capabilities, rules, artefatos, routing, fixtures e métricas |
| processamento | conjunto de jobs, attempts e provider executions sobre uma versão |
| proveniência | cadeia que liga resultado a input, provider, modelo, versão, configuração e tentativa |
| ProductReleaseBundle | unidade instalável do software, com manifest, versões, runbooks e verificações operacionais |
| provider proprietário | adapter de serviço/modelo externo; não representa o workflow inteiro |
| RAG | recuperação e síntese sobre conteúdo indexado; não é fonte da verdade |
| revisão | trabalho humano sobre sugestões, evidências, validações e conflitos |
| roteamento | decisão de próximo passo baseada em política e sinais |
| snapshot aceito | interpretação canônica, versionada e auditável para uma finalidade |
| NativeTextAssessment | decisão interna `USE_NATIVE`, `OCR_REQUIRED`, `REVIEW_REQUIRED` ou `QUARANTINE`; não é saída/confiança do Tika |
| sugestão | saída automática ainda sujeita a política, validação e/ou revisão |
| task graph | sequência/ramificação explícita de capabilities para um perfil |
| validação determinística | regra verificável aplicada a valores, consistência e constraints |

## Termos a evitar sem qualificador

| Evitar | Preferir |
| --- | --- |
| “o provider do documento” | “provider da capability X” |
| “o OCR aprovou” | “o OCR reconheceu; a política/ pessoa decidiu” |
| “arquivo processado” | indicar estágio: normalizado, reconhecido, extraído, validado ou aceito |
| “documento salvo” | materializado, versionado ou arquivado |
| “confiança do documento” | confiança por tarefa/campo + validação + risco |
| “mandar para o ERP” | sugerir vínculo ou efetivar operação após gate |
| “resultado final da IA” | sugestão, resultado normalizado ou snapshot aceito |
| “substituir Tesseract” | escolher engine por perfil após benchmark |
| “Stirling faz o workflow” | Stirling normaliza/manipula e pode executar OCR auxiliar |
| “Tika aprovou o texto” | “Tika observou/extraiu; a policy produziu `NativeTextAssessment`” |
| “pytesseract é o OCR” | “Tesseract é a engine; `pytesseract` é o binding Python” |
| “regex é provider” | “regex pertence a rule pack interno versionado” |
| “Docling é o OCR” | “Docling é toolkit/pipeline composto; declarar capability e engine OCR real quando habilitada” |
| “o notebook vai para produção” | “a lógica foi extraída, empacotada, testada, benchmarkada e promovida” |
| “pacote do produto” | qualificar `AccountingDeliveryPackage` ou `ProductReleaseBundle` |
