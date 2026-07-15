# Arquitetura de referência do ERP Docflow

Status documental: baseline planejado, não implementado  
Atualizado em: 2026-07-10  
Issue de origem: #22  
ADRs relacionados: ADR-0001, ADR-0008, ADR-0009, ADR-0010, ADR-0011, ADR-0012, ADR-0013, ADR-0015 e ADR-0016 (proposto)

## 1. Objetivo

Este documento consolida a arquitetura de referência para o núcleo ERP/GED discutido em **Gestão Documental Inteligente**.

Ele descreve o destino arquitetural e os limites entre responsabilidades. Não declara backend, frontend, workers, banco, filas, rotas, tabelas ou integrações como implementados.

## 2. Princípios arquiteturais

1. **On-prem first, cloud-like**: a operação principal deve poder permanecer sob controle local, sem abandonar containers, healthchecks, filas, observabilidade, configuração por ambiente, backup e deploy reproduzível.
2. **Documento antes do ERP**: um arquivo recebido deve tornar-se uma unidade documental versionável, auditável e independente do lançamento financeiro ao qual poderá ser vinculado.
3. **Original imutável**: arquivo original, derivados normalizados, resultados de reconhecimento e decisões humanas são artefatos distintos.
4. **Automação assistida**: modelos sugerem; regras validam; pessoas aceitam, corrigem, rejeitam ou fazem override quando a política exigir.
5. **Providers por capacidade**: nenhuma ferramenta representa o pipeline inteiro. Cada adapter declara tarefas que realmente executa.
6. **Local first, escalation by value**: processamento local é preferido quando satisfaz qualidade, segurança e prazo; serviços proprietários são acionados quando entregam ganho mensurável.
7. **Proveniência obrigatória**: todo resultado precisa apontar entrada, provider, modelo/versão, configuração, horário, confiança, artefato e tentativa.
8. **Efeito operacional após gates**: uma sugestão extraída não cria silenciosamente lançamento, pagamento ou vínculo oficial.
9. **RAG não é fonte da verdade**: busca e síntese usam conteúdo aceito ou identificam claramente conteúdo ainda não revisado.

## 3. Decisões existentes preservadas

| Tema | Direção vigente | Fonte |
| --- | --- | --- |
| Operação | on-prem first com práticas cloud-like | ADR-0001 |
| Estrutura inicial | modular monolith, com limites internos claros | ADR-0009 |
| Metadados transacionais | PostgreSQL como direção inicial | ADR-0010 |
| Arquivos | interface S3-compatible; MinIO como candidato on-prem | ADR-0011 |
| Núcleo GED | `DocumentEnvelope` | ADR-0012 |
| Decisão humana | revisão, aceite e override auditáveis | ADR-0013 |
| Segurança e autorização | bloqueadas até ADR específico | ADR-0015 |
| Roteamento de modelos | proposta por capacidade e política | ADR-0016, proposto |

## 4. Visão lógica

```text
Canais de entrada
  -> Intake e materialização documental
  -> Orquestrador de processamento
       -> probe/texto nativo
       -> normalização
       -> OCR/layout
       -> extração/classificação
       -> validação
  -> Fila de revisão humana
  -> Aceite/correção/override/rejeição
  -> Vínculos e efetivação operacional
  -> Indexação, consulta e integrações
```

Todo o fluxo escreve eventos e artefatos de auditoria. Arquivos binários ficam no object storage; estado transacional e metadados ficam no banco relacional; processamento assíncrono usa fila/cache quando essa infraestrutura for aprovada e implementada.

## 5. Limites de módulos planejados

| Módulo planejado | Responsabilidade | Não deve assumir |
| --- | --- | --- |
| `intake` | receber arquivo, identificar fonte, calcular hash, criar envelope e versão inicial | OCR, classificação ou lançamento financeiro |
| `documents` | ciclo de vida do `DocumentEnvelope`, versões e metadados canônicos | detalhes de SDK de provider |
| `files` | objetos binários, derivados, integridade, retenção e referências | semântica do documento |
| `processing` | jobs, tentativas, task graph, políticas e resultados | decisão humana final |
| `providers` | adapters por capacidade e contrato normalizado | regras de negócio ou estado canônico |
| `validation` | regras determinísticas, consistência, reconciliação e conflitos | substituir revisão humana |
| `review` | fila, correções, aceite, override, rejeição e reprocessamento | apagar sugestão ou evidência anterior |
| `audit` | eventos append-only, proveniência e trilha de decisão | armazenar conteúdo sensível em log comum |
| `linking` | sugestões e vínculos entre documento e entidades do ERP | efetivar automaticamente operação sensível |
| `finance` | lançamentos, pagamentos e caixa após gates aplicáveis | ser proprietário do arquivo original |
| `search` | indexação, recuperação, RAG e citações para origem | tornar resposta de LLM dado canônico |
| `integrations` | Drive, OneDrive, e-mail, bancos e contabilidade | contornar intake, política ou auditoria |

Esses nomes representam boundaries planejados no modular monolith. Não implicam microservices nem pastas já criadas. Workers podem ser processos implantáveis separadamente sem exigir repositórios ou domínios independentes no MVP.

## 6. DocumentEnvelope

`DocumentEnvelope` é o agregado que dá identidade e ciclo de vida ao documento. Ele não é:

- o blob do PDF;
- o texto de OCR;
- um resultado específico de provider;
- o lançamento financeiro;
- um índice vetorial.

O envelope referencia versões e artefatos e mantém o estado documental atual. O original continua imutável, enquanto novas versões e interpretações são anexadas com proveniência.

### 6.1 Duas materializações diferentes

Para eliminar uma ambiguidade do material de origem, a documentação usa:

- **materialização documental**: ocorre no intake, quando a entrada ganha `DocumentEnvelope`, `DocumentVersion`, `FileObject`, hash e origem;
- **efetivação operacional**: ocorre depois dos gates aplicáveis, quando dados aceitos geram vínculo, lançamento ou outro efeito no ERP.

Aceitar uma interpretação não reescreve o original. Corrigir um campo cria nova decisão/snapshot, preservando sugestão, valor anterior, autor e justificativa.

## 7. Dados e armazenamento

| Tipo de dado | Destino planejado | Regra |
| --- | --- | --- |
| originais e derivados binários | object storage S3-compatible | objetos imutáveis, checksum e referência estável |
| envelope, versões, jobs, decisões e vínculos | PostgreSQL | estado transacional e integridade relacional |
| payloads grandes de OCR/layout | object storage ou JSONB conforme benchmark | não inflar tabelas transacionais sem necessidade |
| fila, locks e cache efêmero | infraestrutura assíncrona a decidir | nunca ser única fonte de estado |
| índice textual/vetorial | search store a decidir | reconstruível a partir de conteúdo versionado |
| logs técnicos | observabilidade | sem documento integral ou segredo por padrão |
| audit trail | persistência append-only lógica | ator, ação, antes/depois, motivo e correlação |

## 8. Providers e orquestração

O orquestrador seleciona uma sequência de tarefas; ele não escolhe simplesmente “o provider do documento”.

Exemplo:

```text
Apache Tika: detectar texto nativo
Stirling PDF/OCRmyPDF/OpenCV: normalizar quando necessário
PaddleOCR ou Tesseract: reconhecer texto local
Google Document AI: escalar layout/tabelas/campos de um perfil elegível
OpenAI: classificação semântica ou sumarização seletiva
Regras internas: validar CNPJ, datas, totais e consistência
Humano: decidir quando houver gate, baixa confiança ou conflito
```

Stirling PDF pode ser exposto por adapter de normalização e OCR auxiliar. Isso não o transforma no provider do fluxo inteiro. A mesma regra vale para Google Document AI, OpenAI, PaddleOCR ou Tesseract: cada integração implementa capacidades explícitas.

Detalhes: [PROVIDER_STRATEGY.md](PROVIDER_STRATEGY.md).

## 9. Fluxo de eventos planejado

Comandos iniciam trabalho; eventos registram fatos. Nomes abaixo são vocabulário de planejamento, não contrato de mensageria:

```text
DocumentReceived
DocumentMaterialized
ProcessingRequested
NativeTextDetected
NormalizationCompleted
RecognitionCompleted
ExtractionCompleted
ClassificationCompleted
ValidationCompleted
ReviewRequired
ReviewDecisionRecorded
DocumentAccepted
OperationalLinkSuggested
OperationalEffectuationAuthorized
SearchIndexUpdated
```

Eventos precisam carregar IDs e referências, não necessariamente o conteúdo integral. Reprocessamentos criam novas tentativas; não apagam tentativas anteriores.

## 10. Segurança, privacidade e operação

Antes de usar dados reais, precisam existir decisões e controles para:

- classificação de sensibilidade e residência de dados;
- quais tenants/perfis podem sair do on-prem;
- secrets fora do código e rotação de credenciais;
- criptografia em trânsito e em repouso;
- limpeza de temporários;
- mascaramento e política de logs;
- retenção, descarte e legal hold;
- RBAC/ABAC e segregação de funções;
- limites de custo, timeout, retry e circuit breaker;
- backup e restore testados;
- trilha de acesso e de decisão.

ADR-0015 continua sendo um gate. Este documento não escolhe solução de autenticação nem autoriza enviar documentos a providers externos.

## 11. Observabilidade e qualidade

Métricas mínimas planejadas:

- volume por tipo, origem e tenant;
- taxa de bypass de OCR;
- latência e erro por etapa/provider/modelo;
- confiança calibrada por campo e perfil;
- taxa de revisão, correção, override e rejeição;
- divergência entre providers;
- custo por documento/página/tarefa;
- reprocessamentos e dead letters;
- precisão/recall por campo em dataset rotulado;
- tempo humano por revisão;
- completude de proveniência e auditoria.

Confianças brutas de engines diferentes não devem ser comparadas como se tivessem a mesma escala. A política deve usar calibração por perfil, validação determinística e resultados de benchmark.

## 12. Status e restrições desta baseline

Esta baseline foi consolidada durante a Phase 0 e continua descrevendo arquitetura planejada/não implementada. Ela:

- não cria código de produto;
- não define endpoints;
- não define schema SQL;
- não escolhe fila ou framework de workers;
- não torna provider obrigatório;
- não autoriza dados reais, credenciais ou deploy;
- não muda ADR aceito.

As decisões ainda abertas estão registradas em [reviews/GESTAO_DOCUMENTAL_INTELIGENTE.md](reviews/GESTAO_DOCUMENTAL_INTELIGENTE.md).

## 13. Diagramas relacionados

- [Contexto planejado](uml/01-context/erp-docflow-system-context-planned.puml)
- [Deployment on-prem planejado](uml/01-context/onprem-deployment-planned.puml)
- [Atividade do pipeline](uml/02-business/document-processing-activity-planned.puml)
- [Componentes de processamento](uml/03-application/document-processing-components-planned.puml)
- [Domínio documental](uml/04-domain/document-processing-domain-planned.puml)
- [Sequência de intake](uml/05-sequence/ingest-to-envelope-planned.puml)
- [Sequência de processamento e revisão](uml/05-sequence/process-review-accept-planned.puml)
- [Estado do DocumentEnvelope](uml/06-state/document-envelope-state-planned.puml)
- [Estado do ProcessingJob](uml/06-state/processing-job-state-planned.puml)
