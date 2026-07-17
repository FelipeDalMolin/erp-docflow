# Fluxo do GitHub Project

- **Classe:** normativo operacional do lifecycle de trabalho
- **Estado:** vigente
- **Autoridade:** tipos de item, estados, condição de execução, modo de colaboração e outcomes do Codex
- **Atualizar quando:** campos/opções reais do Project ou critérios de prontidão mudarem

Este documento define como o GitHub Project será usado para acompanhar o `erp-docflow` durante a Phase 0 e nas fases seguintes.

O objetivo é garantir que Epics, Issues e sub-issues sejam criadas com nomenclatura, tags/labels, campos e critérios de aceite suficientes para permitir execução assistida por Codex sem perder controle humano.

## 1. Princípio operacional

O GitHub Project é o painel de controle do trabalho.

O repositório deve evitar tarefas soltas no chat, sem Issue, sem critério de aceite ou sem vínculo com uma entrega maior.

Todo trabalho relevante deve seguir:

```text
Epic -> Issue/Slice -> Sub-issue opcional -> Branch -> Commit -> Pull Request -> Review humana -> Squash merge
```

A Phase 0 foi encerrada; a Phase 1 está em refinamento. Uma Epic aberta não torna suas slices executáveis. O snapshot atual e o gate ficam em [Status do projeto](../project/PROJECT_STATUS.md).

## 2. Tipos de item

### 2.1 Epic

Uma Epic representa um agrupamento de valor ou uma frente relevante do projeto.

Usar Epic quando houver várias Issues relacionadas por objetivo comum.

Exemplo:

```text
[E0] Sistema operacional do projeto
```

A Epic deve conter:

- objetivo;
- escopo geral;
- fora de escopo;
- lista de Issues/Slices relacionadas;
- critério de conclusão da Epic.

### 2.2 Issue ou Slice

Uma Issue/Slice é a menor unidade executável por humano ou Codex.

A Issue deve ser pequena o suficiente para virar um PR revisável.

Exemplo:

```text
[S0.02] Definir fluxo do GitHub Project
```

A Issue deve conter:

- objetivo;
- escopo;
- fora de escopo;
- critérios de aceite;
- riscos ou decisões pendentes;
- validação esperada;
- relação com Epic, se aplicável.

### 2.3 Sub-issue

Uma sub-issue deve ser usada quando uma Issue ficou grande demais ou possui partes independentes.

Exemplo:

```text
[S0.02.01] Criar taxonomia de labels e campos do Project
```

Sub-issues devem preservar vínculo com a Issue pai.

Não criar sub-issue apenas para registrar uma observação pequena. Nesse caso, usar comentário na Issue principal.

## 3. Nomenclatura

Padrão recomendado:

```text
[E<numero>] <nome-da-epic>
[S<fase>.<sequencia>] <nome-do-slice>
[S<fase>.<sequencia>.<subsequencia>] <nome-da-sub-issue>
```

Exemplos:

```text
[E0] Sistema operacional do projeto
[S0.02] Definir fluxo do GitHub Project
[S0.03] Definir fluxo VS Code, Git e GitHub CLI
[S0.03.01] Validar autenticação do GitHub CLI no WSL
```

Regras:

- usar título claro e acionável;
- evitar título genérico como `ajustes`, `melhorias` ou `documentação`;
- manter a numeração estável depois de usada;
- não reaproveitar número de Issue concluída;
- usar verbos como `Definir`, `Criar`, `Documentar`, `Validar`, `Configurar`, `Revisar`.

## 4. Taxonomia alvo de labels/tags

A taxonomia abaixo é o vocabulário alvo para organizar o Project. Ela não descreve automaticamente labels já criadas ou aplicadas.

No snapshot de 2026-07-14, as Issues legadas não possuem essa taxonomia aplicada. A materialização e aplicação retroativa exigem trabalho operacional próprio. O estado desse gap pertence a [Status do projeto](../project/PROJECT_STATUS.md).

### 4.1 Tipo

```text
type:epic
type:slice
type:sub-issue
type:docs
type:adr
type:chore
type:ci
type:security
```

### 4.2 Fase

```text
phase:0
phase:1
phase:2
```

### 4.3 Status operacional

```text
status:needs-plan
status:ready
status:in-progress
status:review
status:blocked
status:done
```

### 4.4 Codex

```text
codex:eligible
codex:plan-required
codex:human-review
codex:not-eligible
```

### 4.5 Área

```text
area:github-project
area:vscode
area:git
area:github-cli
area:docs
area:adr
area:ci
area:security
area:environment
```

A criação efetiva dessas labels no GitHub pode ser feita manualmente ou em Issue própria. Até isso ocorrer, título, campos do Project e corpo da Issue continuam sendo as evidências; não se deve fingir que uma label proposta está configurada.

## 5. Campos do Project

O Project deve permitir entender estado, prontidão e modo de execução de cada item.

Campos mínimos recomendados:

| Campo | Uso |
| --- | --- |
| Status | Posição do item no fluxo de trabalho. |
| Condição de Execução | Indica se o item está pronto, bloqueado ou precisa de decisão. |
| Modo de Execução | Indica a forma de colaboração: manual, assistida, somente revisão ou pareamento. |
| Tipo | Epic, Slice, Sub-issue, ADR, documentação, chore. |
| Área | Parte do projeto afetada. |
| Fase | Phase 0, Phase 1 etc. |
| Prioridade | Ordem relativa de execução. |
| Issue pai/Epic | Relação com entrega maior. |

Esta lista define o modelo desejado. Antes de usar um valor como critério automatizado, conferir se o campo e a opção existem de fato no Project. `Fase` deve ser o classificador primário; milestones não são usadas atualmente e não devem duplicar a mesma função sem decisão explícita.

## 6. Status

### Backlog

Item registrado, mas ainda não refinado.

Critério:

- pode estar incompleto;
- ainda não deve ser executado;
- pode precisar de Plan.

### Ready

Item pronto para execução.

Critério:

- possui objetivo;
- possui escopo;
- possui fora de escopo;
- possui critérios de aceite;
- não possui decisão bloqueante;
- tem modo de execução definido.

### In progress

Item em execução em branch própria.

Critério:

- existe branch relacionada;
- escopo está em execução;
- não deve haver trabalho paralelo conflitante no mesmo slice.

### Review

Existe PR aberto e pronto para revisão humana.

Critério:

- PR referencia a Issue;
- validações cabíveis foram executadas ou justificadas;
- documentação e ADR foram considerados.

Uma Issue em `Review` ainda não está `Done`. Isso não impede o Codex de puxar outro slice independente, pronto e pertencente ao mesmo envelope.

### Done

Item concluído.

Critério:

- PR foi revisado;
- PR foi mergeado;
- Issue foi fechada;
- critérios de aceite foram atendidos.

### Blocked

Item bloqueado por decisão, dependência, permissão, ambiente ou risco.

Critério:

- bloqueio explícito descrito na Issue;
- próximo passo humano identificado.

## 7. Condição de Execução

A Condição de Execução responde: o item pode ser executado agora?

Valores canônicos:

```text
Não Verificado
Precisa Especificação
Precisa Decisão Humana
Precisa ADR
Bloqueado
Condições Verificadas
```

### Precisa Especificação

Usar quando o problema existe, mas ainda falta decomposição técnica.

O Codex pode ajudar a produzir mini especificação técnica, riscos, escopo e critérios de aceite.

### Precisa Decisão Humana

Usar quando existe uma escolha de produto, arquitetura, segurança, dados, provider, persistência ou operação que não pode ser inferida da documentação vigente.

### Precisa ADR

Usar quando a execução depende de nova decisão arquitetural ou de revisão formal indicada por ADR existente.

### Condições Verificadas

Usar quando a Issue já pode virar branch e PR.

Critérios mínimos:

- escopo claro;
- fora de escopo definido;
- critérios de aceite verificáveis;
- riscos conhecidos;
- nenhuma decisão arquitetural pendente;
- nenhuma área protegida sem autorização explícita.

`Não Verificado` é o estado inicial. `Bloqueado` registra impedimento objetivo. Conclusão pertence ao campo `Status = Done`, não à Condição de Execução.

## 8. Modo de Execução

O Modo de Execução define a forma de colaboração. Ele não é sinônimo do nível técnico de permissão do Codex.

Valores canônicos:

```text
Não Definido
Manual
Assistido por Codex
Somente Revisão Codex
Pareamento / Chat + Humano
```

`Não Definido` é apenas o estado inicial e impede que o item seja considerado pronto.

### Manual

Usar quando envolver decisão de negócio, credencial, dado real, permissão, deploy, branch protection ou ação sensível.

### Assistido por Codex

Usar quando o Codex pode planejar ou executar a parte autorizada e preparar evidências/PR sob revisão humana.

### Somente Revisão Codex

Usar quando a execução é humana e o Codex atua apenas em leitura, análise ou review.

### Pareamento / Chat + Humano

Usar quando decisões e checkpoints fazem parte do próprio trabalho.

### Nível técnico da sessão Codex

`Read`, `Plan` e `Workspace-write` descrevem capacidade técnica da sessão e continuam sujeitos a sandbox/permissões. A Issue/envelope autoriza escopo; a configuração técnica não concede escopo por si só.

Quando útil, registrar o nível esperado no plano ou na Issue, sem misturá-lo ao campo `Modo de Execução`.

## 9. Critério para elegibilidade do Codex

Uma Issue pode entrar na fila elegível — e receber `codex:eligible` quando a label existir — quando:

- possui objetivo claro;
- possui escopo e fora de escopo;
- possui critérios de aceite;
- não exige segredo, credencial ou dado real;
- não exige deploy;
- não altera branch protection;
- não altera ADR aceito sem novo ADR;
- não exige comando destrutivo;
- pode ser entregue em PR pequeno;
- validações cabíveis são conhecidas ou justificáveis.

Se faltar qualquer item relevante, manter `Precisa Especificação`, `Precisa Decisão Humana`, `Precisa ADR` ou `Bloqueado`. Labels auxiliares não substituem o campo canônico.

## 9.1 Loop de continuidade do Codex

Elegibilidade indica que a Issue pode entrar na fila de pull. Uma eventual label `codex:eligible` não concede autonomia fora do contexto aprovado.

Antes da execução, o Plan Mode pode aprovar um **envelope de execução** contendo:

- estado `Rascunho`, `Aprovado`, `Pausado` ou `Encerrado`;
- responsável, data e referência da aprovação;
- objetivo do lote;
- slices explícitos ou critério de seleção;
- áreas permitidas e excluídas;
- paths e ownership quando houver paralelismo;
- dependências;
- validações;
- checkpoints humanos;
- condição de encerramento.

O corpo da Epic ou Issue governante mantém o estado corrente e a evidência durável:

- `Rascunho`: planejamento, sem autorização de slice;
- `Aprovado`: execução limitada ao escopo registrado;
- `Pausado`: nenhuma nova slice pode começar;
- `Encerrado`: retomada exige envelope novo ou revisão aprovada.

Alterar limites, ownership ou exclusões exige nova revisão humana registrada no corpo.

Não é obrigatório criar novo campo no Project. A fila pode ser formada por:

```text
Status = Ready
Condição de Execução = Condições Verificadas
Modo de Execução = Assistido por Codex
Epic/envelope = aprovado
Dependências = satisfeitas ou item independente
```

Ao concluir tecnicamente um slice, o Codex avalia a fila e registra:

| Decisão | Uso |
| --- | --- |
| `CONTINUE` | puxar o próximo slice elegível sem nova aprovação mecânica |
| `AWAIT_DEPENDENCY` | aguardar dependência conhecida e esperada, sem decisão nova |
| `CHECKPOINT` | pedir orientação por decisão/ação humana não prevista, risco, conflito ou ambiguidade |
| `STOP` | encerrar o envelope ou parar por falta de candidato |

Selecionar exatamente uma decisão:

1. envelope encerrado ou sem candidato elegível: `STOP`;
2. decisão, risco, conflito ou ação humana não prevista: `CHECKPOINT`;
3. dependência conhecida e esperada: `AWAIT_DEPENDENCY`;
4. próximo item elegível: `CONTINUE`.

Registrar fato, referência ao envelope e condição de retomada na descrição do PR. Sem PR, registrar em comentário na Issue ou Epic correspondente.

### Regra para PR pendente

O Codex pode iniciar outro slice enquanto um PR aguarda review somente quando:

- o novo slice é independente;
- a branch parte da `main`;
- não depende do conteúdo ainda não mergeado;
- não há sobreposição relevante de arquivos ou decisão;
- o envelope autoriza continuidade.

Se houver dependência conhecida e esperada, o item permanece `Ready` ou `Blocked`, conforme o caso, e a decisão é `AWAIT_DEPENDENCY`. Se a dependência exigir decisão ou coordenação não prevista, usar `CHECKPOINT`.

Branch/PR empilhado não é padrão. Só deve ser usado quando previsto explicitamente no envelope.

### Checkpoint humano

Pedir checkpoint quando houver:

- nova decisão arquitetural, de negócio ou de segurança;
- banco, storage, fluxo de aceite, dado real ou provider externo;
- CI, deploy, branch protection, secrets ou área protegida não autorizada;
- conflito entre candidatos ou prioridades;
- falha de validação que exija ampliar escopo;
- fim do lote ou gate de Phase.

O checkpoint deve informar fato, impacto, opções e recomendação.

### Merge

O loop não altera a revisão humana. O Codex prepara PRs e pode continuar com trabalho independente, mas não faz merge automático.

## 10. Fluxo para criar nova Epic

Checklist:

```text
[ ] Título segue padrão [E<num>] <nome>.
[ ] Objetivo da Epic está claro.
[ ] Escopo geral está definido.
[ ] Fora de escopo está definido.
[ ] Issues/Slices iniciais foram listadas ou planejadas.
[ ] Critério de conclusão da Epic está claro.
[ ] Envelope de execução e checkpoints estão definidos quando houver loop Codex.
[ ] Labels mínimas foram aplicadas.
[ ] Epic foi vinculada ao Project.
```

Labels sugeridas:

```text
type:epic
phase:<fase>
status:needs-plan
```

Aplicar apenas quando a taxonomia tiver sido criada; caso contrário, preencher os campos e o corpo da Epic.

## 11. Fluxo para criar nova Issue/Slice

Checklist:

```text
[ ] Título segue padrão [S<fase>.<sequencia>] <nome>.
[ ] Issue está vinculada a uma Epic quando aplicável.
[ ] Objetivo está claro.
[ ] Escopo está delimitado.
[ ] Fora de escopo está declarado.
[ ] Critérios de aceite são verificáveis.
[ ] Modo de execução está definido.
[ ] Condição de execução está definida.
[ ] Labels mínimas foram aplicadas.
[ ] Não há decisão crítica escondida no chat.
[ ] Continuidade após o slice foi indicada: candidato, dependência ou checkpoint.
```

Labels sugeridas:

```text
type:slice
phase:<fase>
area:<area>
status:needs-plan ou status:ready
codex:plan-required ou codex:eligible
```

Aplicar apenas quando a taxonomia tiver sido criada; a condição canônica continua no campo/corpo da Issue.

## 12. Fluxo para criar sub-issue

Criar sub-issue quando:

- a Issue principal ficou grande demais;
- há entregas independentes;
- há risco de PR grande;
- há partes que podem ser revisadas separadamente.

Checklist:

```text
[ ] Título segue padrão [S<fase>.<sequencia>.<subsequencia>] <nome>.
[ ] Issue pai está referenciada.
[ ] Escopo da sub-issue é independente.
[ ] Critérios de aceite não duplicam a Issue pai.
[ ] Labels foram herdadas ou ajustadas.
```

## 13. Quando mover para Review

Mover para Review quando:

- existe PR aberto;
- o PR não está mais em draft;
- PR referencia a Issue;
- diff está pequeno e revisável;
- validações cabíveis foram executadas ou justificadas;
- documentação afetada foi atualizada;
- ADR foi considerado quando aplicável;
- não há mudança fora de escopo.

## 14. Quando considerar concluído

Considerar concluído quando:

- PR foi revisado por humano;
- PR foi aprovado ou aceito;
- PR foi squash-mergeado;
- Issue foi fechada;
- Project foi atualizado para Done;
- decisões relevantes foram documentadas.

Preparar um PR e decidir `CONTINUE` não move a Issue automaticamente para `Done`.

## 15. Padronização operacional versus automação real

O repositório já possui modelos de referência em [`docs/templates/`](../templates/), mas eles não são templates nativos do GitHub. Padronização operacional significa checklist, nomenclatura, campos e fluxo repetível; não prova que labels, formulários ou automações estejam instalados.

Automação real pode ser criada futuramente, por exemplo:

- templates nativos de Issue;
- template nativo de PR;
- GitHub Actions para validar título;
- GitHub Actions para validar labels;
- script para criar labels;
- automações do Project.

Essas automações devem ser tratadas em Issues próprias, com escopo explícito.
