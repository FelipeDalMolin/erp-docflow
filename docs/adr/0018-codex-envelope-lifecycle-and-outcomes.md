# ADR-0018 — Lifecycle do envelope e outcomes do Codex

Status: Aceito  
Data: 2026-07-17  
Decisores: FelipeDalMolin  
Tags: codex, envelope, outcomes, lifecycle, governança, github-project

## Contexto

O ADR-0017 adotou o loop contínuo de slices e os outcomes `CONTINUE`, `AWAIT_DEPENDENCY`, `CHECKPOINT` e `STOP`. Ele também preservou Issue, branch, PR, revisão humana e squash merge.

O texto anterior, porém, permitia sobreposição entre dependência conhecida, decisão humana não prevista e encerramento normal do envelope. Também faltavam um lifecycle explícito, evidência mínima de aprovação e separação inequívoca entre conclusão técnica, `Review` e `Done`.

Este ADR complementa o ADR-0017. Não reescreve nem altera retroativamente ADR-0003, ADR-0005 ou ADR-0017.

## Decisão

### Lifecycle do envelope

Todo envelope usa exatamente um estado:

| Estado | Semântica | Trabalho permitido |
| --- | --- | --- |
| `Rascunho` | limites ou decisões ainda estão em elaboração | leitura, análise e planejamento; nenhuma slice é autorizada |
| `Aprovado` | objetivo, slices, ownership, exclusões, validações e checkpoints têm aprovação humana durável | executar apenas slices elegíveis e contidas no envelope |
| `Pausado` | a autorização continua registrada, mas novas slices não podem ser iniciadas | preservar trabalho existente, validar ou preparar safe stop; retomada exige registro humano |
| `Encerrado` | objetivo atingido, cancelado ou sem candidato elegível | nenhuma nova slice; nova execução exige envelope novo ou revisão aprovada |

Um envelope `Aprovado` registra responsável/decisor, data, referência da aprovação, objetivo, slices, áreas e paths permitidos, ownership, exclusões, dependências, validações, checkpoints e condição de encerramento.

A Epic ou Issue que governa o lote mantém o estado corrente no corpo. O histórico de edição do GitHub e a referência registrada constituem evidência durável. Mudança de limites, ownership ou exclusões exige nova revisão humana no mesmo corpo.

### Outcomes exclusivos

Ao avaliar continuidade, selecionar exatamente um outcome:

| Outcome | Condição exclusiva | Exemplo | Condição de retomada |
| --- | --- | --- | --- |
| `CONTINUE` | existe próximo item elegível, independente de conteúdo não mergeado, dentro do envelope e sem decisão nova | iniciar frontend em paralelo ao backend após o workspace mergeado e ownership disjunto | início imediato da próxima slice |
| `AWAIT_DEPENDENCY` | existe dependência conhecida e esperada cuja conclusão não exige nova decisão | aguardar squash merge do PR que fornece o workspace | evidência objetiva de conclusão da dependência |
| `CHECKPOINT` | surgiu ambiguidade, risco, conflito ou ação/decisão humana não prevista | uma slice precisa tocar path de outro owner | decisão humana registrada com impacto e direção |
| `STOP` | envelope foi encerrado ou não existe candidato elegível | todas as slices do lote foram concluídas | novo envelope ou revisão humana explícita |

Aplicar esta ordem:

1. envelope `Encerrado` ou sem candidato: `STOP`;
2. decisão, risco, conflito ou ação humana não prevista: `CHECKPOINT`;
3. dependência conhecida e esperada: `AWAIT_DEPENDENCY`;
4. próximo item elegível: `CONTINUE`.

Um outcome não substitui o estado do envelope. `AWAIT_DEPENDENCY` e `CHECKPOINT` não pausam o envelope automaticamente; `STOP` registra a parada e acompanha o encerramento quando o lote terminou.

### Persistência do outcome

Quando existir PR, registrar exatamente um outcome na seção **Decisão de continuidade do Codex** da descrição do PR, incluindo fato observado, próximo item ou dependência, condição de retomada e referência ao envelope.

Quando não existir PR, registrar o outcome em comentário na Issue ou Epic correspondente. O corpo permanece a fonte do estado corrente do envelope; comentários preservam eventos de continuidade.

### Conclusão técnica, Review e Done

- **Conclusão técnica:** implementação, validações, documentação e PR draft estão preparados.
- **Pronto para Review:** PR não está mais draft, checks cabíveis foram executados e o diff está pronto para revisão humana.
- **Review:** status operacional usado quando o PR está pronto para revisão humana.
- **Done:** PR revisado, squash-mergeado, Issue fechada e estado do Project reconciliado.

Conclusão técnica não move a Issue para `Review` ou `Done`. O Codex não faz merge.

### Gate de Phase

Uma transição entre slices já previstas não é gate de Phase. Gate de Phase exige evidência e decisão humana quando altera autorização, risco, arquitetura, segurança, dados, infraestrutura sensível ou condição de saída da fase.

### Vocabulário do produto

Os outcomes pertencem à governança de execução do Codex. `RoutingDecision` continua sendo conceito planejado do pipeline documental e não usa esses outcomes como enum implícito.

## Compatibilidade

- usos anteriores de `AWAIT_DEPENDENCY` para dependência conhecida continuam válidos;
- dependência que exige decisão ou coordenação não prevista passa a usar `CHECKPOINT`;
- fim normal do lote usa `STOP`;
- ADR-0017 permanece preservado e deve ser interpretado junto deste complemento;
- nenhuma automação, label ou campo novo é criada por esta decisão.

## Alternativas consideradas

### Manter a semântica apenas em documentos operacionais

Rejeitada porque permitiria divergência futura sem uma decisão primária.

### Alterar o ADR-0017 como documento vivo

Rejeitada para preservar o histórico da decisão aceita.

### Criar outcomes adicionais

Rejeitada porque quatro outcomes exclusivos cobrem continuidade, espera, decisão e encerramento.

## Consequências positivas

- reduz checkpoints mecânicos;
- distingue espera previsível de decisão humana;
- torna aprovação, pausa e encerramento auditáveis;
- separa conclusão técnica, `Review` e `Done`;
- fornece condição objetiva de retomada.

## Consequências negativas / trade-offs

- exige manter o corpo da Epic/Issue atualizado;
- exige registrar um único outcome ao concluir tecnicamente a slice;
- envelopes vagos continuam inválidos e demandam refinamento.

## Impacto técnico

### Documentação afetada

- `AGENTS.md`;
- `docs/operations/FLUXO_GITHUB_PROJECT.md`;
- `docs/project/MODELO_OPERACIONAL_DO_PROJETO.md`;
- `docs/project/ROADMAP.md`;
- `docs/templates/`;
- `docs/traceability/`;
- `docs/uml/`.

### Código, módulos, entidades e rotas

Nenhum código de produto, módulo, entidade ou rota é criado.

### Infraestrutura

Nenhum runner, automerge, deploy, branch protection ou agente persistente é criado.

### Testes necessários

- links e fences Markdown;
- catálogo e índice de ADR;
- consistência dos outcomes;
- pares PlantUML;
- Structural CI existente.

## Relações

Substitui: nenhum.  
Substituído por: —  
Complementa: ADR-0017.  
Complementado por: —  
Relacionado a: ADR-0003, ADR-0005, ADR-0006 e ADR-0007.

## Critérios para revisão futura

Revisar quando:

- o Project materializar lifecycle ou outcomes como automação;
- pausas e retomadas gerarem interpretações divergentes;
- a política de review/merge mudar;
- existir agente persistente;
- métricas indicarem que os quatro outcomes não são exclusivos.
