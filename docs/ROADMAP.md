# Roadmap

Este roadmap organiza a evolução do ERP/GED em fases incrementais.

A proposta não é construir o sistema inteiro de uma vez. O projeto começa pelo sistema de trabalho e por uma arquitetura documental revisável, avança para um vertical slice de intake e só então adiciona processamento, revisão, financeiro, geração e integrações.

## Visão de destino

A plataforma **on-prem first**, com arquitetura **cloud-like**, deverá ser capaz de:

- receber documentos por uma Inbox e canais integrados;
- materializar `DocumentEnvelope`, original e versões;
- armazenar arquivos com integridade, versionamento e rastreabilidade;
- extrair texto nativo ou executar OCR quando necessário;
- extrair campos, tabelas e entidades;
- sugerir classificação e vínculos;
- validar regras determinísticas;
- permitir revisão humana;
- registrar aceite, correção, rejeição ou override;
- vincular snapshots aceitos a fluxos financeiros;
- gerar e versionar documentos;
- manter auditoria e proveniência;
- evoluir para bancos, escritórios contábeis e fontes externas.

## Dependências entre fases

```text
Phase 0: governança + decisões + arquitetura planejada
  -> Phase 1: aplicação mínima reproduzível
  -> Phase 2: intake + materialização documental
  -> Phase 3: um task graph de processamento
  -> Phase 4: review + accepted snapshot
  -> Phase 5: primeiro efeito ERP autorizado
```

Integrações e geração podem evoluir depois que os boundaries que utilizam estiverem estáveis.

## Phase 0 — Sistema do Projeto e baseline arquitetural

Objetivo: criar o sistema operacional do projeto e tornar decisões de produto rastreáveis antes de código.

Inclui:

- GitHub Project, Issues, slices, branches e PRs;
- modelo operacional;
- estratégia Git, VS Code, GitHub CLI e Codex;
- ADR e traceability baseline;
- UML operacional;
- CI estrutural e branch protection planejada;
- arquitetura, pipeline, glossário e modelo conceitual planejados;
- revisão do chat **Gestão Documental Inteligente**;
- ADR-0016 proposto para providers por capability.

Critério de saída:

- fluxo Issue → branch → PR → CI → review → squash merge operacional;
- docs canônicos sem contradições conhecidas;
- decisões propostas não confundidas com decisões aceitas;
- primeiro perfil documental escolhido;
- segurança, dados reais e providers externos continuam bloqueados até decisões aplicáveis;
- backlog da Phase 1 e spikes necessários especificados.

## Phase 1 — Bootstrap App

Objetivo: criar a estrutura mínima da aplicação, sem antecipar o GED completo.

Inclui:

- monorepo inicial;
- backend FastAPI com `/health`;
- frontend React/Vite;
- boundaries de módulos planejados;
- configuração inicial de ambiente local;
- README de execução;
- Docker Compose inicial;
- observabilidade e configuração mínimas sem secrets.

Fora de escopo inicial:

- autenticação completa;
- OCR/provider real;
- financeiro;
- integração bancária;
- produção.

Resultado esperado:

```text
frontend abre
backend responde /health
estrutura modular existe
ambiente local é reproduzível
```

## Phase 2 — Núcleo GED e intake

Objetivo: implementar um vertical slice de materialização documental antes de ML/OCR.

Inclui:

- `DocumentEnvelope`;
- `DocumentVersion`;
- `FileObject`;
- upload inicial pela Inbox;
- original imutável;
- SHA-256, MIME detectado e origem;
- idempotência de ingestão;
- object storage;
- metadados transacionais;
- evento/auditoria de materialização;
- visualização de estado e versão.

Gates antes de implementar:

- revisar ADR-0010 antes de schema/migrations;
- revisar ADR-0011 antes de object storage real;
- revisar ADR-0012 com o primeiro caso;
- definir tenant/acesso mínimo sem contornar ADR-0015.

Resultado esperado:

```text
arquivo recebido
original íntegro armazenado
envelope e versão materializados
metadados persistidos
documento aparece na Inbox
auditoria permite rastrear a origem
```

## Phase 3 — Probe, OCR, Extract, Classify e Validate

Objetivo: implementar um task graph vertical e observável para o primeiro perfil.

Inclui:

- `DocumentProbe` e bypass de OCR quando texto nativo for suficiente;
- normalização condicional;
- `ProcessingJob`, attempts e idempotência;
- um adapter local inicial;
- um adapter de escalation apenas se aprovado;
- `RecognitionArtifact`;
- `ExtractionResult`;
- `ClassificationResult`;
- `ValidationResult`;
- `RoutingDecision`;
- raw output referenciado e resultado normalizado;
- reprocessamento manual;
- erro, retry e limite;
- métricas de qualidade, latência e custo.

Gates antes de implementar:

- escolher primeiro tipo documental;
- criar dataset/ground truth;
- executar benchmark local versus alternativas permitidas;
- aprovar, revisar ou substituir ADR-0016;
- definir classificação/residência de dados;
- estabilizar apenas o schema mínimo necessário.

Campos candidatos, sujeitos ao primeiro perfil:

- fornecedor;
- valor;
- data de emissão;
- vencimento;
- competência;
- linha digitável;
- CNPJ/CPF;
- tipo provável.

Resultado esperado:

```text
texto nativo é reaproveitado ou OCR é justificado
cada etapa produz artefato e proveniência
campos/classificação são sugestões
regras registram passes, warnings e conflicts
router indica próximo passo
```

## Phase 4 — Review, Acceptance e Audit

Objetivo: implementar revisão humana antes de efeito sensível.

Inclui:

- `ReviewCase`;
- `ReviewDecision`;
- `AcceptedSnapshot`;
- tela com original, evidência, confiança e validações;
- aceitar, corrigir, override, rejeitar e reprocessar;
- antes/depois e justificativa;
- timeline documental;
- audit trail;
- gates por risco/campo/perfil;
- autorização conforme ADR de segurança futuro.

Gates:

- revisar ADR-0013;
- decidir auth/autorização e segregação necessárias;
- definir quais perfis permitem autoaceite;
- definir ações que exigem dupla aprovação.

Resultado esperado:

```text
sistema sugere
regras validam
pessoa/política decide
snapshot aceito é versionado
decisão e evidência são auditáveis
```

## Phase 5 — Núcleo Financeiro

Objetivo: conectar snapshots aceitos aos fluxos ERP.

Inclui:

- `FinancialEntry`;
- `PaymentIntent` inicial;
- `CashMovement` inicial;
- `EntityLink`;
- sugestão e confirmação de vínculo;
- idempotência de efetivação;
- autorização independente;
- dashboard de pendências.

Resultado esperado:

```text
snapshot documental aceito
vínculo confirmado
efeito autorizado
lançamento criado uma única vez
documento e auditoria preservados
```

## Phase 6 — Geração Documental

Objetivo: gerar documentos a partir de dados estruturados.

Inclui:

- templates versionados;
- recibos e contratos simples;
- cobranças;
- PDFs;
- `GeneratedDocument`;
- armazenamento, versão e vínculo com `DocumentEnvelope`;
- revisão/aceite quando aplicável.

## Phase 7 — Integrações

Objetivo: conectar fontes e destinos externos sem contornar o núcleo documental.

Inclui:

- Google Drive e OneDrive como entrada;
- e-mail ingestion;
- importação OFX/CNAB;
- integração bancária futura;
- plano de contas e exportação contábil;
- escritório contábil;
- webhooks e APIs externas.

Toda entrada deve passar por intake/materialização. Toda saída deve preservar autorização, idempotência e auditoria.

## Tracks transversais

### Segurança e LGPD

- autenticação/autorização;
- tenant e segregação;
- data residency;
- retenção/descarte/legal hold;
- criptografia, secrets e logs;
- acesso e auditoria.

### Qualidade de modelos

- datasets versionados;
- golden fixtures;
- benchmark por campo/perfil;
- calibração;
- drift e mudança de modelo;
- custo, latência e taxa de revisão.

### Operação on-prem

- observabilidade;
- capacity planning CPU/GPU;
- backup/restore;
- atualização/rollback;
- dead letter e reprocessamento;
- disponibilidade de providers.

## Princípio de execução

Cada fase deve ser quebrada em slices pequenos:

```text
Issue clara
  -> condição de execução verificada
  -> branch curta
  -> commits
  -> Pull Request
  -> CI e validação proporcional
  -> revisão humana
  -> squash merge
```

Plan Mode pode aprovar um envelope com vários slices da mesma frente. Dentro desse envelope, o Codex pode puxar o próximo item pronto sem nova aprovação mecânica, mantendo Issue, branch e PR por slice.

Depois de cada entrega técnica, o Codex deve decidir:

```text
CONTINUE
AWAIT_DEPENDENCY
CHECKPOINT
STOP
```

Checkpoints são exigidos por mudança de direção, risco, dependência, área protegida ou gate de Phase — não apenas porque um slice terminou.

O Codex pode iniciar trabalho independente enquanto outro PR aguarda review. Trabalho dependente aguarda merge, salvo estratégia de PR empilhado explicitamente aprovada.

Merge permanece humano.

Spikes respondem perguntas e produzem evidência; não promovem automaticamente a hipótese a decisão aceita.

