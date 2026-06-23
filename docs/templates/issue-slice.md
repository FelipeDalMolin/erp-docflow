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

Selecionar uma:

- [ ] Não Verificado
- [ ] Condições Verificadas
- [ ] Precisa Especificação
- [ ] Precisa ADR
- [ ] Precisa Decisão Humana
- [ ] Bloqueado

## Modo de Execução

Selecionar uma:

- [ ] Não Definido
- [ ] Manual
- [ ] Assistido por Codex
- [ ] Somente Revisão Codex
- [ ] Pareamento / Chat + Humano

## Restrições para Codex

- Não executar fora do escopo desta Issue.
- Não alterar ADR aceito sem novo ADR.
- Não criar código de produto durante a Phase 0 sem Issue explícita.
- Não criar deploy, secrets, automerge ou branch protection sem escopo explícito.
- Parar e pedir decisão humana se houver mudança arquitetural, segurança, dados sensíveis ou escopo ambíguo.
