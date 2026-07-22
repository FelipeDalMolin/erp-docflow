# Fechamento, pacote contábil e entrega do produto

Status documental: baseline planejado, não implementado
Atualizado em: 2026-07-21
Issue de origem: #73
ADRs relacionados: ADR-0001, ADR-0008, ADR-0010, ADR-0011, ADR-0014 e ADR-0015 (proposto)

## 1. Finalidade

Este documento define dois fluxos que não devem ser confundidos:

| Objeto | Entrega |
| --- | --- |
| `AccountingDeliveryPackage` | dados, relatórios, evidências e protocolo de um fechamento para o contador |
| `ProductReleaseBundle` | versão instalável/operável do software para `onprem-lab` ou ambiente autorizado |

`GeneratedDocument` é ainda um terceiro objeto: documento de negócio gerado a partir de template. Ele não substitui nenhum dos dois.

Nada aqui cria deploy, produção, escrituração oficial ou autorização para dados reais.

Este é o contrato **técnico** planejado para objetos, estados, invariantes, topology constraints, upgrade/rollback, observabilidade e Definition of Ready. O resultado esperado pelo usuário/operador, os destinatários, os níveis de maturidade e o aceite observável pertencem a [Entrega e aceite do produto](../product/PRODUCT_DELIVERY_AND_ACCEPTANCE.md). Se surgir divergência, registrar Issue e consultar o ADR aplicável em vez de combinar regras silenciosamente.

## 2. PeriodClose

Agregado que coordena o fechamento de uma entidade e período.

Campos conceituais:

- identidade, tenant, entidade e período;
- tipo/finalidade de fechamento;
- authority level;
- estado e versão;
- checklist versionado;
- report runs/snapshots;
- cobertura, totals e pendências;
- exceções aceitas e justificativas;
- revisores/aprovações;
- timestamps de freeze, close, reopen e supersessão;
- package/protocols relacionados.

### 2.1 Estados

```text
OPEN
  -> PREPARING
  -> REVIEW_REQUIRED
  -> READY_TO_CLOSE
  -> CLOSED
  -> REOPENED
  -> CLOSED (nova versão)
```

`CANCELLED` pode existir antes do fechamento. Um close encerrado não é apagado; uma versão posterior o sucede quando a política permitir reabertura.

### 2.2 Invariantes

1. entidade, período e finalidade identificam o escopo;
2. apenas período aberto recebe mutação comum;
3. close registra snapshot dos fatos e report runs usados;
4. exceção aceita tem autor, motivo, prazo e impacto;
5. alteração posterior não modifica snapshot fechado;
6. reabertura exige permissão, justificativa e nova versão;
7. ajustes referenciam período afetado e close anterior;
8. pacote é gerado a partir de close versionado, nunca da tela corrente;
9. entrega registra hash, destinatário autorizado e protocolo;
10. fechar período não executa pagamento.

## 3. Checklist planejado

O checklist é versionado por entidade/finalidade. Itens mínimos do piloto:

- import batches concluídos e control totals conferidos;
- erros de parsing sem descarte silencioso;
- dimensões obrigatórias resolvidas;
- obligations/receivables e settlements consistentes;
- movimentos bancários importados e cobertura de reconciliação calculada quando o dataset os contiver;
- transferências com duas pernas quando houver caso de transferência; caso contrário, item marcado `NOT_APPLICABLE` com motivo;
- rateios reconciliados quando o dataset escolher o caso de rateio; caso use somente vínculo, item marcado `NOT_APPLICABLE` com motivo;
- duplicidades resolvidas;
- warnings/conflicts classificados;
- fatos manuais identificados;
- relatórios gerencial-caixa e competência gerados;
- lineage/coverage calculados;
- exceções aceitas por ator autorizado;
- backup/restore gate avaliado para operação real;
- aprovação final registrada.

O checklist não deve exigir 100% de reconciliação por regra fixa global. Thresholds e exceções dependem de política aprovada e aparecem no pacote. Todo item condicional registra `PASS`, `FAIL`, `WARN` ou `NOT_APPLICABLE`; ausência silenciosa não conta como aprovação.

## 4. CloseException

Exceção é item explícito, não comentário solto:

- tipo, severidade e reason code;
- fato/movimento/relatório afetado;
- valor e impacto;
- evidências;
- owner e prazo;
- decisão: resolver, aceitar temporariamente, excluir ou bloquear;
- ator, justificativa e autoridade;
- status e relação com close/package.

Exceção bloqueante impede `READY_TO_CLOSE`. Exceção aceita continua visível no package.

## 5. AccountingDeliveryPackage

### 5.1 Conteúdo mínimo

```text
manifest.json
close-summary.pdf ou formato aprovado
reports/
exports/
lineage-manifest/
exceptions/
evidence-index/
checksums.txt
```

O formato físico é decisão de implementação. O manifest registra:

- package ID/version;
- close ID/version;
- entidade, período e authority level;
- report definitions/runs;
- formatos e schemas de exports;
- contagens, totals e cobertura;
- exceções incluídas;
- artifact hashes e tamanhos;
- gerador/version;
- instante de freeze;
- classificação e política de retenção.

Documentos originais não são copiados por padrão. O evidence index aponta IDs/localizadores permitidos; anexos sensíveis dependem de política.

### 5.2 Estados do package

```text
DRAFT -> FROZEN -> SENT -> ACKNOWLEDGED
                    \-> REJECTED
       -> SUPERSEDED
```

`FROZEN` torna artifacts e manifest imutáveis. Correção produz nova versão, nunca substituição silenciosa.

### 5.3 DeliveryProtocol

Registra:

- package e hash;
- canal/destinatário resolvido e autorizado;
- ator e finalidade;
- tentativa, timestamps e status;
- confirmação/recibo externo;
- erro normalizado e retryability;
- referência a feedback/retorno.

O protocolo não guarda segredo. Webhook genérico e pacote contábil são capabilities diferentes.

## 6. Retorno do contador

Feedback/arquivo de retorno entra como nova fonte auditável:

- referencia package e protocolo;
- preserva original/hash;
- classifica aceite, solicitação de correção ou ajuste;
- cria tarefas/adjustment candidates;
- não altera close/package anterior;
- mantém correspondência entre item retornado, fato e evidência.

## 7. Linhagem do fechamento

Cada total do package deve alcançar os fatos e evidências conforme [EVIDENCE_TO_REPORT_LINEAGE.md](EVIDENCE_TO_REPORT_LINEAGE.md). O close congela:

- IDs/versões dos fatos e relações;
- report runs e formulas;
- inclusões/exclusões;
- coverage e exceptions;
- decisões e aprovações;
- lineage manifest.

## 8. Golden Month — critério de produto

O piloto R1 fecha uma entidade e um mês representativo:

1. importa fonte XLSX/CSV versionada;
2. normaliza classes, aliases, master data e dimensões;
3. relaciona veículo e imóvel com contrato/aditivo e recebível representativos;
4. registra payable/receivable, settlements e movimentos necessários;
5. reconcilia ou explicita pendências;
6. gera livro, fluxo e matriz com drill-through;
7. executa checklist e revisão;
8. fecha o período;
9. gera package e protocolo para handoff contábil simulado, sem envio externo real;
10. repete o fluxo em E2E sem duplicação;
11. executa a release em `onprem-lab` com dados sintéticos/anonimizados.

Tika/OCR não bloqueiam esse fluxo. Documento processado pode enriquecer evidência posteriormente.

## 9. ProductReleaseBundle

Release instalável do software, separada do pacote contábil.

Manifest mínimo planejado:

- versão/tag e commit SHA;
- imagens imutáveis por digest;
- compatibilidade de schema/migrations;
- lista de serviços/capabilities;
- configuração pública esperada;
- SBOM e checksums;
- release notes;
- requisitos de CPU/RAM/disco;
- runbooks compatíveis;
- smoke/E2E versionados;
- política de upgrade/rollback.

## 10. Topologia single-node do piloto

Conforme decisões e capabilities efetivamente implementadas, o `onprem-lab` pode conter:

```text
web
api
worker
PostgreSQL
object storage S3-compatible
Tika interno
serviços locais de processamento aprovados
```

Essa lista é de destino. A Phase 1 possui Compose de desenvolvimento apenas para web/API. O Compose do piloto é outro artefato e não deve reutilizar bind mounts, defaults inseguros ou ausência de persistência como configuração operacional.

## 11. Requisitos do bundle on-prem

- imagens versionadas e sem mutable tag como única referência;
- volumes persistentes nomeados e documentados;
- migrations idempotentes e compatibilidade verificada;
- preflight de versão, espaço, portas e permissões;
- secrets fora do repositório;
- TLS e boundary de rede decididos antes de dados reais;
- health/readiness independentes;
- logs estruturados e diagnóstico sem conteúdo sensível;
- temporários e retenção controlados;
- backup de PostgreSQL e object storage;
- restore realmente testado;
- smoke test após instalação/upgrade;
- rollback compatível com migrations e dados;
- runbooks de instalação, atualização, backup, restore e incidente.

RPO/RTO e ferramentas concretas permanecem decisões futuras. O [ADR-0014](../adr/0014-backup-and-restore-required.md) impede declarar operação real sem restore testado.

## 12. Gates de implantação

### 12.1 Demonstração sintética

Pode avançar quando:

- release é reproduzível;
- não há secrets/dados reais;
- migrations e smoke passam;
- limitações aparecem nas release notes.

### 12.2 Piloto com dados reais

Continua bloqueado até:

- decisão de autenticação/autorização e papéis;
- TLS, secrets e acesso;
- retenção, LGPD e logs;
- backup/restore testado;
- runbook e recuperação;
- aceite explícito de risco/ambiente;
- providers externos classificados e autorizados.

### 12.3 Produção on-prem

Exige Issue, envelope e decisões próprias. `onprem-lab` aprovado não autoriza `prod-onprem`.

## 13. Upgrade e rollback

Cada release define:

- origem e destino suportados;
- migrations forward e limites de rollback;
- backup/preflight obrigatório;
- ordem de atualização dos serviços;
- compatibilidade API/worker/schema;
- health/smoke de verificação;
- condição de abort/rollback;
- tratamento de job em andamento;
- evidência operacional da execução.

Rollback de container não reverte automaticamente schema. Quando downgrade de dados não for seguro, restaurar backup é operação explícita e auditada.

## 14. Observabilidade mínima

- versão/digest em execução;
- health/readiness por serviço;
- fila/jobs, retries e dead letters quando existirem;
- conexões/latência do banco e storage;
- capacidade de disco;
- falhas de backup e idade do último backup válido;
- resultado do último restore drill;
- import/close/package com correlation IDs;
- audit events separados de logs técnicos.

## 15. Definition of Ready — fechamento

- entidade, período e finalidade;
- checklist/policies versionados;
- authority levels e papéis;
- reports/totals/coverage esperados;
- blockers e exceptions permitidas;
- regras de freeze/reopen/adjustment;
- conteúdo/schema do package;
- canal de entrega e protocolo simulável;
- fixtures Golden Month e comandos E2E;
- impacto de segurança e retenção.

## 16. Definition of Ready — bundle on-prem

- topologia e serviços implementados identificados;
- versão, image build e digests;
- migrations e matriz upgrade/rollback;
- volumes e backup/restore;
- configuração pública/secrets inventory;
- health/readiness/logs;
- requisitos e preflight;
- runbooks e ownership operacional;
- smoke/E2E e expected outputs;
- ambiente alvo explícito;
- `CHECKPOINT` obrigatório para dados reais ou produção.

## 17. Critérios de aceite do piloto

### Fechamento/package

- [ ] Close congela fatos, report runs, coverage e exceções.
- [ ] Mutação comum é bloqueada após `CLOSED`.
- [ ] Reabertura cria nova versão e auditoria.
- [ ] Package possui manifest e hashes verificáveis.
- [ ] Protocolo do handoff simulado referencia exatamente a versão preparada; envio externo real permanece bloqueado pelos gates aplicáveis.
- [ ] Retorno não altera package anterior.
- [ ] Drill-through continua disponível conforme permissão.

### Product release

- [ ] Bundle identifica commit, imagens/digests e SBOM.
- [ ] Instalação limpa no `onprem-lab` passa smoke test.
- [ ] Upgrade suportado passa preflight e E2E.
- [ ] Volumes sobrevivem à recriação de containers.
- [ ] Backup e restore do conjunto persistente são demonstrados.
- [ ] Falha de serviço aparece em health/diagnóstico.
- [ ] Secrets não estão no repositório nem no manifest público.
- [ ] Compose de desenvolvimento e bundle do piloto permanecem distintos.

## 18. Documentos relacionados

- [Domínio financeiro-gerencial](MANAGERIAL_FINANCIAL_DOMAIN.md)
- [Pipeline de importação estruturada](STRUCTURED_IMPORT_PIPELINE.md)
- [Linhagem de evidência até relatório](EVIDENCE_TO_REPORT_LINEAGE.md)
- [Ambientes](../operations/AMBIENTES.md)
- [Roadmap](../project/ROADMAP.md)
- [ADR-0001 — on-prem first](../adr/0001-on-prem-first-cloud-like.md)
- [ADR-0008 — Compose local/onprem-lab](../adr/0008-docker-compose-for-local-and-onprem-lab.md)
- [ADR-0014 — backup e restore](../adr/0014-backup-and-restore-required.md)
