# ADR-0021 — Ownership do shared-dev e isolamento por worktrees

Status: Aceito
Data: 2026-08-04
Decisores: FelipeDalMolin
Tags: dev, compose, worktree, shared-dev, runtime

## Contexto

Os ADRs 0004 e 0008 definem desenvolvimento em WSL e Docker Compose, mas não
determinam quem pode controlar um runtime cumulativo quando o mesmo repositório
possui múltiplas worktrees. O Compose integrado fixa o project name
`erp_docflow_dev`, publica `8100/5180`, preserva um volume PostgreSQL e resolve
bind mounts a partir do diretório de execução. Executar o modelo em outra
worktree pode, portanto, manter a identidade aparente e trocar silenciosamente
o código montado.

O checkpoint #104 reservou esta decisão para distinguir:

- checkout canônico e runtime integrado `shared-dev`;
- worktrees de slices;
- checks e migration rehearsals descartáveis;
- cutover, restart, migration e rollback do runtime cumulativo.

## Evidências vivas da decisão

Snapshot sanitizado de 2026-08-04, depois da integração da #111/PR #112:

| Elemento | Estado observado | Consequência |
| --- | --- | --- |
| checkout canônico | `/srv/apps/erp-docflow`, `main@b19a720eafd1162a3dccd5b2bad8a836a3bdbc3f`, limpo e sincronizado | root candidata a owner no perfil `app-host` |
| host | WSL2, Ubuntu 24.04, Docker Engine 29.6.1, Compose 5.3.0 | perfil operacional distinto da WSL pessoal descrita pelo ADR-0004 |
| worktrees | 18 registradas; `preserve-local-20260804T125151Z` está suja e sem upstream | nenhuma limpeza automática é segura |
| runtime ERP legado | project `erp_docflow_dev`, API/web healthy em 8100/5180 | runtime ativo não nasceu da `main` atual |
| origem do runtime legado | `/srv/apps/erp-docflow-worktrees/phase1-reproduction/compose.yml`, worktree em `83870f79` | mounts e working directory pertencem a worktree histórica |
| banco do runtime legado | nenhum container ou volume PostgreSQL ERP | primeiro PostgreSQL do `shared-dev` será uma introdução controlada de PostgreSQL/schema, não restart simples nem migração de dados legados |
| identidade | apenas labels canônicas do Compose; imagens locais mutáveis | imagem/label isolada não prova source SHA nem código bind-mounted |
| preview legado | `erp-docflow-web-preview` em 4173, sem healthcheck/labels, mount read-only de `s1-03-web`; HTTP 200 no snapshot | inventariar; owner e aposentadoria exigem follow-up próprio |
| modelo integrado | API/web/PostgreSQL, mesmo project name e mesmas portas do legado | outra execução pode adotar ou recriar recursos compartilhados |
| configuração canônica | `.env` ausente no checkout canônico | preflight do futuro cutover deve falhar fechado; não criar credencial automaticamente |
| inventário do host | `/srv/ops/projects.yml` acerta a root, mas declara branch/runtime antigos; `/srv/ops` está sujo e sem remote | permanecer somente leitura e registrar follow-up separado |

O inventário não leu nem registrou valores de `.env`, dados de negócio ou
secrets. Aceitar este ADR não muda container, porta, volume, rede, Compose,
worktree ou `/srv/ops`.

## Decisão

### Perfis e proprietário exclusivo

O `shared-dev` possui exatamente um checkout proprietário por perfil.

#### Perfil `app-host`

- root proprietária: realpath exata `/srv/apps/erp-docflow`;
- branch integrada: `main`;
- remote esperado: `origin` apontando para o repositório canônico;
- worktrees ficam sob `/srv/apps/erp-docflow-worktrees/*` e nunca são owner;
- `/srv/ops/projects.yml` informa a topologia local, mas não autoriza mutação e
  permanece somente leitura neste checkpoint.

#### Perfil `personal-wsl`

- root proprietária: checkout canônico configurado;
- default portátil: `~/projetos/erp-docflow`;
- a root deve estar no filesystem Linux da WSL;
- realpath de código sob `/mnt/c` ou `/mnt/e` é rejeitada;
- dados, exports e backups autorizados podem continuar em `/mnt/e/*-data`.

A rejeição de `/mnt/e` se aplica ao checkout/código, não aos dados operacionais
fora do Git. O perfil `app-host` observado em Ubuntu 24.04 complementa o perfil
portátil do ADR-0004; não declara migração global nem elimina a WSL pessoal.

### Estado transitório antes do cutover

O runtime em 8100/5180 iniciado por `phase1-reproduction@83870f79` é registrado
como **runtime legado**, não como `shared-dev` conforme esta decisão. Até o
cutover controlado:

- ele permanece inventariado e preservado;
- a worktree histórica não recebe autoridade para executar comandos Compose
  genéricos;
- qualquer restart, recreate, down ou mudança exige Issue operacional humana
  explícita;
- sua mera existência não autoriza a root canônica a adotá-lo ou substituí-lo.

### Autoridade dos comandos futuros

O controlador futuro será `./tools/devctl`.

- `shared status`: somente leitura; pode ser chamado de qualquer checkout para
  diagnóstico, mas sempre resolve e inspeciona a root proprietária configurada
  e o runtime reconhecido. O cwd chamador é apenas contexto para informar owner
  mismatch e nunca recebe autoridade;
- `shared preflight`: não altera working tree, configuração nem runtime; pode
  atualizar somente referências Git por `fetch` explícito e é fail-closed fora
  da root proprietária;
- `shared up`: preflight, build controlado e recreate; nunca executa migration
  e nunca expõe API/web quando a revisão atual do banco é incompatível com a
  imagem alvo;
- `shared migrate`: exige API/web paradas ou quiescentes, usa a imagem alvo,
  valida um único Alembic head, compara current/head e executa `upgrade head`
  explicitamente;
- `shared restart`: não executa build, pull ou migration e recusa reiniciar
  aplicação sobre schema incompatível;
- `check` e `migration-rehearsal`: únicos modos Compose/runtime permitidos a
  uma worktree, sempre isolados do `shared-dev`; lint, testes e builds locais
  que não controlam esse runtime continuam sujeitos ao runbook de validação.

Esses comandos ainda não existem. Esta PR define contratos e guardas
transitórios, sem antecipar sua implementação.

### Guards fail-closed do shared-dev

Antes de qualquer mutação futura do runtime, o `devctl` deve comprovar
simultaneamente:

- perfil conhecido e realpath igual à root proprietária;
- branch `main`;
- remote `origin` esperado;
- `git fetch` concluído pelo preflight, com atualização restrita às referências
  Git; `shared status` usa as referências já disponíveis e informa quando o
  frescor remoto não foi comprovado;
- `HEAD == refs/remotes/origin/main`;
- `ahead=0`, `behind=0` e árvore limpa;
- `.env` presente, ignorado pelo Git e com permissão adequada, sem expor valor;
- Docker context/daemon esperado pelo perfil;
- modelo Compose válido;
- project name, config files, working directory, portas, redes, volumes, labels
  e bind mounts inventariados;
- portas livres ou pertencentes exatamente ao runtime reconhecido;
- runtime existente compatível ou cutover explicitamente autorizado.

Branch chamada `main` não é evidência suficiente. Qualquer divergência impede
`up`, `migrate` e `restart` e produz diagnóstico sanitizado.

### Modelos Compose futuros

Ficam selecionados:

- `compose.check.yml`: modelo autônomo de check descartável;
- `compose.rehearsal.yml`: modelo autônomo de migration rehearsal;
- `compose.shared.yml`: overlay do modelo canônico apenas para identidade e
  controles do `shared-dev`.

Os dois modelos descartáveis não são overrides do `compose.yml` e não dependem
de `ports: []`, `!reset` ou `!override`. O `devctl` deve fornecer `--file` e
project name explícitos; nenhum modelo descartável usa o nome
`erp_docflow_dev`.

### Check descartável

`./tools/devctl check --issue <n>` deve provar no modelo efetivo:

- project name único `erp_docflow_check_issue_<n>_<suffix>`;
- zero portas publicadas;
- rede exclusiva da execução;
- zero volumes externos ou compartilhados;
- volumes nomeados descartáveis somente quando exclusivos, rotulados e
  pertencentes ao project name;
- labels de owner, mode e Issue em namespace próprio;
- nenhuma referência ao project, rede, volume ou container do `shared-dev`.

Sucesso remove somente o project name exato. Falha preserva evidência e imprime
o comando de cleanup exato; nunca usa `prune`, glob, project name incompleto ou
`down` sobre o runtime compartilhado.

### Migration rehearsal

`./tools/devctl migration-rehearsal --issue <n>` deve:

1. criar project name, rede e volumes exclusivos;
2. obter cópia lógica do banco sintético autorizado com
   `pg_dump --format=custom`;
3. registrar checksum, validar o archive com `pg_restore --list` e restaurar em
   database vazio, isolado e compatível, usando role não-superuser e
   `pg_restore --exit-on-error --no-owner --no-privileges`;
4. validar um único Alembic head;
5. aplicar a migration da branch;
6. executar invariantes, testes, restart e nova verificação;
7. limpar somente recursos exatos em sucesso ou preservar evidência em falha.

É proibido copiar diretamente arquivos de volume PostgreSQL. Código antigo
nunca é conectado a banco já migrado. Dumps de fonte não confiável precisam de
inspeção antes do restore, pois um archive pode conter definições capazes de
executar código no destino; o rehearsal não concede superuser ao restaurador.

### Identidade verificável do runtime

O overlay futuro usa namespace customizado; `com.docker.compose.*` permanece
reservado ao Compose:

```text
com.erp-docflow.runtime.mode=shared-dev
com.erp-docflow.runtime.profile=<profile>
com.erp-docflow.runtime.source-sha=<HEAD>
com.erp-docflow.runtime.source-path=<realpath>
com.erp-docflow.runtime.config-digest=<digest>
com.erp-docflow.runtime.credential-revision=<opaque-non-secret-id>
com.erp-docflow.runtime.started-by=devctl
```

O config digest representa o modelo efetivo normalizado e não secreto. Valores
de `.env`/secrets são excluídos antes do hash e nunca aparecem em logs,
documentação ou artifacts. Compatibilidade de credenciais não é inferida desse
digest: o tooling mantém um identificador opaco e não derivado dos valores,
alterado em inicialização/rotação, e combina sua comparação com um probe pela
imagem alvo e rede Compose, usando os mesmos componentes de credencial da
API/migration runner, além da verificação de database/user sem exibi-los.
Socket local, role administrativa ou modo `trust` do PostgreSQL não servem como
prova. Ausência, divergência ou falha de autenticação bloqueia a operação. O
identificador é evidência auxiliar, não substitui o probe; hash simples de
secret também não pode ser usado, pois permitiria tentativa offline.

`shared status` valida em conjunto:

- labels customizadas e labels canônicas do Compose;
- config files e working directory;
- bind mounts reais;
- source path, SHA, branch, ahead/behind e árvore limpa;
- image IDs/digests;
- project name, portas, redes e volumes;
- healthchecks e estado dos serviços.

Digest de imagem não prova código bind-mounted, e label isolada não substitui a
inspeção dos mounts.

### Cutover e rollback futuros

Antes do primeiro cutover, capturar sem secrets:

- Compose file, working directory, source SHA/path e config digest;
- containers, imagens/digests, labels e bind mounts;
- project name, redes, portas e volumes;
- Alembic heads/current e estado de migration, quando houver banco;
- healthchecks e nomes de variáveis sem valores;
- runtime legado em 8100/5180 e preview em 4173;
- dump lógico de qualquer PostgreSQL anterior.

Quando houver banco anterior, os writers são quiescidos antes do dump reservado
para rollback e permanecem bloqueados continuamente desde o início do dump até
o sucesso, rollback ou abandono explicitamente registrado. Esse archive custom
recebe checksum e restore-test em destino separado antes da troca; a fronteira
de escrita e o resultado ficam registrados. O primeiro cutover atualmente
observado não possui PostgreSQL ERP legado, então dump e fronteira de escrita
são registrados como `N/A`, sem inventar evidência.

O cutover separa `shared up` de `shared migrate` e usa uma sequência compatível
com schema:

1. parar ou quiescer API/web e qualquer writer;
2. preparar/recriar somente PostgreSQL e a imagem alvo, mantendo API/web
   indisponíveis;
3. executar `shared migrate` com a imagem alvo;
4. comprovar `current == head` e somente então iniciar API/web;
5. executar smoke, restart e nova verificação.

Em nenhum momento aplicação antiga ou nova pode escrever sobre schema
incompatível. Se o tooling não conseguir provar a compatibilidade, o cutover
falha fechado antes de expor os serviços.

Rollback:

- prefere forward fix;
- preserva qualquer volume novo;
- nunca conecta código antigo ao banco migrado;
- recalcula e compara o checksum imediatamente antes de qualquer restore;
- restaura somente o dump anterior cujo checksum e restore-test foram
  comprovados, sempre em database e volume vazios, distintos e preservados;
- nunca sobrescreve o volume que recebeu a migration;
- não trata a worktree `phase1-reproduction` como rollback suficiente.

O primeiro PostgreSQL integrado não possui banco ERP legado para copiar, mas
ainda exige volume novo, migration explícita e evidência de restart.

## Alternativas consideradas

### Checkout canônico em main como owner

Aceita. Alinha o runtime cumulativo ao código integrado e permite provar path,
SHA e mounts.

### Worktree dedicada e imutável como owner

Rejeitada. Mantém duas referências operacionais e facilita divergência entre
runtime e `main` integrada.

### Nenhum runtime cumulativo

Rejeitada para desenvolvimento integrado. Checks descartáveis não substituem
restart, migration e smoke cumulativos necessários antes da #40.

### Overrides do Compose para remover portas/volumes

Rejeitada para check e rehearsal. Modelos autônomos evitam depender de
semântica de merge e extensões específicas da versão do Compose.

### Cópia física de volume PostgreSQL

Rejeitada. Acopla rehearsal a versão, layout e estado interno do processo; a
cópia lógica é verificável e restaurada em destino separado.

## Consequências positivas

- elimina autoridade ambígua sobre o runtime cumulativo;
- impede worktree de trocar mounts do `shared-dev` silenciosamente;
- separa lifecycle de build, migration e restart;
- torna checks/rehearsals isolados e removíveis pelo identificador exato;
- torna source SHA/path, mounts, config e health comprováveis;
- preserva a worktree local suja e o runtime legado até cutover autorizado;
- cria rollback baseado em dados/evidência, não apenas em código antigo.

## Consequências negativas / trade-offs

- o runtime legado passa a ser não conforme até o cutover;
- a ausência de `.env` na root canônica faz o preflight falhar hoje;
- o tooling e os três modelos Compose ainda precisam ser implementados;
- mais guards aumentam o custo de operações locais deliberadas;
- `/srv/ops` e o preview 4173 exigem follow-ups externos a esta PR;
- worktrees históricas não podem ser removidas apenas porque o upstream sumiu.

## Impacto técnico

### Nesta decisão

Somente os nove documentos autorizados pela #113 são alterados. `AGENTS.md` e
os runbooks recebem guardas transitórios. Nenhum comando, Compose, workflow,
runtime, `.env`, worktree ou arquivo de `/srv/ops` muda nesta PR.

### Na futura implementação

- três PRs sequenciais implementarão preflight/status, check/rehearsal e
  controle do `shared-dev`;
- o cutover será Issue operacional pareada distinta;
- atualizar `/srv/ops/projects.yml`, limpar worktrees e decidir o preview 4173
  exigem ownership e Issues próprios.

## Fontes primárias

- [project name e precedência no Docker Compose](https://docs.docker.com/compose/how-tos/project-name/);
- [application model e labels canônicas do Compose](https://docs.docker.com/compose/intro/compose-application-model/);
- [services, labels e mounts no Compose](https://docs.docker.com/reference/compose-file/services/);
- [volumes no Compose](https://docs.docker.com/reference/compose-file/volumes/);
- [backup e restore no PostgreSQL](https://www.postgresql.org/docs/current/backup.html);
- [`pg_dump`](https://www.postgresql.org/docs/current/app-pgdump.html);
- [`pg_restore`](https://www.postgresql.org/docs/current/app-pgrestore.html);
- [`git worktree`](https://git-scm.com/docs/git-worktree.html).

## Relações

Substitui: nenhum.
Substituído por: —
Complementa: ADR-0004 e ADR-0008.
Complementado por: —
Relacionado a: ADR-0001, ADR-0003, ADR-0010 e ADR-0014.

## Revisão futura obrigatória

Revisar esta decisão quando:

- o primeiro cutover do `shared-dev` for preparado ou concluído;
- mudar root, host, distribuição WSL, Docker context ou backend de containers;
- mudar estratégia de worktrees ou runtime cumulativo;
- surgir necessidade de porta, rede ou volume compartilhado em checks;
- migration rehearsal lógico deixar de atender a versão/volume de dados;
- rollback real ou exceção operacional revelar lacuna nos guards.

Uma revisão registra nova evidência; não reescreve silenciosamente snapshots ou
cutovers anteriores.
