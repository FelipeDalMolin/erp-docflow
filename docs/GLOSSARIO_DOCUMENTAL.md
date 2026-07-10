# Glossário documental

Status: vocabulário canônico planejado  
Atualizado em: 2026-07-10  
Issue de origem: #22

| Termo | Uso canônico |
| --- | --- |
| aceite | decisão que autoriza uma interpretação/snapshot para determinada finalidade |
| adapter/provider | integração que implementa uma ou mais capabilities normalizadas |
| artefato derivado | arquivo ou payload produzido a partir de uma versão, sem substituir o original |
| auditoria | histórico durável de fatos e decisões relevantes; não é sinônimo de log técnico |
| capability | tarefa atômica declarada por um provider, como OCR ou extração de campos |
| captura/ingestão | recebimento de arquivo ou referência por um canal |
| classificação | sugestão de tipo, taxonomia, rótulo ou destino |
| conteúdo reconhecido | texto/layout observado por extração nativa ou OCR; ainda não é verdade de negócio |
| correção | alteração humana de valor sugerido, com antes/depois e autoria |
| DocumentEnvelope | identidade e ciclo de vida do documento materializado |
| DocumentVersion | versão material original, derivada ou gerada de um documento |
| efeito/efetivação operacional | criação autorizada de vínculo, lançamento, pagamento ou ação em outro módulo |
| ensemble | uso reconciliado de mais de um resultado/modelo para a mesma tarefa |
| escalonamento | mudança para outro provider/capability por política, qualidade, falha ou risco |
| evidência | trecho, página, coordenadas ou artefato que sustenta uma sugestão/decisão |
| extração | proposta de campos, tabelas e entidades tipadas |
| FileObject | referência ao objeto binário e seus metadados de integridade/storage |
| human-in-the-loop | participação humana prevista na política de decisão, não correção informal fora do sistema |
| Inbox Documental | espaço operacional de entradas, pendências e estados documentais |
| materialização documental | criação de envelope, versão, arquivo, hash e origem na entrada |
| normalização | transformação técnica que produz derivado apropriado para processamento |
| OCR/reconhecimento | produção de texto/layout a partir de imagem ou PDF escaneado |
| original | conteúdo recebido, preservado de forma imutável |
| override | substituição deliberada de uma conclusão, com permissão e justificativa |
| perfil documental | task graph, schema, providers elegíveis, thresholds, budgets e gates de um caso |
| processamento | conjunto de jobs, attempts e provider executions sobre uma versão |
| proveniência | cadeia que liga resultado a input, provider, modelo, versão, configuração e tentativa |
| provider proprietário | adapter de serviço/modelo externo; não representa o workflow inteiro |
| RAG | recuperação e síntese sobre conteúdo indexado; não é fonte da verdade |
| revisão | trabalho humano sobre sugestões, evidências, validações e conflitos |
| roteamento | decisão de próximo passo baseada em política e sinais |
| snapshot aceito | interpretação canônica, versionada e auditável para uma finalidade |
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

