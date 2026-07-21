# Pipeline de importação estruturada

Status documental: fluxo planejado, não implementado
Atualizado em: 2026-07-21
Issue de origem: #73
ADRs relacionados: ADR-0009, ADR-0010, ADR-0011, ADR-0012 e ADR-0015 (proposto)

## 1. Finalidade

Este documento define o contrato para importar XLSX e CSV como fontes de fatos gerenciais auditáveis. OFX e CNAB usam adapters próprios e não devem ser escondidos em um parser genérico de planilha.

O arquivo original é preservado com hash e origem. As células são processadas por parser estruturado; texto extraído pelo Tika ou por OCR não é usado para reconstruir linhas. O destino conceitual está em [MANAGERIAL_FINANCIAL_DOMAIN.md](MANAGERIAL_FINANCIAL_DOMAIN.md).

## 2. Princípios

1. **preview antes de commit**;
2. **raw antes de normalized**;
3. **mapping e transformações versionados**;
4. **erro por célula/linha sem descarte silencioso**;
5. **idempotência no lote, linha e efeito**;
6. **arquivo, aba, linha e célula como evidência**;
7. **fórmulas nunca são executadas pelo importador**;
8. **replay produz nova execução e preserva histórico**;
9. **importação propõe/valida; não paga nem fecha período**;
10. **drill-through deve alcançar o valor bruto da origem**.

## 3. Objetos planejados

### 3.1 ImportBatch

Unidade de execução para um arquivo e finalidade:

- tenant, entidade e período declarados;
- `source_file_object_id`, SHA-256 e nome original;
- `document_envelope_id` quando o arquivo estiver materializado no GED;
- mapping/profile version;
- status, ator, timestamps e correlation ID;
- contagens por resultado;
- referência a raw rows, candidates, decisões e commit.

### 3.2 ImportMappingVersion

Contrato imutável que define:

- tipo/formato e seleção de abas;
- linha de cabeçalho e aliases;
- coluna de origem para campo-alvo;
- tipo, locale, transformações e defaults;
- campos obrigatórios;
- validators de célula, linha e lote;
- regra de identidade/deduplicação;
- política de linhas ignoradas;
- versão do destino e finalidade.

### 3.3 RawRow e RawCell

Representação fiel do valor observado, com:

- aba, índice de linha e coordenada da célula;
- valor armazenado e tipo reportado pela biblioteca;
- fórmula textual, quando existir, sem execução;
- valor cacheado, se presente, marcado como tal;
- estado hidden/merged quando relevante;
- hash canônico da linha;
- warnings de leitura.

### 3.4 NormalizedRow

Resultado tipado das transformações, mantendo referência 1:N às células brutas. Não substitui `RawRow`.

### 3.5 ImportCandidate e ImportDecision

`ImportCandidate` propõe criação, atualização, duplicidade ou vínculo. `ImportDecision` registra aceitar, corrigir, rejeitar ou adiar. O commit só usa candidates elegíveis e a versão de mapping revisada.

## 4. Fluxo canônico

```text
receber arquivo
  -> materializar original e hash
  -> detectar formato sem executar conteúdo
  -> abrir em modo seguro/read-only
  -> inventariar abas/headers
  -> selecionar mapping version
  -> produzir raw rows/cells
  -> preview e amostragem
  -> normalizar tipos
  -> validar célula, linha e lote
  -> detectar duplicidade/reconciliação
  -> produzir candidates e pendências
  -> decisão humana quando aplicável
  -> commit transacional/idempotente
  -> relatório do lote e drill-through
```

Falha após materialização não apaga o batch nem o original.

## 5. Contrato de mapping

Exemplo conceitual `v1alpha`:

```yaml
mapping_id: legacy_cashbook_pt_br
mapping_version: 1
target_schema: managerial_fact/v1alpha

source:
  format: xlsx
  sheet_selector: {names: [Livro Caixa]}
  header_row: 4
  data_start_row: 5
  skip_when: [all_cells_blank]

columns:
  Data:
    target: occurred_at
    type: local_date
    transforms: [trim, parse_date_pt_br]
    required: true
  Descrição:
    target: description
    type: text
    transforms: [unicode_nfkc, collapse_whitespace]
    required: true
  Valor:
    target: amount
    type: decimal
    locale: pt-BR
    transforms: [parse_decimal]
    required: true
  Tipo:
    target: direction
    type: enum
    aliases: {Entrada: INFLOW, Saída: OUTFLOW}

identity:
  fields: [occurred_at, description, amount, direction]
  strategy: candidate_fingerprint

validators:
  - rule: amount_non_zero/v1
  - rule: period_matches_batch/v1
```

O mapping não deve conter código executável. Transformações e validators são IDs de um registry permitido.

## 6. Particularidades de XLSX

O parser precisa tratar explicitamente:

- sistema de datas 1900/1904;
- células de data reais versus texto;
- números com formato visual diferente do valor armazenado;
- identificadores com zeros à esquerda;
- fórmulas e valores cacheados;
- células mescladas;
- linhas/abas ocultas;
- múltiplos cabeçalhos e notas antes da tabela;
- tabelas repetidas na mesma aba;
- abas vazias ou com schema incompatível;
- macros, vínculos externos e objetos embutidos;
- limites de linhas, colunas, memória e tempo.

Arquivos com macro não têm macro executada. A política decide rejeitar, quarentenar ou ler apenas conteúdo permitido. Links externos não são resolvidos automaticamente.

## 7. Particularidades de CSV

Registrar ou exigir:

- encoding e BOM;
- delimitador;
- quote/escape;
- newline;
- locale de número/data;
- presença de header;
- contagem esperada de colunas;
- linhas malformadas;
- limite de tamanho/linhas.

Detecção automática produz candidate e confiança técnica, não decisão silenciosa. Preview confirma ambiguidades.

## 8. Normalização tipada

Transformações candidatas:

| Categoria | Funções planejadas |
| --- | --- |
| texto | `unicode_nfkc`, `trim`, `collapse_whitespace`, preservação do raw |
| decimal | parsing por locale, escala e arredondamento explícitos |
| data | formatos permitidos e timezone apenas quando aplicável |
| documento fiscal | remover máscara + módulo 11, mantendo original |
| enum | alias table versionada; valor desconhecido vira erro/candidate |
| dimensão | ID exato, aliases e fuzzy apenas como sugestão |
| vazio | distinguir ausente, string vazia, zero e `N/A` conforme mapping |

Nenhuma transformação destrói o valor bruto.

## 9. Validação em três níveis

### 9.1 Célula

- tipo e formato;
- obrigatório;
- tamanho/escala;
- enum/identificador;
- regra determinística aplicável.

### 9.2 Linha

- coerência entre datas;
- direção e valor;
- dimensões mínimas;
- identidade/duplicidade;
- campos condicionais.

### 9.3 Lote

- entidade e período;
- totals/control totals;
- linhas sequenciais/duplicadas;
- cobertura de mapping;
- reconciliação com saldo, quando a fonte fornecer;
- taxa de erro e política de commit parcial.

Resultados:

```text
VALID
VALID_WITH_WARNINGS
INVALID
DUPLICATE_CANDIDATE
REVIEW_REQUIRED
```

Commit parcial só existe quando o mapping/policy o autorizar e o relatório listar exatamente o que entrou e o que ficou pendente.

## 10. Idempotência e commit

### 10.1 Chaves

- batch: tenant + arquivo SHA-256 + mapping ID/version + purpose;
- linha: batch + aba + identidade de linha/hash;
- efeito: source row reference + target type + policy version.

Reenviar o mesmo arquivo deve localizar o batch anterior ou criar nova tentativa explícita; nunca duplicar efeitos silenciosamente.

### 10.2 Transação

O commit planejado:

1. verifica batch e mapping ainda válidos;
2. bloqueia concorrência do mesmo lote;
3. valida candidates selecionados;
4. cria fatos/vínculos com idempotency key;
5. grava outbox/audit quando esse mecanismo estiver aprovado;
6. fecha a tentativa com contagens e hashes;
7. mantém pendências fora da transação como itens rastreáveis.

Erro transacional não marca linhas como importadas.

## 11. Reason codes mínimos

```text
FORMAT_UNSUPPORTED
FILE_LIMIT_EXCEEDED
WORKBOOK_ENCRYPTED
MACRO_NOT_ALLOWED
EXTERNAL_LINK_NOT_RESOLVED
SHEET_NOT_FOUND
HEADER_NOT_FOUND
COLUMN_REQUIRED_MISSING
CELL_TYPE_INVALID
VALUE_PARSE_FAILED
ENUM_UNKNOWN
DIMENSION_NOT_FOUND
DIMENSION_AMBIGUOUS
ROW_DUPLICATE_CANDIDATE
BATCH_CONTROL_TOTAL_MISMATCH
PERIOD_CLOSED
COMMIT_CONFLICT
```

Cada erro referencia batch, aba, linha/célula quando aplicável, regra/version e mensagem segura.

## 12. Experiência mínima de importação

A UI planejada precisa oferecer:

- seleção de entidade, período e finalidade;
- arquivo e mapping detectado/selecionado;
- preview de headers e primeiras linhas;
- valor bruto ao lado do normalizado;
- contadores de válidos, warnings, inválidos e duplicatas;
- filtros e navegação para erro por linha;
- correção/mapeamento sem perder a origem;
- dry-run antes do commit;
- progresso e retomada;
- relatório final e export de erros;
- acesso ao drill-through após commit.

Estados loading, empty, error, permission denied e conflito de período são obrigatórios. A UI não deve apresentar “importado com sucesso” se houver linhas descartadas ou pendentes não informadas.

## 13. Golden Month

O primeiro dataset de aceitação deve ser anonimizado/sintético e representar um mês completo:

- entradas e saídas;
- previsto e realizado;
- classes, aliases e master data conhecidos e ambíguos;
- ao menos um veículo e um imóvel com contrato/aditivo e recebível relacionados;
- ao menos uma duplicidade;
- erro de data/decimal;
- dimensão desconhecida/ambígua;
- rateio ou vínculo;
- movimento a reconciliar;
- control total conhecido;
- fechamento posterior.

Resultados esperados são versionados. O teste E2E reimporta o mesmo arquivo e comprova ausência de duplicação.

## 14. Segurança e operação

- não executar fórmulas, macros ou links externos;
- limites de descompressão, memória, tempo, linhas e colunas;
- temporários com lifecycle e limpeza;
- logs sem conteúdo integral;
- dados reais somente após gate do ADR-0015;
- original, mappings e decisões sujeitos a retenção;
- bibliotecas de parsing fixadas e atualizadas por processo controlado;
- importação não recebe credencial bancária por arquivo de configuração versionado.

## 15. Fronteira com OFX/CNAB

OFX e CNAB possuem estruturas, versões, identificadores e controles próprios. Eles reutilizam conceitos de batch, raw, normalização, validação e idempotência, mas exigem:

- adapter/formato escolhido explicitamente;
- fixtures e contract tests próprios;
- dados bancários e políticas específicas;
- reconciliação conforme [MANAGERIAL_FINANCIAL_DOMAIN.md](MANAGERIAL_FINANCIAL_DOMAIN.md).

Uma Issue não deve prometer “OFX ou CNAB”; deve escolher o primeiro contrato.

## 16. Definition of Ready para uma slice Codex

- formato, mapping e target schema definidos;
- fixture manifest permitido e expected output versionado;
- biblioteca/parser decidido e versão a fixar;
- tratamento de fórmula, macro, encoding e limites;
- transação, idempotency keys e política de commit parcial;
- reason codes e UX de erro;
- paths/ownership e migrations aplicáveis;
- comandos exatos de lint, testes unitários, contract e E2E;
- impacto no domínio, linhagem e fechamento;
- checkpoint para dados reais, segurança ou mudança de schema.

## 17. Critérios de aceite do primeiro importador

- [ ] O original e o mapping version são recuperáveis.
- [ ] Toda célula normalizada aponta para raw cell.
- [ ] Locale, datas, zeros à esquerda e fórmulas têm testes.
- [ ] Nenhuma linha é descartada silenciosamente.
- [ ] Preview e dry-run não criam fatos.
- [ ] Commit é transacional e idempotente.
- [ ] Reimportação não duplica efeitos.
- [ ] Erros podem ser exportados e corrigidos.
- [ ] Fatos criados permitem drill-through até arquivo/aba/célula.
- [ ] Golden Month reconcilia com os control totals esperados.
