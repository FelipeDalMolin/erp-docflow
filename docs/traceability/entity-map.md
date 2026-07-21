# Entity Map

Mapa de conceitos planejados. Ainda não há entidades, tabelas, schemas ou state machines implementados. Os conceitos gerenciais e de entrega incluídos pela Issue #73 permanecem baselines sujeitos ao ADR e ao refinamento aplicáveis.

| Conceito | Responsabilidade | Boundary | Estado/UML | ADRs | Implementação |
| --- | --- | --- | --- | --- | --- |
| `DocumentEnvelope` | identidade e ciclo documental | documents | envelope state | ADR-0012 | não implementado |
| `DocumentVersion` | versão material original/derivada/gerada | documents/files | domain UML | ADR-0011, 0012 | não implementado |
| `FileObject` | referência binária, SHA-256, `advertised_mime`, `intake_detected_mime` e integridade | files | domain UML | ADR-0011, 0012, 0014 | não implementado |
| `DocumentProbe` | `probe_detected_mime`, páginas, proteção, parser e warnings, sem decisão de suficiência | processing | pipeline | ADR-0016 (proposto) | não implementado |
| `NativeTextAssessment` | decidir uso do texto nativo, OCR, review ou quarentena por policy | processing | activity UML | ADR-0016 (proposto); #85 | não implementado |
| `ProcessingJob` | objetivo/task graph de processamento | processing | job state | ADR-0012, 0016 (proposto) | não implementado |
| `ProcessingAttempt` | tentativa imutável de job | processing | job state | ADR-0016 (proposto) | não implementado |
| `ProviderExecution` | capability + provider/modelo/input/artefato | providers | process sequence | ADR-0016 (proposto) | não implementado |
| `RecognitionArtifact` | texto/layout observado com origem `NATIVE`, `OCR`, `FUSED` ou `OCR_DERIVED_TEXT_LAYER` | processing | domain UML | ADR-0012, 0016 (proposto) | não implementado |
| `EvidenceRef` | referência versionada a campo, linha, trecho, página, região ou artefato | lineage | pipeline/domain UML | ADR-0012, 0013; #78 | não implementado |
| `ExtractionResult` | campos/tabelas sugeridos | processing | domain UML | ADR-0012, 0016 (proposto) | não implementado |
| `ClassificationResult` | tipo/rótulo sugerido | processing | domain UML | ADR-0012, 0016 (proposto) | não implementado |
| `ValidationResult` | regra, resultado e conflito | validation | process sequence | ADR-0013, 0016 (proposto) | não implementado |
| `RoutingDecision` | próximo passo explicado por política | processing | activity UML | ADR-0016 (proposto); #86 | não implementado |
| `ReviewCase` | unidade de trabalho de revisão | review | process sequence | ADR-0013; 0015 (proposto/gate) | não implementado |
| `ReviewDecision` | ação humana imutável | review | domain UML | ADR-0013; 0015 (proposto/gate) | não implementado |
| `AcceptedSnapshot` | interpretação aceita/versionada | documents/review | envelope state | ADR-0012, 0013 | não implementado |
| `EntityLink` | relação sugerida/confirmada | linking | pipeline | ADR-0012, 0013 | não implementado |
| `AuditEvent` | fato/decisão durável | audit | domain UML | ADR-0013; 0015 (proposto/gate); 0016 (proposto) | não implementado |
| `ImportBatch` | execução idempotente de importação com mapping/schema versionados | imports | structured import pipeline | #77 | não implementado |
| `ImportMappingVersion` | contrato imutável de abas, colunas, tipos, transforms e validators | imports | structured import pipeline | #77 | não implementado |
| `RawRow` / `RawCell` | valor observado, fórmula não executada, coordenada e warnings | imports | structured import pipeline | #77 | não implementado |
| `NormalizedRow` | resultado tipado que preserva referência às células brutas | imports | structured import pipeline | #77 | não implementado |
| `ImportCandidate` / `ImportDecision` | proposta e decisão de criar, atualizar, vincular, rejeitar ou adiar | imports/review | structured import pipeline | #77 | não implementado |
| `ManagerialFact` | fato gerencial com autoridade, competência, dimensões e evidências | finance | evidence-to-report lineage | #74/#75; ADR futuro antes do schema | não implementado |
| `Obligation` | compromisso `PAYABLE` ou `RECEIVABLE`, separado de liquidação | obligations | managerial domain | #74/#75 | não implementado |
| `Charge` | parcela/cobrança prevista associada a uma obrigação | obligations | managerial domain | #74/#75 | não implementado |
| `Settlement` | pagamento, recebimento, estorno ou compensação realizados | finance | managerial domain | #74/#75; ADR-0015 (proposto/gate) | não implementado |
| `SettlementAllocation` | relação N:N entre liquidações e charges/fatos | finance | managerial domain | #74/#75 | não implementado |
| `BankMovement` | movimento importado e conciliável, sem efeito automático | finance/imports | managerial domain | #75/#77 | não implementado |
| `ReconciliationMatch` | vínculo versionado entre movimento e fato/settlement | finance | managerial domain | #74/#75 | não implementado |
| `AllocationSplit` | rateio reconciliado por dimensão, centro, ativo ou contrato | finance | managerial domain | #74/#75 | não implementado |
| `TransferPair` | duas pernas correlacionadas de transferência interna | finance | managerial domain | #74/#75 | não implementado |
| `Asset` | dimensão patrimonial, como veículo ou imóvel | assets | managerial domain | #75 | não implementado |
| `Contract` | vínculo contratual com vigência e aditivos | contracts | managerial domain | #75 | não implementado |
| `DerivationStep` | transformação versionada entre evidência, fato e saída derivada | lineage | reporting/lineage | #78 | não implementado |
| `ReportDefinition` | fórmula, dimensões, autoridade e versão de uma visão canônica | reporting | reporting/lineage | #78 | não implementado |
| `ReportRun` | execução reproduzível de relatório sobre um dataset/snapshot | reporting | reporting/lineage | #78 | não implementado |
| `SavedView` | filtros, ordem e colunas sem redefinir a fórmula canônica | reporting | reporting/lineage | #78 | não implementado |
| `CloseSnapshot` | fatos/report runs congelados usados por um fechamento | closing | close/delivery | #79 | não implementado |
| `PeriodClose` | fechamento com checklist, cobertura, pendências e autoridade | closing | close/delivery | #79; ADR futuro antes de bloquear período | não implementado |
| `AccountingDeliveryPackage` | pacote/protocolo de fechamento enviado à contabilidade | accounting | close/delivery | #79/#80 | não implementado |
| `ProductReleaseBundle` | release instalável e verificável do software | delivery | deployment | ADR-0001, 0008, 0014; #81 | não implementado |
| usuário/permissão | identidade e autorização | auth | ainda não definido | ADR-0015 (proposto/gate) | não implementado |

## Regras

- “conceito planejado” não define tabela ou classe;
- resultado de provider não é snapshot aceito;
- snapshot aceito não é entidade financeira;
- `DocumentEnvelope` não é requisito para toda fonte de `ManagerialFact`;
- `AccountingDeliveryPackage` não é `ProductReleaseBundle`;
- estados candidatos devem ser revisados antes de persistência;
- auth/permissão dependem de ADR específico;
- atualizar quando entidades reais, schemas ou state machines existirem.
