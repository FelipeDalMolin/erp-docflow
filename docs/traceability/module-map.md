# Module Map

Mapa de boundaries planejados. Ainda não há módulos de produto implementados.

Este arquivo orienta arquitetura e decomposição futura; não autoriza backend, frontend, banco, Compose, workers ou integrações.

| Boundary planejado | Responsabilidade | Conceitos principais | ADRs | Implementação |
| --- | --- | --- | --- | --- |
| `intake` | canais, idempotência e materialização inicial | ingestion, hash, origem | ADR-0012 | não implementado |
| `documents` | ciclo do envelope, versões e snapshots | DocumentEnvelope, DocumentVersion, AcceptedSnapshot | ADR-0012, 0013 | não implementado |
| `files` | binários, derivados, integridade e retenção | FileObject | ADR-0011, 0012, 0014 | não implementado |
| `processing` | jobs, attempts, task graph e routing | ProcessingJob, ProcessingAttempt, RoutingDecision | ADR-0012, 0016 (proposto) | não implementado |
| `providers` | adapters por capability | ProviderExecution, normalized result | ADR-0016 (proposto) | não implementado |
| `validation` | regras determinísticas e conflitos | ValidationResult | ADR-0013, 0016 (proposto) | não implementado |
| `review` | review, correção, aceite, override e rejeição | ReviewCase, ReviewDecision | ADR-0013; 0015 (proposto/gate) | não implementado |
| `audit` | fatos duráveis, proveniência e decisão | AuditEvent | ADR-0013; 0015 (proposto/gate); 0016 (proposto) | não implementado |
| `linking` | sugestão/confirmação de relações | EntityLink | ADR-0012, 0013 | não implementado |
| `finance` | lançamentos, pagamentos e caixa | FinancialEntry, PaymentIntent, CashMovement | ADR-0009, 0013; 0015 (proposto/gate) | não implementado |
| `search` | índice, recuperação e RAG | chunks/read models | ADR-0012; 0015 (proposto/gate); 0016 (proposto) | não implementado |
| `integrations` | fontes e destinos externos | connectors/outbox | ADR-0001; 0015 (proposto/gate); 0016 (proposto) | não implementado |
| `auth` | identidade, acesso e segregação | usuário, papel, política | ADR-0015 (proposto/gate) | não implementado |

## Boundary técnico planejado

Workers podem executar jobs de `processing` em processos/containers separados, mantendo o produto inicialmente como modular monolith. Isso não cria microservices nem permite que um provider altere diretamente o banco canônico.

## Quando atualizar

- quando a Phase 1 criar estrutura real;
- quando boundary virar módulo de código;
- quando ADR mudar responsabilidade;
- quando um slice provar que dois boundaries devem ser unidos ou separados.
