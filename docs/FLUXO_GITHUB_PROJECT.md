# Fluxo do GitHub Project

Este documento define como o GitHub Project será usado para acompanhar o `erp-docflow` durante a Phase 0 e nas fases seguintes.

O objetivo é garantir que Epics, Issues e sub-issues sejam criadas com nomenclatura, tags/labels, campos e critérios de aceite suficientes para permitir execução assistida por Codex sem perder controle humano.

## 1. Princípio operacional

O GitHub Project é o painel de controle do trabalho.

O repositório deve evitar tarefas soltas no chat, sem Issue, sem critério de aceite ou sem vínculo com uma entrega maior.

Todo trabalho relevante deve seguir:

```text
Epic -> Issue/Slice -> Sub-issue opcional -> Branch -> Commit -> Pull Request -> Review humana -> Squash merge
```

Durante a Phase 0, o foco é documentar o sistema operacional do projeto. Código de produto, deploy e automações complexas ficam fora de escopo, salvo Issue explícita.

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

## 4. Labels/tags iniciais

A taxonomia abaixo é a proposta mínima para organizar o Project.

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

A criação efetiva dessas labels no GitHub pode ser feita manualmente ou em Issue própria. Este documento define a taxonomia; não obriga automação real nesta etapa.

## 5. Campos do Project

O Project deve permitir entender estado, prontidão e modo de execução de cada item.

Campos mínimos recomendados:

| Campo | Uso |
| --- | --- |
| Status | Posição do item no fluxo de trabalho. |
| Condição de Execução | Indica se o item está pronto, bloqueado ou precisa de decisão. |
| Modo de Execução | Indica se será feito por humano, Codex Plan, Codex Workspace-write ou misto. |
| Tipo | Epic, Slice, Sub-issue, ADR, documentação, chore. |
| Área | Parte do projeto afetada. |
| Fase | Phase 0, Phase 1 etc. |
| Prioridade | Ordem relativa de execução. |
| Issue pai/Epic | Relação com entrega maior. |

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

Valores recomendados:

```text
Needs refinement
Needs decision
Ready for Plan
Ready for execution
Blocked
Done
```

### Ready for Plan

Usar quando o problema existe, mas ainda falta decomposição técnica.

O Codex pode ajudar a produzir mini especificação técnica, riscos, escopo e critérios de aceite.

### Ready for execution

Usar quando a Issue já pode virar branch e PR.

Critérios mínimos:

- escopo claro;
- fora de escopo definido;
- critérios de aceite verificáveis;
- riscos conhecidos;
- nenhuma decisão arquitetural pendente;
- nenhuma área protegida sem autorização explícita.

## 8. Modo de Execução

O Modo de Execução define como o trabalho deve ser conduzido.

Valores recomendados:

```text
Human only
Codex Read
Codex Plan
Codex Workspace-write
Hybrid
```

### Human only

Usar quando envolver decisão de negócio, credencial, dado real, permissão, deploy, branch protection ou ação sensível.

### Codex Read

Usar para inspeção, revisão, análise de Issue, levantamento de risco ou leitura de documentação.

### Codex Plan

Usar quando a Issue ainda precisa de decomposição, critérios de aceite ou análise de impacto.

Não deve editar arquivos.

### Codex Workspace-write

Usar quando a Issue está pronta para execução.

Pode editar arquivos dentro do workspace e preparar PR pequeno.

### Hybrid

Usar quando o Codex executa parte documental ou técnica e o humano decide pontos de governança.

## 9. Critério para Codex Eligible

Uma Issue pode receber `codex:eligible` quando:

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

Se faltar qualquer item relevante, usar `codex:plan-required` ou `codex:human-review`.

## 9.1 Loop de continuidade do Codex

`codex:eligible` indica que a Issue pode entrar na fila de pull. A label não concede autonomia fora do contexto aprovado.

Antes da execução, o Plan Mode pode aprovar um **envelope de execução** contendo:

- objetivo do lote;
- slices explícitos ou critério de seleção;
- áreas permitidas e excluídas;
- dependências;
- validações;
- checkpoints humanos;
- condição de encerramento.

Não é obrigatório criar novo campo no Project. A fila pode ser formada por:

```text
Status = Ready
Condição de Execução = Ready for execution
Codex = codex:eligible
Epic/envelope = aprovado
Dependências = satisfeitas ou item independente
```

Ao concluir tecnicamente um slice, o Codex avalia a fila e registra:

| Decisão | Uso |
| --- | --- |
| `CONTINUE` | puxar o próximo slice elegível sem nova aprovação mecânica |
| `AWAIT_DEPENDENCY` | aguardar merge, decisão ou outra entrega |
| `CHECKPOINT` | pedir orientação por mudança, risco, conflito ou ambiguidade |
| `STOP` | encerrar o envelope ou parar por falta de candidato |

### Regra para PR pendente

O Codex pode iniciar outro slice enquanto um PR aguarda review somente quando:

- o novo slice é independente;
- a branch parte da `main`;
- não depende do conteúdo ainda não mergeado;
- não há sobreposição relevante de arquivos ou decisão;
- o envelope autoriza continuidade.

Se houver dependência, o item permanece `Ready` ou `Blocked`, conforme o caso, e a decisão é `AWAIT_DEPENDENCY`.

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
- PR foi mergeado;
- Issue foi fechada;
- Project foi atualizado para Done;
- decisões relevantes foram documentadas.

Preparar um PR e decidir `CONTINUE` não move a Issue automaticamente para `Done`.

## 15. Automação operacional versus automação real

Nesta fase, automação significa padronização operacional: checklist, nomenclatura, labels, campos e fluxo repetível.

Automação real pode ser criada futuramente, por exemplo:

- templates de Issue;
- templates de PR;
- GitHub Actions para validar título;
- GitHub Actions para validar labels;
- script para criar labels;
- automações do Project.

Essas automações devem ser tratadas em Issues próprias, com escopo explícito.
