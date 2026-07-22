# Domínio financeiro-gerencial orientado por evidências

Status documental: baseline planejado, não implementado
Atualizado em: 2026-07-21
Issue de origem: #73
ADRs relacionados: ADR-0009, ADR-0010, ADR-0012, ADR-0013 e ADR-0015 (proposto)

## 1. Finalidade

Este documento define o boundary conceitual do domínio financeiro-gerencial. Ele não define schema SQL, ORM, endpoints, lançamentos contábeis oficiais nem autorização para pagamento.

Princípio central:

> O núcleo do produto é o fato gerencial sustentado por evidências. `DocumentEnvelope` continua sendo o núcleo GED, mas um documento não é a única origem possível do fato.

O desenho complementa a [arquitetura](ARCHITECTURE.md), o [baseline documental](DATA_MODEL_BASELINE.md), a [importação estruturada](STRUCTURED_IMPORT_PIPELINE.md) e a [linhagem até relatórios](EVIDENCE_TO_REPORT_LINEAGE.md).

## 2. Fontes aceitas e fronteiras

Um fato pode nascer de:

```text
DOCUMENT_ACCEPTED_SNAPSHOT
STRUCTURED_IMPORT_ROW
MANUAL_ENTRY
BANK_MOVEMENT
INTEGRATION_EVENT
RECURRENCE_RULE
```

Toda origem precisa de identidade, versão, ator/processo, instante, idempotency key e evidência. Origem manual não significa “sem evidência”: a própria declaração, justificativa e autoria formam evidência, com autoridade inferior quando a política exigir confirmação.

### 2.1 Evidência antes do efeito

- documento/OCR produz sugestões, não efeito automático;
- planilha preserva arquivo, aba, linha, célula e mapping version;
- extrato preserva movimento bruto e identificador bancário;
- integração preserva payload referenciado, contrato e tentativa;
- recorrência gera ocorrência proposta, mantendo regra e versão;
- revisão/aceite eleva autoridade sem apagar o valor anterior.

### 2.2 O que não pertence a este boundary

- blob original e ciclo GED, pertencentes a `documents/files`;
- SDK de provider, pertencente a `providers`;
- autenticação e autorização, bloqueadas pelo [ADR-0015](../adr/0015-auth-authorization-security-strategy.md);
- contabilidade oficial sem revisão/autoridade definida;
- execução bancária ou pagamento automático;
- visualizações como fonte canônica.

## 3. Conceitos planejados

### 3.1 ManagerialFact

Unidade canônica de evento econômico/gerencial.

Campos conceituais mínimos:

- identidade, tenant e entidade administrada;
- `fact_type` e direção econômica;
- valor em `Decimal`, moeda e regra de arredondamento;
- `competence_date`, `due_date` e `occurred_at`, sem colapsá-las;
- contraparte e dimensões confirmadas ou pendentes;
- estado, authority level e versão;
- idempotency key;
- conjunto de `EvidenceRef` por campo relevante;
- correlação com obrigação, liquidação, movimento e fechamento.

Um fato não precisa nascer de documento aceito. Precisa nascer de fonte rastreável e satisfazer o gate correspondente.

### 3.2 Obligation

Compromisso previsto:

```text
PAYABLE
RECEIVABLE
```

Preserva principal, parcelas/charges, vencimento, competência, contraparte, contrato/regra de origem, saldo e condições. Previsto não é realizado.

### 3.3 Charge

Parcela ou cobrança vinculada a uma obrigação. Permite múltiplos vencimentos sem duplicar a identidade do contrato/obrigação.

### 3.4 Settlement

Liquidação observada ou confirmada:

```text
PAYMENT
RECEIPT
REVERSAL
COMPENSATION
```

Não pressupõe integração bancária. Registra data, valor, meio, origem e autoridade.

### 3.5 SettlementAllocation

Relação N:N entre settlement e charges/fatos. Suporta:

- pagamento parcial;
- uma remessa quitando várias parcelas;
- uma parcela quitada por vários movimentos;
- desconto, juros, multa e diferença explicitados;
- estorno sem apagar a alocação original.

### 3.6 BankMovement

Observação imutável de extrato/importação bancária. Não se torna receita ou despesa por si só. Pode participar de reconciliação, transferência ou settlement.

### 3.7 ReconciliationMatch

Vínculo versionado entre movimentos e fatos/settlements, com estado:

```text
SUGGESTED
CONFIRMED
REJECTED
SUPERSEDED
```

Preserva regra, score, alternativas e decisão. Fuzzy matching só cria candidate.

### 3.8 AllocationSplit

Rateio de valor para dimensões como centro de custo, categoria, imóvel, veículo, contrato ou projeto. A soma das parcelas deve reconciliar com o valor de origem na precisão da moeda.

### 3.9 TransferPair

Transferência interna é representada por duas pernas correlacionadas. Ela não gera receita e despesa artificiais e não pode ter apenas uma perna confirmada em período fechado.

## 4. Dimensões e relações tipadas

Dimensões candidatas:

- entidade/empresa/unidade;
- contraparte;
- conta financeira;
- categoria e plano gerencial;
- centro de custo/projeto;
- imóvel, veículo ou outro ativo;
- contrato/aditivo;
- competência e período;
- fonte/canal.

`EntityLink` continua útil para associação sugerida ou confirmada com o GED. Relações internas essenciais — obrigação-parcela, settlement-allocation, transferência e rateio — devem ser tipadas no domínio, não representadas por link genérico.

## 5. Datas, valores e autoridade

### 5.1 Datas distintas

| Campo | Uso |
| --- | --- |
| `competence_date` | período econômico/gerencial |
| `due_date` | vencimento previsto |
| `settlement_date` | realização financeira |
| `source_observed_at` | quando a fonte foi observada |
| `recorded_at` | quando o sistema registrou |

Ausência de uma data não autoriza copiar outra silenciosamente. Defaults precisam de regra/versionamento e warning.

### 5.2 Valores

- usar `Decimal`, nunca ponto flutuante binário para valor monetário;
- guardar moeda e precisão;
- valor bruto e normalizado permanecem relacionados;
- sinal não substitui `direction/type`;
- impostos, juros, multa e desconto ficam separados quando relevantes;
- conversão cambial exige taxa, fonte, data e evidência.

### 5.3 Níveis de autoridade

Relatórios e UI devem indicar, sem misturar:

```text
MANAGERIAL_CASH
MANAGERIAL_ACCRUAL
ACCOUNTING_CANDIDATE
ACCOUNTING_REVIEWED
CLOSED
```

Esses níveis descrevem a autoridade da visão/registro para determinada finalidade; não são uma alegação de escrituração oficial. A passagem para níveis contábeis exige política e ator autorizados.

## 6. Estados e invariantes

Lifecycle mínimo de um fato:

```text
PROPOSED -> VALIDATED -> CONFIRMED -> SUPERSEDED
                    \-> REJECTED
```

Invariantes:

1. correção cria nova versão/decisão; não altera silenciosamente a origem;
2. previsto e realizado são registros relacionados, não o mesmo campo sobrescrito;
3. settlement não excede saldo sem regra explícita de diferença;
4. allocations reconciliam com o total dentro da precisão definida;
5. estorno referencia o registro revertido;
6. duplicata de origem/idempotency key não cria segundo efeito;
7. reconciliação confirmada registra ator e evidências vistas;
8. período fechado bloqueia mutação comum;
9. ajuste posterior referencia o período afetado e segue política de fechamento;
10. nenhuma saída automática de dinheiro nasce de extração, importação ou reconciliação sugerida.

## 7. Fluxo import-first do Golden Month

```text
arquivo XLSX/CSV preservado
  -> mapping e preview
  -> linhas normalizadas e validadas
  -> classes, aliases e master data normalizados
  -> veículo relacionado como dimensão do ledger
  -> imóvel + contrato/aditivo + recebível relacionados
  -> ManagerialFact proposto
  -> revisão de exceções/dimensões
  -> obligations/settlements/reconciliation
  -> relatórios com drill-through
  -> fechamento e pacote contábil
```

Esse fluxo não depende de Tika, OCR ou conclusão de todos os perfis documentais. Documentos podem ser anexados depois como evidência adicional sem trocar a identidade do fato.

## 8. Idempotência e deduplicação

Camadas diferentes usam chaves diferentes:

| Camada | Chave candidata |
| --- | --- |
| arquivo/import batch | tenant + SHA-256 + mapping purpose |
| linha estruturada | batch + sheet + row identity/hash |
| integração | source system + external event ID |
| movimento bancário | conta + identificador bancário; fallback aprovado por fingerprint |
| recorrência | regra + competência + occurrence key |
| efeito gerencial | source reference + effect type + policy version |

Fingerprint probabilístico gera candidate de duplicidade; não substitui identificador determinístico quando ele existe.

## 9. Validações determinísticas iniciais

- CNPJ/CPF por módulo 11 quando aplicável;
- datas e ordem temporal;
- valor, moeda e escala;
- soma de rateios/allocations;
- saldo de obrigação/charge;
- coerência payable/receivable com settlement;
- duas pernas de transferência;
- dimensão obrigatória por entidade/período;
- período aberto;
- duplicidade e concorrência;
- reconciliação de totais por lote.

Resultado usa `PASS`, `WARN`, `FAIL` ou `NOT_APPLICABLE`; warning não deve virar sucesso silencioso.

## 10. Fechamento e relatórios

Fatos canônicos alimentam read models reconstruíveis. Cada linha/célula de relatório mantém caminho até fatos e evidências conforme [EVIDENCE_TO_REPORT_LINEAGE.md](EVIDENCE_TO_REPORT_LINEAGE.md).

O fechamento, suas exceções e seu pacote são definidos em [ACCOUNTING_CLOSE_AND_DELIVERY.md](ACCOUNTING_CLOSE_AND_DELIVERY.md). `GeneratedDocument`, `AccountingDeliveryPackage` e `ProductReleaseBundle` são objetos distintos.

## 11. Segurança e segregação

Antes de dados reais:

- tenant e entidade precisam de boundary confirmado;
- papéis para lançar, revisar, reconciliar, fechar e reabrir precisam ser decididos;
- ações sensíveis registram ator, motivo e before/after;
- secrets bancários ficam fora do repositório;
- payloads e logs seguem minimização;
- segregação de funções e dupla aprovação são avaliadas;
- retenção e base legal são definidas.

Este baseline não resolve o gate do ADR-0015.

## 12. Slice mínimo e Definition of Ready

Uma slice do domínio só fica elegível quando informar:

- caso e entidade/período do vertical slice;
- conceitos e invariantes incluídos;
- fontes permitidas;
- schema/migration e ownership, após revisão do ADR-0010;
- transações e idempotency keys;
- authority level e ações autorizadas;
- fixtures sintéticas/anonimizadas;
- validações e reason codes;
- comandos de migration check, lint e testes;
- impacto em linhagem, relatórios e fechamento;
- condição explícita de checkpoint para pagamento, segurança ou contabilidade oficial.

## 13. Critérios de aceite do primeiro vertical slice

- [ ] Um fato pode nascer de importação estruturada sem snapshot documental.
- [ ] Todo campo relevante aponta evidência e transformação.
- [ ] Previsto, realizado e reconciliado permanecem distinguíveis.
- [ ] Payable e receivable usam o mesmo boundary com tipos explícitos.
- [ ] Settlement e allocation suportam relações N:N sem duplicidade.
- [ ] Transferências não inflam receita/despesa.
- [ ] Exceções e pendências são visíveis.
- [ ] Relatório permite drill-through até fonte.
- [ ] Período fechado impede alteração comum.
- [ ] Nenhum pagamento ou escrituração oficial ocorre automaticamente.
