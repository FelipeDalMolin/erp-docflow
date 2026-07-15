# Entity Map

Mapa de conceitos planejados. Ainda não há entidades, tabelas, schemas ou state machines implementados.

| Conceito | Responsabilidade | Boundary | Estado/UML | ADRs | Implementação |
| --- | --- | --- | --- | --- | --- |
| `DocumentEnvelope` | identidade e ciclo documental | documents | envelope state | ADR-0012 | não implementado |
| `DocumentVersion` | versão material original/derivada/gerada | documents/files | domain UML | ADR-0011, 0012 | não implementado |
| `FileObject` | referência binária, hash e integridade | files | domain UML | ADR-0011, 0012, 0014 | não implementado |
| `DocumentProbe` | MIME, páginas, texto nativo e qualidade | processing | pipeline | ADR-0016 (proposto) | não implementado |
| `ProcessingJob` | objetivo/task graph de processamento | processing | job state | ADR-0012, 0016 (proposto) | não implementado |
| `ProcessingAttempt` | tentativa imutável de job | processing | job state | ADR-0016 (proposto) | não implementado |
| `ProviderExecution` | capability + provider/modelo/input/artefato | providers | process sequence | ADR-0016 (proposto) | não implementado |
| `RecognitionArtifact` | texto/layout observado | processing | domain UML | ADR-0012, 0016 (proposto) | não implementado |
| `ExtractionResult` | campos/tabelas sugeridos | processing | domain UML | ADR-0012, 0016 (proposto) | não implementado |
| `ClassificationResult` | tipo/rótulo sugerido | processing | domain UML | ADR-0012, 0016 (proposto) | não implementado |
| `ValidationResult` | regra, resultado e conflito | validation | process sequence | ADR-0013, 0016 (proposto) | não implementado |
| `RoutingDecision` | próximo passo explicado por política | processing | activity UML | ADR-0016 (proposto) | não implementado |
| `ReviewCase` | unidade de trabalho de revisão | review | process sequence | ADR-0013; 0015 (proposto/gate) | não implementado |
| `ReviewDecision` | ação humana imutável | review | domain UML | ADR-0013; 0015 (proposto/gate) | não implementado |
| `AcceptedSnapshot` | interpretação aceita/versionada | documents/review | envelope state | ADR-0012, 0013 | não implementado |
| `EntityLink` | relação sugerida/confirmada | linking | pipeline | ADR-0012, 0013 | não implementado |
| `AuditEvent` | fato/decisão durável | audit | domain UML | ADR-0013; 0015 (proposto/gate); 0016 (proposto) | não implementado |
| usuário/permissão | identidade e autorização | auth | ainda não definido | ADR-0015 (proposto/gate) | não implementado |
| `FinancialEntry` | lançamento futuro | finance | ainda não definido | ADR-0009, 0013 | não implementado |
| `PaymentIntent` | intenção futura de pagamento | finance | ainda não definido | ADR-0009, 0013; 0015 (proposto/gate) | não implementado |

## Regras

- “conceito planejado” não define tabela ou classe;
- resultado de provider não é snapshot aceito;
- snapshot aceito não é entidade financeira;
- estados candidatos devem ser revisados antes de persistência;
- auth/permissão dependem de ADR específico;
- atualizar quando entidades reais, schemas ou state machines existirem.
