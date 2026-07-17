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
