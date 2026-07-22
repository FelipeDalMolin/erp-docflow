# Roadmap

- **Classe:** planejamento canônico de Phases, releases e gates
- **Estado:** vigente
- **Status corrente:** [Phase 1 em execução controlada; R1 em descoberta](PROJECT_STATUS.md)
- **Atualizar quando:** escopo, dependência, resultado ou gate de Phase/release mudar

Este roadmap organiza a evolução do `erp-docflow` por duas dimensões complementares:

- **Phases:** maturidade técnica e capabilities;
- **releases:** resultados utilizáveis que combinam apenas as capabilities necessárias.

Phase 1 e R1 não são sinônimos. A Phase 1 entrega o bootstrap técnico **R0**; a release **R1 Golden Month** entrega o primeiro percurso de produto utilizável.

## 1. Direção de produto

O produto deverá transformar fontes documentais, estruturadas, manuais ou integradas em informação gerencial auditável, preservando a linhagem até evidência, relatório e fechamento.

```text
fonte identificada
  -> conteúdo bruto preservado
  -> interpretação candidata
  -> validação + decisão proporcional ao risco
  -> fato gerencial ou vínculo autorizado
  -> relatório com drill-through
  -> fechamento e pacote versionados
```

O `DocumentEnvelope` permanece o núcleo do domínio GED. Ele não é o núcleo de todo o produto e não deve ser a origem obrigatória de todo fato gerencial. Essa direção permanece baseline planejada até a decisão da [#74](https://github.com/FelipeDalMolin/erp-docflow/issues/74).

Fontes de produto:

- [North Star](../product/PRODUCT_NORTH_STAR.md);
- [Piloto Golden Month](../product/PILOT_VERTICAL_SLICE.md);
- [Jornadas e UX](../product/USER_JOURNEYS_AND_UX.md);
- [Entrega e aceite](../product/PRODUCT_DELIVERY_AND_ACCEPTANCE.md).

## 2. Overlay de releases

| Release | Resultado verificável | Gate de saída |
| --- | --- | --- |
| R0 — bootstrap técnico | workspace, API, web, Compose de desenvolvimento, CI e runbooks | #26/#33–#37 integradas; ambiente reproduzível |
| R1 — Golden Month | um mês sintético/anonimizado com classes/master data, veículo, imóvel, contrato/aditivo e recebível, importado, reconciliado, analisado, fechado e submetido a handoff contábil simulado com lineage | Epic #75, TLS/lab isolado, restore demonstrado e E2E ponta a ponta aprovados no `onprem-lab` |
| R2 — piloto operacional | dados reais autorizados, controles de segurança ratificados, gestão contratual/conciliação ampliadas e operação suportada | gates do ADR-0015, backup/restore recorrentes, RPO/RTO e aceite operacional |
| R3 — inteligência e escala | processamento documental ampliado, learning, busca híbrida e novas integrações | benchmark, segurança, custo e operação por capability |

Uma release pode atravessar várias Phases. Isso não autoriza pular gates arquiteturais, de segurança ou de dados.

## 3. Relação entre as capabilities

```text
governança + bootstrap
  -> materialização de fontes/evidências
  -> interpretação + validação + review
  -> fatos gerenciais + reconciliação
  -> relatórios + fechamento + entrega

trilha paralela:
  probe/texto nativo -> OCR seletivo -> extração/classificação -> feedback
```

As Epics #27–#32 são trilhas de capability e maturidade. Não existe a regra “terminar todo OCR antes de iniciar valor gerencial”. O Golden Month começa por XLSX/CSV e correção manual auditada; Tika/OCR agregam automação posteriormente.

## 4. Phase 0 — Sistema do Projeto

Objetivo: estabelecer governança, decisões, documentação, rastreabilidade e guardrails antes de código de produto.

Estado: **encerrada**. Hardening #65, #67 e #69 foi integrado pelos PRs #68, #71 e #70.

Resultado preservado:

- fluxo Issue → branch → PR → CI → review → squash merge;
- Plan Mode por envelope e loop controlado do Codex;
- ADRs, UML, templates e Structural CI;
- baselines de arquitetura/documentos/providers;
- distinção entre planejado, decidido e implementado.

## 5. Phase 1 / R0 — Bootstrap App

Objetivo: criar a aplicação mínima reproduzível sem antecipar GED, processamento ou domínio gerencial.

Estado: **Epic #26 autorizada para execução controlada**. A #33 aguarda review/merge no PR #72.

Inclui:

- workspace mínimo;
- backend FastAPI com `GET /health`;
- frontend React/Vite técnico;
- Compose de desenvolvimento apenas para API/web;
- CI de aplicação e runbooks.

Fora de escopo:

- Inbox funcional, upload, banco, MinIO ou workers;
- Tika, OCR, regex ou provider;
- domínio gerencial e fechamento;
- bundle instalável de piloto ou deploy.

Resultado R0:

```text
frontend abre
backend responde /health
ambiente local é reproduzível
CI executa os mesmos comandos documentados
```

Esse resultado é fundação técnica, não produto utilizável.

## 6. Phase 2 — Núcleo GED e intake

Objetivo: materializar a entrada documental com identidade, integridade e auditoria, antes de processamento profundo.

Inclui:

- `DocumentEnvelope`, `DocumentVersion` e `FileObject`;
- upload/Inbox documental;
- original imutável, SHA-256, tamanho e origem;
- `advertised_mime` informado pelo cliente;
- `intake_detected_mime` preliminar e `mime_mismatch` preservado;
- object storage, metadados transacionais e idempotência;
- estado final de intake `INSPECTION_PENDING`;
- visualização de estado, versão e auditoria inicial.

Não inclui:

- Apache Tika;
- `probe_detected_mime`;
- texto nativo, OCR, extração ou classificação.

Gates: revisar ADR-0010, ADR-0011, ADR-0012 e acesso mínimo conforme ADR-0015 antes de persistência/storage reais.

## 7. Phase 3 — Processamento documental

Objetivo: implementar um task graph observável por perfil, com decisões baseadas em benchmark.

### 7.1 Descoberta e decisão antes de implementação

1. #43 define profile, dataset manifest, ground truth, splits, sensibilidade, hardware e métricas.
2. #88 materializa o harness reproduzível de experimento: notebook fino, pacote/CLI, manifest, testes e artifact bundle imutável.
3. #82 valida Tika isolado para probe/texto nativo.
4. #83 compara candidatos somente para `recognize_text`, enquanto #89 avalia Docling CPU sem OCR para `extract_layout` e `extract_table_structure`; as trilhas podem executar em paralelo após profile/harness, e #83 usa a evidência Tika da #82 quando aplicável.
5. O perfil Docling composto com OCR, se testado, registra também engine, modelo e configuração subjacentes.
6. ADR-0016 é revisado e a decisão específica de cada capability/provider é registrada.
7. Somente então adapters produtivos tornam-se elegíveis.

### 7.2 Baseline Tika

Na primeira capability real de processamento, um worker chama Tika Server interno para:

- `probe_document`;
- `extract_native_text`;
- `probe_detected_mime`, metadados e warnings;
- resposta bruta referenciada e saída normalizada;
- versão, configuração e digest registrados.

OCR interno do Tika permanece desabilitado. O serviço não recebe credenciais de banco/storage e opera com limites de timeout, CPU, memória, tamanho, temporários e recursão.

O projeto, não o Tika, produz `NativeTextAssessment`:

```text
USE_NATIVE | OCR_REQUIRED | REVIEW_REQUIRED | QUARANTINE
```

### 7.3 Evolução seletiva

O Tika continua primeiro quando OCR existir. Apenas páginas/regiões insuficientes seguem para normalização e `recognize_text`. Artefatos `NATIVE`, `OCR` e `FUSED` preservam `derived_from`; texto de camada pesquisável gerada não se torna “nativo”.

Layout/ordem de leitura (`extract_layout`) e tabelas (`extract_table_structure`) são capabilities separadas de OCR e produzem `DocumentStructureArtifact`. Docling é challenger inicial e relê o original ou derivado autorizado; ele não consome implicitamente o texto do Tika. A serialização JSON preserva o modelo `DoclingDocument`, enquanto envelope/status/erros/timings/confidence/opções ficam correlacionados separadamente. Se o Docling orquestrar OCR, a invocation gera execution por capability e nunca transforma a saída em texto `NATIVE`; origem não resolvida bloqueia uso canônico.

Avaliação do texto nativo (#85), rule packs (#84), classificação/registry de validação (#47) e routing explicável (#86) permanecem capabilities separadas. A #48 mede regressão E2E do pipeline implementado; não substitui o benchmark pré-implementação.

## 8. Phase 4 — Review, acceptance e audit

Objetivo: permitir decisão humana/política antes de uso ou efeito sensível.

Inclui:

- `ReviewCase`, `ReviewDecision` e `AcceptedSnapshot`;
- documento, linha estruturada ou evidência ao lado da proposta;
- valor bruto, normalizado, alternativas e conflitos;
- aceitar, corrigir, override, rejeitar ou reprocessar;
- revisão de classificação, vínculos, obrigação/recebível e fato proposto;
- timeline da fonte até relatório/fechamento;
- audit trail e autorização proporcional ao risco.

Gates: ADR-0013, estratégia de auth/autorização, autoaceite por perfil e eventual dupla aprovação.

## 9. Phase 5 — Domínio gerencial e reconciliação

Objetivo: representar fatos e compromissos multiorigem sem tornar documento condição obrigatória.

Baseline planejada:

- `ManagerialFact`;
- `Obligation` com `PAYABLE` e `RECEIVABLE`;
- `Charge` e recorrência quando aplicável;
- `Settlement` para pagamento, recebimento, estorno e compensação;
- `SettlementAllocation` N:N;
- `BankMovement` e reconciliação;
- transferências com duas pernas;
- rateios;
- previsto e realizado preservados separadamente;
- `EvidenceRef` para fonte documental, estruturada, manual ou externa.

As #54–#57 devem ser refinadas com essas relações tipadas. `EntityLink` continua útil para sugestões/vínculos, mas não substitui contratos, parcelas, settlements ou allocations.

Gates: decisão #74, autoridade #80, persistência/segurança e idempotência de efeito.

## 10. Phase 6 — Geração documental

Objetivo: gerar artefatos versionados a partir de dados estruturados.

Inclui templates, PDF, recibos/contratos e `GeneratedDocument` relacionado ao `DocumentEnvelope` quando aplicável.

Três objetos não podem ser confundidos:

| Objeto | Finalidade |
| --- | --- |
| `GeneratedDocument` | documento produzido pelo domínio |
| `AccountingDeliveryPackage` | snapshot/pacote de fechamento entregue ao contador |
| `ProductReleaseBundle` | software instalável e operável |

## 11. Phase 7 — Integrações

Objetivo: conectar canais externos sem contornar intake, autorização, idempotência ou auditoria.

Inclui:

- Drive, OneDrive ou e-mail como canais documentais;
- OFX/CNAB como importação bancária estruturada;
- APIs e webhooks;
- integração bancária e contábil futura.

Upload local de XLSX/CSV do Golden Month pertence à [#77](https://github.com/FelipeDalMolin/erp-docflow/issues/77) e não depende desta Phase. A #63 deve escolher um formato bancário; a #64 deve tratar webhook/saída de integração, não o pacote contábil.

## 12. R1 — Golden Month

Objetivo: provar o produto em uma entidade e um mês completos.

Percurso:

```text
dataset anonimizado
  -> importar/mapping/validar
  -> normalizar classes/aliases/master data
  -> vincular veículo ao ledger
  -> vincular imóvel + contrato/aditivo + recebível
  -> revisar exceções
  -> fatos + obrigações + settlements
  -> reconciliar
  -> livro/matriz com drill-through
  -> fechar período
  -> AccountingDeliveryPackage + protocolo
  -> instalar e comprovar no onprem-lab
```

Issues de produto: [#75](https://github.com/FelipeDalMolin/erp-docflow/issues/75), #76–#81. Capabilities existentes #39–#40 e #49–#57 serão reutilizadas/refinadas. Processamento documental #82–#86 e #88–#89 não bloqueia o percurso.

## 13. Tracks transversais

### Segurança, privacidade e autoridade

- autenticação/autorização e segregação;
- classificação, residência, retenção, descarte e legal hold;
- criptografia, secrets, logs e auditoria;
- níveis gerencial-caixa, gerencial-competência, candidato contábil, revisado e fechado.

### UX e acessibilidade

- contexto entidade/período;
- preview e erros por linha;
- workbench com evidência;
- estados loading/vazio/erro/bloqueio/sem permissão;
- teclado, foco, contraste e desktop-first responsivo;
- drill-through e filtros preservados.

### Qualidade de processamento

- datasets/versionamento/golden fixtures;
- métricas por campo/perfil;
- abstention, calibração, drift e regressão;
- custo, latência, hardware e taxa de review;
- promoção/rollback por evidência reproduzível.

### Operação on-prem

- Compose de piloto separado do desenvolvimento;
- imagens imutáveis, migrations e rollback;
- health/readiness, logs e diagnóstico;
- backup/restore testado;
- release notes, manifest e SBOM;
- smoke/E2E Golden Month.

## 14. Princípio de execução

Cada slice precisa informar entradas, saídas, invariantes, ownership, dependências, decisão técnica, fixtures, lineage, reason codes, métricas e comandos antes de receber `Condições Verificadas`.

```text
Issue clara
  -> envelope aprovado
  -> branch curta
  -> implementação + validação
  -> draft PR
  -> CI + review humano
  -> squash merge humano
```

Plan Mode pode aprovar vários slices, mas mantém Issue/branch/PR por slice. Depois de cada entrega técnica, o Codex registra exatamente um outcome:

```text
CONTINUE | AWAIT_DEPENDENCY | CHECKPOINT | STOP
```

Mudança de release, decisão, risco, dado real, segurança, provider, persistência, deploy ou gate exige `CHECKPOINT`. Spikes produzem evidência; não promovem automaticamente hipótese a decisão aceita.
