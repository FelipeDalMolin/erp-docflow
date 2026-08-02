# Contrato de persistência e storage do intake PDF-first

Status documental: contrato planejado e ratificado para o protótipo local sintético, não implementado
Atualizado em: 2026-07-31
Issue de origem: [#38](https://github.com/FelipeDalMolin/erp-docflow/issues/38)
Envelope de execução: [#92](https://github.com/FelipeDalMolin/erp-docflow/issues/92)
ADRs relacionados: ADR-0010, ADR-0011, ADR-0012, ADR-0014 e ADR-0015 (proposto)

## 1. Finalidade e autoridade

Este documento fecha os gates mínimos de persistência, object storage, integridade, idempotência e acesso provisório antes do primeiro intake PDF-first. Ele especializa, para o protótipo local com fixtures sintéticas, o [baseline de dados](DATA_MODEL_BASELINE.md) e o [pipeline documental](DOCUMENT_PIPELINE.md).

O contrato ratifica uma direção de implementação futura; não prova nem cria schema, migrations, repositórios, endpoint de upload, serviços PostgreSQL/MinIO, volumes, credenciais ou dados persistidos. Código e testes das Issues #39 e #40 serão a evidência de implementação quando seus próprios gates forem satisfeitos.

As revisões previstas nas ADR-0010, ADR-0011 e ADR-0012 ficam atendidas para esse recorte local e sintético, sem alterar essas ADRs. Mudança de banco, interface de storage, modelo GED, acesso, exposição ou classe de dado exige novo checkpoint e, quando aplicável, ADR sucessor.

## 2. Limite do protótipo autorizado

O recorte autorizado é:

- execução local, sem exposição externa;
- PDFs, imagens e demais fixtures exclusivamente sintéticas autorizadas pelo profile;
- um `tenant_id` e um ator/reviewer de desenvolvimento fixos, injetados pelo servidor;
- configuração somente por ambiente ou placeholders sem valor secreto versionado;
- persistência transacional no PostgreSQL e binários em MinIO por interface S3-compatible;
- intake encerrado em `INSPECTION_PENDING`, sem Tika, OCR, extração, classificação ou review funcional.

Esse recorte não constitui autenticação, autorização, RBAC, ABAC ou segregação multi-tenant. O cliente não escolhe nem sobrescreve tenant, ator ou reviewer. Dado real, múltiplos tenants, acesso remoto, exposição externa ou efeito operacional permanecem bloqueados pela ADR-0015 até decisão sucessora e autorização humana registradas.

## 3. Autoridade de estado e de conteúdo

| Responsabilidade | Autoridade planejada | Invariante |
| --- | --- | --- |
| estado do intake, envelope, versão, ocorrência, referências e audit event | PostgreSQL | é a fonte canônica do estado transacional |
| original e futuros derivados binários | MinIO por interface S3-compatible | objetos são imutáveis e verificados por SHA-256 e tamanho |
| correlação entre estado e objeto | referência persistida no PostgreSQL | uma referência não comprova integridade sem verificação do objeto |

Blobs não são gravados no PostgreSQL. A chave de objeto é opaca, não expõe nome original, CNPJ, tenant legível ou outro dado sensível e não depende de ETag para integridade. A estratégia física exata da chave será fechada na #40 sem mudar essas invariantes.

O domínio depende de uma porta S3-compatible, não de SDK ou tipos do MinIO. MinIO é a implementação ratificada somente para o protótipo local sintético; qualquer uso em `onprem-lab`, dado real ou outro ambiente permanece sujeito aos gates operacionais e de segurança.

O nome original e demais metadados permitidos pertencem ao estado transacional e obedecem a classificação, retenção e mascaramento futuros. Não devem aparecer em object keys, logs técnicos ou mensagens de erro inseguras.

## 4. Integridade e observações do intake

Durante o streaming de entrada, o intake calcula de forma incremental:

- SHA-256 dos bytes efetivamente recebidos;
- tamanho efetivo em bytes;
- `intake_detected_mime` por inspeção preliminar segura, versionada e aprovada.

ETag é metadado do protocolo/storage e não substitui SHA-256. Uma gravação só é considerada íntegra quando conteúdo recuperável, SHA-256 e tamanho efetivamente persistidos conferem com a ocorrência registrada. Escrita do original é imutável e condicional: se a chave física já existir, a #40 deverá comprovar igualdade de hash e tamanho antes de qualquer reaproveitamento e jamais sobrescrever conteúdo divergente.

As três observações de MIME continuam independentes:

| Campo | Origem | Fase |
| --- | --- | --- |
| `advertised_mime` | cliente ou canal; não confiável, mas preservado | intake |
| `intake_detected_mime` | inspeção preliminar segura | intake |
| `probe_detected_mime` | futuro adapter de `probe_document` | Phase 3 |

Um valor posterior não sobrescreve outro. Divergência conhecida gera `mime_mismatch` e a razão aplicável; não autoriza nem rejeita silenciosamente o documento. Ausência ou detecção indeterminada permanece explícita e não pode ser convertida em `mime_mismatch=false`. A #40 não pode antecipar `probe_detected_mime`, Tika, contagem de páginas ou texto nativo.

## 5. Identidade, ocorrência e idempotência

Idempotência de ingestão, igualdade binária e identidade documental são dimensões diferentes:

- o namespace desta operação é `document_intake`; dentro dele, a unidade é `(tenant_id, idempotency_key)`, equivalente a `(tenant_id, operation, idempotency_key)` quando outras operações idempotentes existirem;
- o fingerprint `document-intake-v1` contém, no mínimo, SHA-256, tamanho, `advertised_mime` normalizado, nome original em Unicode NFC e origem/canal normalizados;
- a serialização canônica precisa ser determinística e versionada; acrescentar ou alterar campo semântico exige nova versão, preservando a comparação de ocorrências antigas;
- duas requisições concorrentes com a mesma unidade são serializadas por constraint e operação transacional no PostgreSQL; somente uma reserva a ocorrência, e a outra compara ou retoma o estado persistido;
- SHA-256 igual indica igualdade binária, não identidade automática de documento, versão, ocorrência ou evento de negócio.

O comportamento obrigatório é:

| Situação | Resultado |
| --- | --- |
| mesma chave e mesmo fingerprint | retornar os mesmos identificadores e o estado corrente da ocorrência existente, sem duplicar envelope, versão, objeto ou audit event de sucesso |
| mesma chave e fingerprint diferente por conteúdo ou metadados | conflito explícito com `IDEMPOTENCY_CONFLICT`; a ocorrência anterior permanece inalterada |
| SHA-256 igual com chave diferente | preservar ocorrências e auditorias distintas; eventual reaproveitamento físico não realiza merge documental |
| retry ou restart da mesma operação incompleta | retomar ou reconciliar a ocorrência existente, sem criar sucesso duplicado |

A chave vem do canal, mas o `tenant_id` usado no escopo é sempre o valor provisório injetado pelo servidor. Ausência, formato, retenção e limites da chave serão definidos pela Issue de implementação, sem reduzir as garantias acima.

## 6. Consistência entre PostgreSQL e MinIO

O intake usa estado intermediário durável e reconciliação; não existe transação ACID distribuída implícita entre PostgreSQL e MinIO. Estados de reserva, transferência, verificação, falha e reconciliação pertencem à ocorrência de intake, nunca ao estado canônico do `DocumentEnvelope`.

Uma implementação conforme este contrato deve preservar a seguinte sequência lógica, ainda que a organização interna varie:

1. reconhecer ou reservar de modo concorrente a ocorrência pela chave de idempotência;
2. receber o stream, calcular SHA-256/tamanho e gravar o objeto sem expor uma materialização concluída;
3. verificar a recuperabilidade, o SHA-256 e o tamanho do objeto;
4. persistir atomicamente a referência verificada, a transição de estado e o `AuditEvent` associado;
5. encerrar o intake em `INSPECTION_PENDING` somente depois da materialização íntegra.

Invariantes de falha e recuperação:

- nenhum envelope alcança `MATERIALIZED` ou `INSPECTION_PENDING` antes da verificação do objeto;
- falha de storage ou de integridade mantém a ocorrência em estado não concluído e nunca produz sucesso parcial;
- falha na transação final pode deixar objeto candidato a órfão, que deve permanecer identificável para reconciliação;
- retry e restart retomam a ocorrência pela mesma identidade idempotente;
- reconciliação usa correlação opaca, respeita grace period configurado, confirma a ausência de referências e operações concorrentes e registra evidência/motivo antes de qualquer limpeza;
- deleção cega, apenas por idade, prefixo ou ausência momentânea de leitura no banco é proibida;
- um reconciliador não apaga objeto que esteja referenciado, em transferência, reservado por outra tentativa ou cuja autoridade não possa ser comprovada;
- o `AuditEvent` de sucesso participa da mesma unidade transacional que publica o novo estado; log técnico não o substitui.

Falhas externas anteriores à transação final pertencem ao diagnóstico da ocorrência e à reconciliação; não devem criar um `AuditEvent` de materialização nem fingir atomicidade distribuída.

Redis, filas, workers e outbox não são escolhidos nem implementados por este contrato. O fluxo inicial pode ser síncrono, mas precisa manter as mesmas propriedades de recuperação e auditoria.

## 7. Reason codes mínimos

Os códigos abaixo são parte do contrato de intake e não substituem status HTTP, exceção técnica ou mensagem segura ao usuário:

| Reason code | Condição mínima |
| --- | --- |
| `IDEMPOTENCY_CONFLICT` | a mesma chave no mesmo tenant foi reapresentada com fingerprint diferente |
| `STORAGE_WRITE_FAILED` | o original não pôde ser gravado por completo |
| `STORAGE_READ_FAILED` | o objeto necessário não pôde ser recuperado para verificação ou leitura |
| `STORAGE_INTEGRITY_MISMATCH` | SHA-256 ou tamanho recuperado diverge do valor registrado/esperado |
| `DATABASE_WRITE_FAILED` | a unidade transacional de estado não pôde ser concluída |
| `ORPHAN_OBJECT_PENDING_CLEANUP` | existe objeto candidato a órfão aguardando reconciliação segura |

Uma tentativa pode registrar mais de um sinal quando houver causalidade distinta. O reason code preserva uma classificação estável; detalhes de SDK, bucket, chave, SQL, credencial ou conteúdo não devem vazar na resposta ou em logs comuns.

A #40 também deverá fechar e testar os códigos de entrada para arquivo vazio, `MIME_MISMATCH`, `UNSUPPORTED_FORMAT` e `RESOURCE_LIMIT_EXCEEDED`, sem criar um vocabulário concorrente ao profile. Esses códigos estendem o mínimo de persistência acima; não autorizam probe ou processamento.

## 8. Acesso provisório e configuração

No protótipo, o servidor injeta constantes de desenvolvimento para tenant e ator/reviewer. Essas constantes:

- existem apenas no ambiente local autorizado;
- não são derivadas de header, formulário, query string ou payload controlado pelo cliente;
- identificam ações para correlação e audit trail, sem alegar identidade autenticada;
- não autorizam dado real, acesso externo ou isolamento entre organizações.

O modo local sintético precisa ser habilitado explicitamente. Sem esse perfil, sem as constantes válidas ou em ambiente incompatível, os futuros endpoints de intake permanecem indisponíveis; não há fallback para valores recebidos do cliente.

Endpoints futuros do intake devem ser vinculados somente a interfaces locais previstas pelo ambiente de desenvolvimento. A simples existência de `tenant_id` ou reviewer no modelo não satisfaz a ADR-0015.

Nomes de bucket, endpoint e demais opções não sensíveis usam ambiente/placeholders. Credenciais, senhas, tokens e chaves não são versionados; sua futura injeção e rotação dependem da slice de infraestrutura autorizada.

## 9. Restart, backup e restore

Persistência após restart é requisito de aceite do protótipo: reiniciar processo ou container da API, PostgreSQL ou MinIO não pode apagar uma ocorrência concluída nem tornar o original irrecuperável. A #40 deverá comprovar recuperação do original, SHA-256, tamanho, MIME, estado e idempotência depois do restart, usando armazenamento persistente autorizado pela slice de infraestrutura aplicável.

Remover deliberadamente dados/volumes não é restart. Nenhum runbook pode apresentar recriação destrutiva como teste de persistência.

Antes de qualquer `onprem-lab`, operação contínua ou dado real, a ADR-0014 exige backup e restore testados como um conjunto coerente:

- snapshot lógico/transacional do PostgreSQL;
- objetos e metadados necessários do storage;
- relação verificável entre referências e binários;
- procedimento de restore, verificação de integridade e evidência do resultado;
- política de retenção, RPO/RTO e tratamento de gravações concorrentes definidos pela futura slice operacional.

Backup/restore, scripts, jobs, volumes e operação de ambiente não são implementados pela #38. Sem demonstração de restore conjunto, o protótipo permanece local e sintético.

## 10. Ownership e desbloqueio das próximas slices

Esta #38 possui apenas este contrato, seu registro no índice de arquitetura e a direção correspondente no Roadmap. Ela não autoriza implementação física.

| Slice | Ownership planejado | Condições cumulativas para execução |
| --- | --- | --- |
| #39 — modelo mínimo | `DocumentEnvelope`, `DocumentVersion`, `FileObject`, ocorrência/idempotência, `AuditEvent`, migrations PostgreSQL e repositórios mínimos | merge humano da #38; conclusão e integração das #36 e #37; encerramento da #26; refinamento da #39 com paths, schema mínimo, fixtures e comandos; novo estado `Condições Verificadas` |
| #40 — original íntegro | adapter S3-compatible/MinIO, streaming, SHA-256/tamanho, MIME preliminar, round-trip, coordenação banco/storage, reconciliação, replay e testes de restart | todas as condições acima; merge humano da #39; refinamento da #40 com paths, limites, falhas, configuração e comandos; novo estado `Condições Verificadas` |

A #39 define a representação relacional mínima e suas constraints; a #40 usa esses contratos para orquestrar a fronteira com storage. A #40 não redefine entidades em paralelo, e a #39 não implementa adapter MinIO. Os paths exatos de código pertencem ao refinamento de cada Issue; não podem ser inferidos deste documento.

Branches empilhadas não estão autorizadas. Cada slice futura parte da `main` depois dos merges humanos exigidos e permanece dentro do envelope aprovado.

## 11. Fora de escopo desta decisão

- schema, migrations, ORM, models, repositórios ou upload HTTP;
- PostgreSQL, MinIO, buckets, volumes ou Compose;
- Tika, OCR, providers, filas, workers, Redis ou processamento;
- preview, extração, classificação, revisão ou UI;
- autenticação real, autorização, dado real, exposição externa ou deploy;
- secret, backup/restore automatizado, automerge ou branch protection.

## 12. Critérios de conformidade futura

Uma implementação só poderá declarar conformidade quando testes reproduzíveis demonstrarem:

- round-trip do original com SHA-256 e tamanho preservados;
- separação entre os três níveis de MIME;
- idempotência e conflito conforme a matriz deste contrato;
- ausência de materialização em falhas de storage, integridade ou banco;
- reconciliação sem deleção cega;
- `AuditEvent` e estado publicados atomicamente;
- recuperação após restart sem duplicação;
- tenant e ator/reviewer provisórios injetados pelo servidor;
- nenhuma credencial, dado real ou exposição externa.

Até essa evidência existir, PostgreSQL, MinIO, intake e persistência permanecem **planejados e não implementados**.
