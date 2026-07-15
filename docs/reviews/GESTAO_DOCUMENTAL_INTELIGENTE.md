# Revisão do chat Gestão Documental Inteligente

Status: consolidação de origem e pendências  
Revisado em: 2026-07-10  
Issue de aplicação: #22  
Repositório alvo: `FelipeDalMolin/erp-docflow`

## 1. Objetivo desta revisão

Transformar o conteúdo discutido no chat em documentação rastreável, separando:

- decisões já ratificadas por ADR;
- direções coerentes que podem orientar documentação;
- proposta arquitetural ainda sujeita a aprovação;
- hipóteses que exigem benchmark;
- perguntas abertas;
- contradições terminológicas resolvidas.

Este documento registra a síntese; os contratos canônicos estão nos documentos relacionados ao final.

## 2. Síntese executiva

O projeto não deve ser apenas “um OCR que exporta campos”. O núcleo é um GED/ERP documental que:

1. recebe arquivo ou referência por uma Inbox;
2. materializa identidade, original e versão;
3. processa por capabilities rastreáveis;
4. separa conteúdo observado de interpretação sugerida;
5. valida regras determinísticas;
6. encaminha conflitos/risco para revisão humana;
7. registra aceite, correção, override ou rejeição;
8. vincula o snapshot aceito a entidades do ERP;
9. efetiva operações somente após gates;
10. preserva auditoria e proveniência ponta a ponta.

A camada de ML/Deep Learning, local ou proprietária, entra como conjunto de providers especializados. Ela não substitui o domínio, o orquestrador, o GED, a validação nem o human-in-the-loop.

## 3. Decisões consolidadas

### 3.1 Já ratificadas

| Decisão | Situação | Fonte |
| --- | --- | --- |
| on-prem first com práticas cloud-like | aceita | ADR-0001 |
| modular monolith inicial | aceita com revisão futura | ADR-0009 |
| PostgreSQL como direção relacional | aceita com revisão futura | ADR-0010 |
| S3-compatible/MinIO candidato | aceita com revisão futura | ADR-0011 |
| `DocumentEnvelope` como núcleo GED | aceita com revisão futura | ADR-0012 |
| revisão, aceite e override como estrutura do fluxo | aceita com revisão futura | ADR-0013 |
| auth/security exigem decisão própria | proposta/gate | ADR-0015 |

### 3.2 Consolidadas como regras documentais

- original, derivado, OCR, extração, snapshot aceito e entidade financeira são objetos diferentes;
- OCR só ocorre quando texto nativo não atende ao perfil;
- validação determinística é obrigatória antes de uso operacional de campos relevantes;
- reprocessamento adiciona tentativa; não apaga histórico;
- RAG é read model e deve citar origem/status;
- integração de entrada não contorna materialização e auditoria;
- efeito financeiro não nasce diretamente de output de modelo;
- scores de providers diferentes exigem calibração antes de comparação.

### 3.3 Proposta ainda não ratificada

ADR-0016 propõe providers por capability e roteamento por política. Enquanto o ADR permanecer `Proposto`:

- a documentação pode usar o desenho para descoberta e benchmark;
- nenhum provider é obrigatório;
- nenhuma integração, credencial ou envio de dado real está autorizado;
- o primeiro perfil deve ser definido antes do contrato estável.

## 4. Papel das soluções discutidas

| Solução | Encaixe correto |
| --- | --- |
| Apache Tika | probe e extração de texto nativo antes de OCR |
| Stirling PDF | serviço self-hosted de manipulação/normalização e OCR auxiliar |
| OCRmyPDF | saneamento e geração de PDF pesquisável |
| Tesseract | OCR local simples/fallback por perfil |
| PaddleOCR/PaddleOCR-VL | candidato local mais completo para OCR/layout/entendimento |
| Google Document AI | provider gerenciado para OCR, layout, tabelas, key-value, classificação e processors |
| OpenAI | provider seletivo para entendimento visual/semântico, extração estruturada, classificação e sumarização |
| LayoutLMv3/Donut/Table Transformer | especialização futura após dataset e caso comprovado |
| regras/fuzzy matching | validação, normalização, reconciliação e qualidade |
| RAG | consulta/síntese sobre conteúdo versionado e autorizado |
| revisão humana | gate explícito para baixa confiança, conflito, risco e efeito sensível |

## 5. Contradições e resolução

### 5.1 PaddleOCR substitui Tesseract?

**Material de origem:** ora substituição, ora complementaridade.

**Resolução:** a arquitetura permite substituição dentro de um perfil, mas mantém ambos como providers elegíveis. A escolha depende de benchmark por idioma, layout, hardware, custo e taxa de revisão.

### 5.2 Toda camada proprietária vira um provider?

**Material de origem:** dúvida se Stirling, Document AI e OpenAI deveriam ser equivalentes.

**Resolução:** viram adapters, mas de capabilities diferentes. Um adapter não ganha responsabilidade que a ferramenta não possui.

### 5.3 Stirling PDF é o OCR workflow?

**Material de origem:** risco de colocá-lo como etapa central.

**Resolução:** Stirling é auxiliar de normalização/manipulação e pode executar OCR. Orquestração, extração semântica, validação, versionamento e auditoria continuam no ERP Docflow.

### 5.4 OCR ou Tika primeiro?

**Material de origem:** pipelines com OCR sempre e proposta low-cost “Tika first”.

**Resolução:** probe/texto nativo primeiro. OCR é condicional.

### 5.5 Extrair antes de classificar ou classificar antes de extrair?

**Material de origem:** as duas ordens aparecem.

**Resolução:** task graph por perfil. Documentos desconhecidos podem usar sinais comuns antes da classe; classes conhecidas podem selecionar schema antes da extração.

### 5.6 Materializar no início ou no fim?

**Material de origem:** “upload → materialização” e “review → materialize”.

**Resolução:** materialização documental ocorre na entrada; após aceite ocorre efetivação operacional. A interpretação aceita é um snapshot, não uma regravação do original.

### 5.7 Modular monolith ou serviços separados?

**Material de origem:** módulos coesos e desenho com API/workers/storage separados.

**Resolução:** modular monolith descreve boundaries de produto/código. Workers e dependências de infraestrutura podem rodar em processos/containers diferentes sem exigir microservices ou repositórios separados.

### 5.8 Provider por variável de ambiente ou escolha dinâmica?

**Material de origem:** configuração `PROVIDER` e router dinâmico.

**Resolução:** ambiente habilita adapters, endpoints e secrets; tenant/perfil/política selecionam capability e fallback em runtime. Uma variável global não modela o pipeline.

### 5.9 Maior confidence vence?

**Material de origem:** comparação entre OCRs.

**Resolução:** não comparar score bruto sem calibração. Usar benchmark por perfil/campo, validação e evidência; conflito relevante vai para review.

## 6. Requisitos funcionais derivados

- Inbox com origem, estado, pendência e ações;
- upload idempotente e original imutável;
- hash, versionamento e auditoria;
- processamento assíncrono com tentativa/reprocessamento;
- resultados separados de OCR, extração, classificação e validação;
- evidência por campo;
- review com original, sugestão, conflito e ação;
- aceite/correção/override/rejeição;
- vínculo sugerido/confirmado com entidades do ERP;
- timeline documental;
- busca/RAG com referência e status;
- configuração de perfil/provider sem acoplamento ao domínio.

## 7. Requisitos não funcionais derivados

- on-prem first e portabilidade;
- segurança por tenant e sensibilidade;
- secrets fora do código;
- data residency e provider eligibility;
- idempotência e consistência entre banco/storage/fila;
- audit trail durável;
- observabilidade por etapa/modelo;
- controle de custo e rate limit;
- benchmark e monitoramento de qualidade;
- backup/restore;
- retenção e deleção de temporários;
- logs sem conteúdo sensível por padrão.

## 8. Perguntas abertas

### Produto e domínio

1. Qual é o primeiro tipo documental e seu fluxo de negócio?
2. Quais canais entram no primeiro MVP além de upload?
3. Quais campos são canônicos e quais são apenas sugestão?
4. Qual efeito operacional será o primeiro: vínculo, lançamento ou apenas arquivamento?
5. Que ações exigem dupla aprovação?

### Providers e dados

6. PaddleOCR, Tesseract ou Google Document AI para o primeiro benchmark?
7. Qual processor/modelo específico do Google Document AI?
8. OpenAI receberá imagem, texto nativo ou OCR já produzido?
9. Quais classes de documento podem sair do on-prem?
10. Quais thresholds e budgets por perfil?
11. Há GPU on-prem disponível/prevista?
12. Como reter respostas brutas de providers?

### Segurança e operação

13. Qual modelo de tenant, usuário e permissão?
14. Qual retenção por tipo documental?
15. Como tratar LGPD, legal hold e descarte?
16. Qual fila/worker e mecanismo de outbox?
17. Quais RPO/RTO e testes de restore?

### Qualidade

18. Qual dataset rotulado será usado?
19. Quais métricas e tolerâncias por campo?
20. Qual taxa máxima de revisão manual é aceitável?
21. Como calibrar scores entre providers?

## 9. Ordem recomendada para decisão

```text
1. escolher primeiro perfil e caso de uso
2. definir ground truth e critérios de qualidade
3. classificar sensibilidade/residência
4. executar benchmark local vs gerenciado
5. aprovar ADR-0016 ou substituí-lo
6. estabilizar schema v1 do resultado
7. modelar slice mínimo do DocumentEnvelope
8. implementar intake e materialização
9. adicionar um task graph vertical
10. validar review e auditoria antes de efeito financeiro
```

## 10. Artefatos canônicos resultantes

- [Arquitetura](../architecture/ARCHITECTURE.md)
- [Pipeline documental](../architecture/DOCUMENT_PIPELINE.md)
- [Estratégia de providers](../architecture/PROVIDER_STRATEGY.md)
- [Baseline de dados](../architecture/DATA_MODEL_BASELINE.md)
- [Glossário](../architecture/GLOSSARIO_DOCUMENTAL.md)
- [ADR-0016 proposto](../adr/0016-capability-based-document-processing-providers.md)
- [Catálogo UML](../uml/README.md)

