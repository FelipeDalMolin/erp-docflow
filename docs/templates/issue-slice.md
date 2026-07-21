# Objetivo

Descrever o objetivo específico da Issue/Slice.

## Contexto

Explicar o contexto necessário para executar a Issue sem depender de decisões escondidas no chat.

## Escopo

- Item 1
- Item 2
- Item 3

## Fora de escopo

- Item fora de escopo 1
- Item fora de escopo 2

## Critérios de aceite

- [ ] Critério verificável 1
- [ ] Critério verificável 2
- [ ] Critério verificável 3

## Validação esperada

Comandos, revisão manual ou evidências esperadas:

```bash
# exemplo
```

## Dependências e paths

Dependências obrigatórias:

- #<numero ou `nenhuma`>

Paths permitidos:

- `<path>`

Paths protegidos ou excluídos:

- `<path>`

Ownership e sobreposição:

- owner por path:
- branches/PRs concorrentes verificados:
- condição de desbloqueio:

## Contrato de execução

Entradas:

- `<tipo, schema/versão, origem e classificação>`

Saídas:

- `<artefato, estado, evento ou comportamento observável>`

Invariantes:

- `<o que nunca pode ser perdido, sobrescrito ou duplicado>`

Tecnologia e estratégia:

- decidida: `<tecnologia/algoritmo/política e fonte da decisão>`
- candidata sob benchmark: `<candidato, spike/benchmark e gate de promoção>`
- não aplicável: `<justificativa, quando não houver escolha técnica>`

Experimento e promoção, quando aplicável:

- pergunta/hipótese e baseline:
- `ExperimentManifest` / `BenchmarkRun`:
- package, lockfile, config e artifact digest usados:
- paridade entre experimento, teste, runtime e release:
- critério de promoção, rejeição ou inconclusão:

Artefatos, proveniência e lineage:

- persistidos:
- `derived_from` / referência à origem:
- regra/profile/modelo e versão:

Falhas e controle:

- reason codes:
- idempotência:
- timeout/retry/replay:
- comportamento parcial/indisponível:

Fixtures e dados permitidos:

- dataset/manifest:
- casos válidos, inválidos, ambíguos e limites:
- sensibilidade/autorização:

Métricas e targets:

- qualidade/correção:
- latência/custo/recursos, quando aplicável: `<p50/p95, throughput, CPU-seconds, RSS pico, cold/warm start, disco/cache>`
- taxa de review/erro, quando aplicável:

UX, quando aplicável:

- loading, vazio, sucesso parcial, erro, bloqueado e sem permissão:
- teclado/foco/acessibilidade:

## Relação com Epic

Epic relacionada:

- #<numero>

## Relação com ADRs

ADRs relacionados:

- ADR-000X

Criar novo ADR?

- [ ] Não
- [ ] Sim, explicar:

## Relação com documentação

Documentos afetados:

- `docs/...`

## Impacto esperado

- Docs:
- ADRs:
- Traceability:
- UML:
- Módulos:
- Entidades:
- Rotas:
- Infra:

## Condição de Execução

Selecionar exatamente uma e manter as demais desmarcadas:

- [ ] Não Verificado
- [ ] Condições Verificadas
- [ ] Precisa Especificação
- [ ] Precisa ADR
- [ ] Precisa Decisão Humana
- [ ] Bloqueado

## Modo de Execução

Selecionar exatamente uma e manter as demais desmarcadas:

- [ ] Não Definido
- [ ] Manual
- [ ] Assistido por Codex
- [ ] Somente Revisão Codex
- [ ] Pareamento / Chat + Humano

## Continuidade após este slice

Envelope/Epic aprovado:

- #<numero ou referência>

Estado do envelope:

- `Rascunho | Aprovado | Pausado | Encerrado`

Responsável, data e referência da aprovação:

- <registro>

Próximo candidato conhecido:

- #<numero> — <título>

Dependência após este slice:

- [ ] O próximo candidato é independente e pode ser puxado após o PR draft.
- [ ] O próximo candidato depende do merge deste PR.
- [ ] Há checkpoint humano previsto.
- [ ] Encerrar o envelope.

O Codex deve registrar `CONTINUE`, `AWAIT_DEPENDENCY`, `CHECKPOINT` ou `STOP` ao concluir tecnicamente o slice.

Registrar exatamente um outcome na descrição do PR, com:

- fato observado;
- referência ao envelope;
- próximo item ou dependência;
- condição de retomada.

Sem PR, registrar o outcome em comentário na Issue ou Epic correspondente.

## Restrições para Codex

- Não executar fora do escopo desta Issue.
- Não alterar ADR aceito sem novo ADR.
- Não iniciar código de produto sem slice especificada, condições verificadas e envelope aprovado.
- Não criar deploy, secrets, automerge ou branch protection sem escopo explícito.
- Parar e pedir decisão humana se houver mudança arquitetural, segurança, dados sensíveis ou escopo ambíguo.
- Não pedir nova aprovação apenas porque o slice terminou quando houver próximo item elegível no envelope.
