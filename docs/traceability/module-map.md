# Module Map

Mapa de boundaries planejados. Ainda não há módulos de produto implementados. A ampliação abaixo registra o destino aprovado para documentação pela Issue #73; não autoriza código, schema ou deploy.

Este arquivo orienta arquitetura e decomposição futura; não autoriza backend, frontend, banco, Compose, workers ou integrações.

| Boundary planejado | Responsabilidade | Conceitos principais | Fonte/ADRs | Implementação |
| --- | --- | --- | --- | --- |
| `intake` | canais documentais, idempotência e materialização inicial | ingestion, hash, origem | ADR-0012 | não implementado |
| `imports` | XLSX/CSV com mapeamento versionado e erros por lote/linha; formatos bancários usam adapters próprios | ImportBatch, ImportMappingVersion, RawRow/RawCell, NormalizedRow | #77; #63 para formato bancário | não implementado |
| `documents` | ciclo do envelope, versões e snapshots | DocumentEnvelope, DocumentVersion, AcceptedSnapshot | ADR-0012, 0013 | não implementado |
| `files` | binários, derivados, integridade e retenção | FileObject | ADR-0011, 0012, 0014 | não implementado |
| `processing` | jobs, attempts, assessment, task graph e routing | ProcessingJob, NativeTextAssessment, RoutingDecision | #82/#85/#86; ADR-0012, 0016 (proposto) | não implementado |
| `providers` | adapters por capability; Tika e OCR permanecem separados | ProviderExecution, RecognitionArtifact | #82/#83; ADR-0016 (proposto) | não implementado |
| `validation` | parsers, validators, regras determinísticas e conflitos | ValidationResult, rule packs | #47/#84; ADR-0013, 0016 (proposto) | não implementado |
| `review` | review, correção, aceite, override e rejeição | ReviewCase, ReviewDecision | ADR-0013; 0015 (proposto/gate) | não implementado |
| `audit` | fatos duráveis e decisões humanas/técnicas | AuditEvent | ADR-0013; 0015 (proposto/gate); 0016 (proposto) | não implementado |
| `lineage` | cadeia evidência → fato → célula/relatório → fechamento | EvidenceRef, DerivationStep | #78; ADR-0012/0013 | não implementado |
| `linking` | sugestão e confirmação de relações tipadas | EntityLink | ADR-0012, 0013 | não implementado |
| `assets` | dimensões patrimoniais e respectivos dossiês | Asset | #75; ADR futuro se necessário | não implementado |
| `contracts` | contratos, aditivos, vigências e vínculos | Contract, ContractTerm | #75; ADR futuro se necessário | não implementado |
| `obligations` | contas a pagar/receber, parcelas e recorrências | Obligation, Charge | #74/#75; ADR futuro antes do schema | não implementado |
| `finance` | fatos gerenciais, liquidações, conciliação, transferências e rateios | ManagerialFact, Settlement, ReconciliationMatch, AllocationSplit | #74/#75; ADR-0013; 0015 (proposto/gate) | não implementado |
| `reporting` | livro, matriz, saved views e drill-through | ReportDefinition, SavedView | #78; read models reconstruíveis | não implementado |
| `closing` | checklist, cobertura, pendências e fechamento de período | PeriodClose | #79; ADR futuro antes de efeito sensível | não implementado |
| `accounting` | pacote/protocolo e retorno da contabilidade | AccountingDeliveryPackage | #79/#80; integração depende de decisão própria | não implementado |
| `search` | índice, recuperação e RAG | chunks/read models | ADR-0012; 0015 (proposto/gate); 0016 (proposto) | não implementado |
| `integrations` | fontes e destinos externos sem bypass de gates | connectors/outbox | ADR-0001; 0015 (proposto/gate); 0016 (proposto) | não implementado |
| `auth` | identidade, acesso e segregação | usuário, papel, política | ADR-0015 (proposto/gate) | não implementado |
| `ux` | shell e jornadas de importação, review, gestão, relatórios e fechamento | estados de tela e navegação | #76; #35 cobre apenas bootstrap técnico | não implementado |
| `delivery` | bundle instalável, upgrade/rollback, diagnóstico e aceite on-prem | ProductReleaseBundle | ADR-0001, 0008, 0014; #81 | não implementado |

## Boundary técnico planejado

Workers podem executar jobs de `processing` em processos/containers separados, mantendo o produto inicialmente como modular monolith. O Tika planejado permanece isolado como serviço interno de `probe_document` e `extract_native_text`, sem credenciais de PostgreSQL ou object storage. Isso não cria microservices de domínio nem permite que um provider altere diretamente o banco canônico.

## Quando atualizar

- quando a Phase 1 criar estrutura real;
- quando boundary virar módulo de código;
- quando ADR mudar responsabilidade;
- quando um slice provar que dois boundaries devem ser unidos ou separados.
