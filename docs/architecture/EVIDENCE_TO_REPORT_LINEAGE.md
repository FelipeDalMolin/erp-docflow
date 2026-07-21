# Linhagem de evidência até relatório

Status documental: contrato planejado, não implementado
Atualizado em: 2026-07-21
Issue de origem: #73
ADRs relacionados: ADR-0009, ADR-0010, ADR-0012, ADR-0013 e ADR-0015 (proposto)

## 1. Finalidade

Este documento define como um valor apresentado em livro, matriz, dashboard, fechamento ou pacote contábil deve ser rastreado até fatos, decisões e evidências.

Um relatório é read model reconstruível, não fonte da verdade. RAG, cache, export e planilha derivada não promovem valores a dado canônico.

## 2. Cadeia canônica

```text
SourceEvidence
  -> EvidenceRef
  -> DerivationStep
  -> ManagerialFact / relação tipada
  -> ReportDefinition + ReportRun
  -> ReportCell/Row
  -> CloseSnapshot / AccountingDeliveryPackage
```

A cadeia admite mais de uma evidência por campo e mais de um fato por célula agregada. Cada salto registra tipo e versão.

## 3. Tipos de evidência

| Tipo | Localizador mínimo |
| --- | --- |
| `DOCUMENT_REGION` | documento, versão, artefato, página e região/trecho |
| `STRUCTURED_CELL` | import batch, arquivo, aba, linha e célula |
| `BANK_MOVEMENT` | conta/fonte, movimento bruto e identificador |
| `MANUAL_ASSERTION` | ator, timestamp, valor, justificativa e contexto |
| `INTEGRATION_EVENT` | sistema, external ID, contrato/version e payload referenciado |
| `RECURRENCE_OCCURRENCE` | regra/version, competência e occurrence key |
| `REVIEW_DECISION` | review case/decision e before/after |
| `VALIDATION_RESULT` | regra/version, inputs referenciados e outcome |

Evidência pode sustentar um valor sem ter a mesma autoridade. A autoridade depende de validação, revisão e finalidade.

## 4. EvidenceRef

Exemplo conceitual `v1alpha`:

```json
{
  "evidence_id": "ev_...",
  "evidence_type": "STRUCTURED_CELL",
  "source": {
    "source_id": "batch_...",
    "source_version": "mapping-v1",
    "source_sha256": "..."
  },
  "locator": {
    "sheet": "Livro Caixa",
    "row": 18,
    "cell": "D18"
  },
  "observed": {
    "raw_value": "1.234,56",
    "value_hash": "..."
  },
  "access_classification": "internal"
}
```

O contrato físico pode armazenar conteúdo por referência. Logs comuns não devem copiar `raw_value` sensível.

## 5. DerivationStep

Registra transformação verificável:

- `derivation_id` e timestamp;
- operation/rule ID e versão;
- inputs ordenados por referência;
- output e hash/version;
- parâmetros/configuração;
- executor técnico ou ator;
- warnings e validation results;
- correlation/causation ID.

Exemplos:

```text
parse_decimal_pt_br/v1
map_category_alias/v3
allocate_amount/v1
sum_by_entity_period/v2
reconcile_bank_movement/v1
review_correction/v1
```

Transformação não determinística deve registrar modelo/provider, configuração e execução. Resultado humano registra ator e justificativa.

## 6. Relações de linhagem

Tipos mínimos de aresta:

```text
OBSERVED_IN
DERIVED_FROM
VALIDATED_BY
CORRECTED_BY
ACCEPTED_BY
LINKED_TO
ALLOCATED_TO
SETTLED_BY
RECONCILED_WITH
REVERSES
SUPERSEDES
INCLUDED_IN
EXCLUDED_FROM
```

Arestas possuem origem, destino, tipo, versão e contexto. Não usar um campo JSON opaco para substituir relações essenciais do domínio.

## 7. Relatórios planejados

### 7.1 ReportDefinition

Definição versionada de:

- finalidade e authority level;
- dataset/read model de origem;
- dimensões, medidas e fórmulas permitidas;
- filtros obrigatórios;
- timezone, moeda e arredondamento;
- tratamento de nulos/pendências;
- política de acesso;
- contrato de drill-through.

### 7.2 ReportRun

Execução reproduzível que registra:

- report definition/version;
- entidade, período e filtros;
- `as_of` e versão do read model;
- ator/processo;
- hashes/IDs dos fatos incluídos;
- totals, contagens e cobertura;
- estado de fechamento, quando aplicável;
- referência ao artefato exportado.

### 7.3 SavedView

Persiste preferências de apresentação — filtros, ordem, colunas e agrupamentos — sem redefinir fórmula canônica. Uma saved view não altera `ReportDefinition`.

## 8. Drill-through

Fluxo mínimo:

```text
célula/linha do relatório
  -> contribuição por ManagerialFact
  -> relações: obligation/settlement/allocation/reconciliation
  -> campos e DerivationSteps
  -> EvidenceRefs
  -> fonte permitida ao usuário
```

Requisitos:

- preservar filtros e contexto de entidade/período;
- mostrar valor bruto, normalizado e decisão quando permitido;
- identificar pendência, ajuste, reversão ou supersessão;
- listar todas as contribuições em agregações;
- não revelar evidência sem permissão;
- permitir export de lineage manifest sem copiar documento sensível por padrão.

## 9. Autoridade visível

Toda visualização informa uma das finalidades:

```text
MANAGERIAL_CASH
MANAGERIAL_ACCRUAL
ACCOUNTING_CANDIDATE
ACCOUNTING_REVIEWED
CLOSED
```

Também mostra:

- `as_of`;
- entidade/período;
- versão da definição;
- filtros ativos;
- cobertura de evidência;
- quantidade de warnings/pendências;
- se o período está aberto ou fechado.

Não apresentar “contábil” sem qualificar candidate, reviewed ou closed.

## 10. Cobertura de evidência

Métricas não substituem análise de risco. Indicadores mínimos:

- fatos com ao menos uma evidência;
- campos obrigatórios com evidência de campo;
- valor absoluto coberto por evidência;
- contribuições revisadas versus apenas importadas;
- fatos com warnings/conflicts;
- movimentos reconciliados;
- itens manuais sem confirmação adicional;
- linhas excluídas e motivo.

Exemplo de medida:

```text
coverage_by_amount =
  sum(abs(contribution_amount) com evidência elegível)
  / sum(abs(contribution_amount) total)
```

Numerador, denominador, exclusões e política de elegibilidade devem ser versionados. Zero total precisa de tratamento explícito.

## 11. Inclusão, exclusão e ajustes

- inclusão registra `INCLUDED_IN` entre fato e report run;
- exclusão por política registra `EXCLUDED_FROM` e reason code;
- correção não reescreve report run congelado;
- ajuste posterior cria fato/derivação próprio;
- reprocessamento gera novo run/version;
- pacote fechado preserva o snapshot usado, mesmo que read models evoluam.

## 12. Performance e reconstrução

Read models podem materializar agregações, mas precisam ser reconstruíveis a partir de fatos e relações canônicas. Cache deve incluir:

- report definition/version;
- entidade/período/filtros;
- versão ou watermark dos fatos;
- authority level;
- política de acesso.

Invalidar cache sem apagar `ReportRun` usado em fechamento. Índice textual/vetorial permanece derivado.

## 13. Segurança e retenção

- autorização aplicada tanto no relatório quanto no drill-through;
- lineage não pode ser usado para contornar acesso ao documento;
- exports recebem classificação e retenção;
- evidência sensível aparece minimizada/mascarada;
- acesso e export relevantes geram auditoria;
- deleção legal preserva tombstone e relações permitidas;
- package manifest usa hashes e IDs, não segredo.

O modelo de papéis depende do [ADR-0015](../adr/0015-auth-authorization-security-strategy.md).

## 14. Relação com fechamento

Ao fechar um período, o sistema congela:

- report definitions e runs usados;
- facts/relations incluídos;
- cobertura e exceções aceitas;
- lineage manifest;
- autoridade e aprovações.

O contrato de fechamento e entrega está em [ACCOUNTING_CLOSE_AND_DELIVERY.md](ACCOUNTING_CLOSE_AND_DELIVERY.md).

## 15. Experiência mínima

- tabela/matriz com comportamento familiar de planilha;
- filtros e saved views na URL/estado persistido;
- indicador de autoridade e cobertura;
- drill-through por célula/linha;
- painel lateral com fato, relações e evidências;
- estados sem dados, loading, error e permission denied;
- aviso quando dados mudaram desde o run;
- export com manifest/version e filtros.

## 16. Definition of Ready para uma slice Codex

- report definition e fórmula versionadas;
- fatos/dimensões de origem identificados;
- contrato de lineage e drill-through;
- política de inclusão/exclusão e authority level;
- expected totals e dataset Golden Month;
- limites de acesso e mascaramento;
- estratégia de read model/cache/rebuild;
- paths, ownership e migrations;
- comandos de testes unitários, integração e E2E;
- tolerâncias monetárias e de cobertura;
- impacto no fechamento/package.

## 17. Critérios de aceite

- [ ] Toda contribuição de relatório aponta fatos canônicos.
- [ ] Todo campo relevante do fato aponta evidência ou exceção explícita.
- [ ] Fórmulas e filtros são versionados.
- [ ] Saved view não altera definição canônica.
- [ ] Agregações listam todas as contribuições no drill-through.
- [ ] Permissões são mantidas até a fonte.
- [ ] Read model pode ser reconstruído.
- [ ] Reexecução com o mesmo snapshot produz totals idênticos.
- [ ] Ajuste posterior não altera report run congelado.
- [ ] Export identifica entidade, período, versão, filtros e authority level.
