# AGENTS.md

Instrucoes operacionais para uso do Codex neste repositorio.

## Contexto do projeto

O `erp-docflow` esta na Phase 0.

O objetivo da Phase 0 e criar o sistema operacional do projeto antes de iniciar codigo de produto.

Ambiente oficial atual:

```text
Windows host
Ubuntu-20.04 WSL compartilhada
VS Code em WSL
Codex extension
```

O uso principal do Codex deve ocorrer pela Codex extension no VS Code remoto WSL.

Uso opcional:

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
- nao criar codigo de produto durante a Phase 0;
- nao criar deploy;
- nao usar secrets;
- nao alterar ADR aceito sem novo ADR;
- nao usar `danger-full-access` como padrao.

## Loop de continuidade

O Codex pode operar em loop dentro de um envelope de execucao aprovado em Plan Mode.

O envelope pode abranger mais de um slice e deve indicar:

- objetivo do lote;
- slices ou criterios de selecao;
- areas permitidas;
- fora de escopo;
- dependencias;
- validacoes;
- checkpoints humanos;
- condicao de encerramento.

Aprovado o envelope, o Codex nao deve pedir nova autorizacao mecanica ao fim de cada slice.

Depois de preparar a entrega tecnica de um slice, deve avaliar a fila e registrar uma das decisoes:

```text
CONTINUE
AWAIT_DEPENDENCY
CHECKPOINT
STOP
```

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

