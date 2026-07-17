# AGENTS.md

Instrucoes operacionais para uso do Codex neste repositorio.

## Contexto do projeto

O baseline da Phase 0 esta concluido. A Phase 1 esta aberta em refinamento, mas nenhuma slice de codigo esta automaticamente autorizada.

Antes de executar, consultar:

1. `docs/project/PROJECT_STATUS.md` para fase, gate e fila candidata;
2. a Issue e o envelope aprovado para escopo e autorizacao;
3. `docs/operations/FLUXO_GITHUB_PROJECT.md` para lifecycle e prontidao;
4. `docs/operations/ESTRATEGIA_GIT.md` para branch, PR e merge;
5. este arquivo para guardrails especificos do Codex.

O portal `docs/README.md` define a matriz de autoridade. Quando documentos divergirem, o Codex nao deve combinar regras silenciosamente: deve usar a fonte primaria, registrar a contradicao e pedir checkpoint se ela alterar a execucao.

Ambiente oficial atual:

```text
Windows host
Ubuntu-20.04 WSL compartilhada
VS Code em WSL
Codex extension
```

O uso principal do Codex deve ocorrer pela Codex extension no VS Code remoto WSL.

O caminho do checkout depende do host. Neste `app-host`, o inventário operacional define `/srv/apps/erp-docflow`; em uma WSL de desenvolvimento pessoal, os runbooks usam `~/projetos/erp-docflow` como padrão genérico. Consultar `/srv/ops/projects.yml` quando ele existir.

Uso opcional no caminho genérico:

```bash
cd ~/projetos/erp-docflow
codex
```

## Fluxo obrigatorio

O Codex deve trabalhar com autonomia alta, mas controlada por:

```text
Issue -> branch -> commits -> Pull Request -> CI quando existir -> review humana -> squash merge
```

Regras:

- nao trabalhar sem Issue clara;
- nao trabalhar direto na `main`;
- confirmar escopo, fora de escopo e criterios de aceite pela Issue e pelo envelope aprovado antes de editar;
- manter PRs pequenos e revisaveis;
- nao fazer merge automatico;
- nao iniciar codigo de produto enquanto a slice da Phase 1 permanecer em `Precisa Especificacao` ou fora de envelope aprovado;
- nao criar deploy;
- nao usar secrets;
- nao alterar ADR aceito sem novo ADR;
- nao usar `danger-full-access` como padrao.

## Loop de continuidade

O Codex pode operar em loop dentro de um envelope de execucao aprovado em Plan Mode.

O envelope pode abranger mais de um slice e deve indicar:

- estado `Rascunho`, `Aprovado`, `Pausado` ou `Encerrado`;
- responsavel, data e referencia da aprovacao;
- objetivo do lote;
- slices ou criterios de selecao;
- areas permitidas;
- paths e ownership quando houver paralelismo;
- fora de escopo;
- dependencias;
- validacoes;
- checkpoints humanos;
- condicao de encerramento.

`Rascunho` nao autoriza slice. `Aprovado` autoriza somente o escopo registrado. `Pausado` impede iniciar nova slice. `Encerrado` exige novo envelope ou nova revisao aprovada para retomar.

O corpo da Epic ou Issue governante mantem o estado corrente e a evidencia duravel. Mudanca de limites, ownership ou exclusoes exige revisao humana registrada antes de continuar.

Aprovado o envelope, o Codex nao deve pedir nova autorizacao mecanica ao fim de cada slice.

Depois de preparar a entrega tecnica de um slice, deve avaliar a fila e registrar uma das decisoes:

```text
CONTINUE
AWAIT_DEPENDENCY
CHECKPOINT
STOP
```

Semantica operacional:

- `CONTINUE`: proximo item elegivel dentro do envelope;
- `AWAIT_DEPENDENCY`: dependencia conhecida e esperada, sem nova decisao humana;
- `CHECKPOINT`: ambiguidade, risco, mudanca ou dependencia que exige decisao/acao humana nao prevista;
- `STOP`: envelope encerrado ou nenhum candidato elegivel.

Selecionar exatamente um outcome nesta ordem:

1. envelope encerrado ou sem candidato: `STOP`;
2. decisao, risco, conflito ou acao humana nao prevista: `CHECKPOINT`;
3. dependencia conhecida e esperada: `AWAIT_DEPENDENCY`;
4. proximo item elegivel: `CONTINUE`.

Registrar o outcome na descricao do PR com fato, referencia ao envelope e condicao de retomada. Sem PR, registrar em comentario na Issue ou Epic correspondente.

Pode usar `CONTINUE` quando o proximo slice:

- esta pronto para execucao;
- pertence ao envelope aprovado;
- tem dependencias satisfeitas ou e independente;
- nao depende de PR ainda nao mergeado;
- nao conflita com branch ou PR em andamento;
- nao introduz decisao nova;
- nao toca area excluida ou protegida;
- tem validacoes conhecidas.

O Codex pode iniciar um slice independente enquanto outro PR aguarda review, partindo da `main`, sem sobreposicao relevante e quando o envelope permitir.

Slice dependente deve aguardar o merge. Branch ou PR empilhado exige autorizacao explicita no envelope.

O loop seleciona e executa trabalho. Ele nao autoriza automerge, merge pelo Codex ou expansao silenciosa de escopo.

Preparar implementacao, validacoes, documentacao e PR draft conclui tecnicamente o slice para fins do loop. Mover a Issue para `Review` exige PR fora de draft e efetivamente pronto para revisao humana. `Done` continua dependendo de review, squash merge, fechamento e reconciliacao do Project.

## Autorizacao versus capacidade tecnica

A Issue e o envelope dizem **o que** esta autorizado. `.codex/config.toml`, sandbox, permissoes e disponibilidade de rede dizem **o que a sessao consegue executar tecnicamente**.

Uma autorizacao de escopo nao amplia automaticamente permissao de filesystem, rede, credencial ou GitHub. Se push, PR ou outra acao autorizada estiver tecnicamente indisponivel, registrar o bloqueio; nao contornar o sandbox nem solicitar acesso mais amplo sem necessidade explicita.

## Escopo explicito obrigatorio

As seguintes alteracoes so podem ser feitas quando estiverem explicitamente previstas no escopo da Issue:

- alteracoes em `.codex/`;
- alteracoes em `AGENTS.md`;
- alteracoes de CI;
- alteracoes em ADRs aceitos;
- alteracoes de branch protection.

Se a Issue nao citar explicitamente uma dessas areas, o Codex deve parar e pedir decisao humana antes de alterar.

## Niveis de uso

### Leitura

Usar para:

- inspecionar arquivos;
- entender documentacao;
- revisar PRs;
- analisar Issues;
- levantar riscos.

Nao editar arquivos neste nivel.

### Plan

Usar quando a Issue ainda precisar de:

- escopo;
- decomposicao;
- criterios de aceite;
- decisao humana;
- analise de riscos;
- avaliacao de impacto.

Nao editar arquivos neste nivel.

### Workspace-write

Usar para executar Issues verificadas.

Permitido:

- editar arquivos dentro do workspace;
- criar arquivos previstos na Issue;
- executar validacoes locais;
- preparar commits pequenos.

Nao permitido:

- escrever fora do workspace;
- acessar secrets;
- alterar configuracoes globais da maquina;
- executar deploy;
- automatizar merge.

### Execucao local

Usar para comandos locais de leitura, validacao e Git dentro do workspace.

Validacoes devem ser proporcionais ao escopo da Issue.

### Danger-full-access

`danger-full-access` e proibido como padrao.

So pode ser usado como excecao explicita, temporaria e justificada pelo humano.

## Quando parar e pedir decisao humana

O fim de um slice, isoladamente, nao e motivo para parar.

O Codex deve parar e pedir decisao humana quando:

- a Issue estiver vaga;
- a Issue nao tiver criterios de aceite;
- a mudanca sair do escopo da Issue;
- houver impacto arquitetural;
- houver alteracao de ADR aceito;
- houver mudanca em seguranca;
- houver mudanca em permissoes;
- houver mudanca de banco;
- houver mudanca de storage;
- houver mudanca de deploy;
- houver mudanca em CI critico;
- houver mudanca em branch protection;
- houver mudanca em fluxo de aceite;
- for necessario acessar segredo, credencial ou dado real;
- for necessario comando destrutivo;
- for necessario escrever fora do workspace;
- for necessario acesso amplo de rede;
- for necessario alterar `.codex/`, `AGENTS.md`, CI, ADR aceito ou branch protection sem escopo explicito na Issue.

O checkpoint deve ser curto e conter:

- fato observado;
- impacto no envelope ou no proximo slice;
- opcoes viaveis;
- recomendacao do Codex.

## Comandos permitidos

Comandos de leitura e inspecao:

```bash
pwd
ls
find
rg
sed
cat
```

Comandos Git de leitura:

```bash
git status
git diff
git log
git show
```

Comandos Git seguros quando a Issue estiver executavel:

```bash
git switch -c <branch>
git add <arquivos>
git commit -m "<mensagem>"
git push -u origin <branch>
```

O nome da branch deve seguir o padrao canonico de `docs/operations/ESTRATEGIA_GIT.md`; outros documentos apenas demonstram o procedimento.

Comandos GitHub CLI permitidos:

```bash
gh issue view <numero>
gh pr view
gh pr checks
gh pr create
```

Comandos de validacao local permitidos quando existirem no projeto:

```bash
pytest
pnpm test
pnpm lint
pnpm typecheck
docker compose config
```

Instalacao de dependencias so deve ocorrer quando a Issue permitir e o humano aprovar.

Os comandos acima descrevem operacoes admitidas pelo processo. Eles continuam sujeitos as permissoes tecnicas da sessao e ao escopo do envelope.

## Comandos proibidos

Comandos proibidos:

```bash
git reset --hard
git checkout -- <file>
git clean -fd
git push --force
git push --force-with-lease
gh pr merge
gh pr close
gh repo delete
gh secret *
```

Tambem sao proibidos:

- `rm -rf` fora de diretorios gerados e claramente descartaveis;
- comandos com secrets em linha de comando;
- deploy;
- migracao de producao;
- alteracao de branch protection sem Issue explicita;
- automerge;
- uso de `danger-full-access` como modo padrao.

## Documentacao e ADRs

Atualizar documentacao quando comportamento, fluxo ou decisao mudar.

ADRs aceitos nao devem ser editados como documentos vivos comuns.

Quando uma decisao aceita mudar de forma relevante:

- criar novo ADR;
- referenciar o ADR anterior;
- manter rastreabilidade.

Decisoes relevantes nao devem ficar apenas no chat.

## Criterios de aceite para trabalho assistido por Codex

Antes de concluir uma tarefa, o Codex deve verificar:

- a Issue foi respeitada;
- nao houve mudanca fora de escopo;
- arquivos alterados fazem sentido para o slice;
- validacoes cabiveis foram executadas ou a ausencia delas foi registrada;
- documentacao afetada foi atualizada;
- ADR e rastreabilidade foram considerados quando aplicavel;
- nao foram criados secrets, deploy, automerge ou codigo de produto indevido.
- a decisao de continuidade foi registrada como `CONTINUE`, `AWAIT_DEPENDENCY`, `CHECKPOINT` ou `STOP`.
- o estado e o gate em `docs/project/PROJECT_STATUS.md` continuam corretos ou foram atualizados no mesmo PR.
