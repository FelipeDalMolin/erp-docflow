# Fluxo VS Code, Git e GitHub CLI

- **Classe:** runbook operacional
- **Estado:** vigente
- **Autoridade:** sequência prática de comandos; regras pertencem às fontes especializadas
- **Atualizar quando:** ambiente oficial ou procedimento local/CLI mudar

Este documento define o procedimento operacional para trabalhar no `erp-docflow` usando VS Code remoto no WSL, Git e GitHub CLI.

Ele complementa o [Fluxo do GitHub Project](FLUXO_GITHUB_PROJECT.md) e a [Estratégia Git](ESTRATEGIA_GIT.md): essas fontes definem as regras; este documento demonstra como executá-las.

## 1. Ambiente oficial

Ambiente de trabalho principal:

```text
Windows host
Ubuntu WSL conforme ambiente vigente
VS Code remoto no WSL
Git
GitHub CLI
Codex extension
```

Diretório padrão do repositório:

```text
~/projetos/erp-docflow
```

Dados operacionais fora do Git:

```text
/mnt/e/erp-docflow-data
```

A distribuição `docker-desktop` não deve ser usada como shell principal de desenvolvimento.

Versão atual e alvo de migração não devem ser inferidos deste runbook. Consultar [Ambientes](AMBIENTES.md) e [WSL multi-projetos](WSL_MULTI_PROJETOS.md).

## 2. Fonte da verdade

A fonte da verdade do trabalho é o GitHub; a matriz de autoridade interna está no [portal documental](README.md):

```text
Issue -> Branch -> Commit -> Pull Request -> Review humana -> Squash merge
```

O chat pode ajudar a pensar, mas decisões relevantes devem terminar em documentação, Issue, PR ou ADR.

Não executar trabalho relevante sem Issue clara.

## 3. Verificação inicial no WSL

Antes de trabalhar:

```bash
git status
pwd
gh auth status
```

O diretório esperado deve ser:

```text
~/projetos/erp-docflow
```

Se o repositório estiver em `/mnt/c` ou `/mnt/e`, considerar mover o código para o filesystem Linux do WSL antes de executar desenvolvimento.

## 4. Consultar Issue

Usar GitHub CLI para consultar a Issue:

```bash
gh issue view <numero>
```

Verificar:

```text
[ ] Objetivo claro.
[ ] Escopo claro.
[ ] Fora de escopo claro.
[ ] Critérios de aceite verificáveis.
[ ] Labels/tags coerentes.
[ ] Condição de execução adequada.
[ ] Modo de execução adequado.
[ ] Nenhuma decisão humana pendente.
```

Se faltar escopo ou critério de aceite, usar Codex em modo Plan. Não editar arquivos ainda.

## 5. Criar Epic, Issue ou sub-issue pelo GitHub CLI

A criação de itens pode ser manual pelo GitHub web ou assistida pelo GitHub CLI.

Os arquivos em `docs/templates/` são corpos de referência. Eles existem, mas não são formulários nativos do GitHub.

Antes de usar `--label`, verificar se a taxonomia alvo já foi criada:

```bash
gh label list
```

Se não existir, criar o item sem improvisar outra label e registrar o gap operacional.

### 5.1 Criar Epic

Exemplo:

```bash
gh issue create \
  --title "[E0] Sistema operacional do projeto" \
  --body-file docs/templates/epic.md
```

Adicionar labels alvo somente depois de confirmá-las no repositório.

### 5.2 Criar Issue/Slice

Exemplo:

```bash
gh issue create \
  --title "[S1.01] Definir workspace e monorepo mínimo" \
  --body-file docs/templates/issue-slice.md
```

### 5.3 Criar sub-issue

Exemplo:

```bash
gh issue create \
  --title "[S1.01.01] Validar layout do workspace" \
  --body-file docs/templates/sub-issue.md
```

No corpo da sub-issue, referenciar a Issue pai.

Exemplo:

```text
Issue pai: #<numero>
```

## 6. Conferir labels/tags

Após criar um item, conferir:

```bash
gh issue view <numero>
```

Labels mínimas recomendadas:

```text
type:<tipo>
phase:<fase>
area:<area>
status:<status-operacional>
codex:<condição-codex>
```

Se a label ainda não existir no repositório, não improvisar nome alternativo sem decisão. Registrar a necessidade de criação da label em Issue própria ou comentário.

## 7. Quando uma Issue pode virar branch

Uma Issue pode virar branch quando estiver com `Condição de Execução = Condições Verificadas` e pertencer a envelope aprovado quando aplicável.

Checklist:

```text
[ ] A Issue tem objetivo claro.
[ ] A Issue tem escopo claro.
[ ] A Issue tem fora de escopo.
[ ] A Issue tem critérios de aceite.
[ ] Não exige decisão arquitetural pendente.
[ ] Não exige secret, dado real ou deploy.
[ ] Não altera área protegida sem escopo explícito.
[ ] Pode ser entregue em PR pequeno.
```

## 8. Criar branch

O padrão canônico pertence à [Estratégia Git](ESTRATEGIA_GIT.md):

```text
<tipo>/<slice>-<resumo-curto>
<tipo>/issue-<numero>-<resumo-curto>  # quando não houver identificador de slice
```

Exemplo:

```bash
git switch main
git pull --ff-only
git switch -c feature/s1-01-workspace
```

Não trabalhar direto na `main`.

## 9. Executar mudanças

Durante a execução:

```bash
git status
git diff
```

Regras:

- manter diff pequeno;
- alterar apenas arquivos do escopo;
- não iniciar código de produto sem slice especificada, condições verificadas e envelope aprovado;
- não usar secrets;
- não executar deploy;
- não alterar ADR aceito sem novo ADR;
- não alterar branch protection;
- não alterar CI sem Issue explícita.

## 10. Validar

Validações devem ser proporcionais ao escopo.

Para documentação:

```bash
git diff --check
```

Quando existirem no projeto:

```bash
pytest
pnpm test
pnpm lint
pnpm typecheck
docker compose config
```

Se não houver validação automatizada aplicável, registrar no PR:

```text
Validação: revisão documental. Não há testes automatizados aplicáveis ao escopo.
```

## 11. Commit

Usar commits pequenos e descritivos.

Exemplos:

```bash
git add docs/FLUXO_GITHUB_PROJECT.md
git commit -m "docs(project): define fluxo do GitHub Project"
```

```bash
git add docs/FLUXO_VSCODE_GIT_GITHUB_CLI.md
git commit -m "docs(flow): define fluxo VS Code Git e GitHub CLI"
```

## 12. Push

```bash
git push -u origin <branch>
```

## 13. Criar PR

Exemplo:

```bash
gh pr create \
  --title "[S1.01] Definir workspace e monorepo mínimo" \
  --body-file docs/templates/pr.md \
  --base main \
  --head <branch>
```

O PR deve conter:

```text
## Objetivo

## Alterações

## Fora de escopo

## Validação

## Riscos e observações

## Issues relacionadas
```

Quando o PR fecha Issues ao ser mergeado, usar:

```text
Closes #<numero>
```

## 14. Review humana

O PR deve ir para review humana.

Checklist de revisão:

```text
[ ] O PR resolve a Issue.
[ ] O escopo foi respeitado.
[ ] Não há mudança acidental fora de escopo.
[ ] O diff é pequeno e revisável.
[ ] Não há secrets.
[ ] Não há deploy.
[ ] Não há automerge.
[ ] Documentação afetada foi atualizada.
[ ] ADR foi considerado quando aplicável.
```

O Codex não deve fazer merge automático.

## 15. Depois do merge

Após merge humano:

```text
[ ] Issue fechada.
[ ] Project atualizado para Done.
[ ] Branch remota removida, se desejado.
[ ] Próximas Issues desbloqueadas.
[ ] Decisões relevantes refletidas em documentação ou ADR.
```

## 16. Uso do Codex por modo

### Leitura

Usar para inspecionar arquivos, PRs, Issues e riscos.

Não editar.

### Plan

Usar quando a Issue ainda precisa de escopo, decomposição, critério de aceite ou decisão humana.

Não editar.

### Workspace-write

Usar quando a Issue está pronta para execução.

Pode editar arquivos no workspace, validar, preparar commit e PR.

## 17. Quando parar

Parar e pedir decisão humana quando:

- a Issue estiver vaga;
- não houver critérios de aceite;
- houver impacto arquitetural;
- houver alteração de ADR aceito;
- houver mudança em segurança;
- houver mudança em permissões;
- houver mudança de banco;
- houver mudança de storage;
- houver mudança de deploy;
- houver mudança em CI crítico;
- houver mudança em branch protection;
- houver necessidade de segredo, credencial ou dado real;
- houver necessidade de comando destrutivo;
- houver necessidade de escrever fora do workspace.

## 18. Templates de referência e automação futura

Este documento usa os modelos de referência já existentes em `docs/templates/`.

Automação real futura pode materializar:

- formulários nativos em `.github/ISSUE_TEMPLATE/`;
- template nativo em `.github/PULL_REQUEST_TEMPLATE.md`;
- script para criar labels;
- validação de título de Issue;
- validação de labels obrigatórias;
- automações do GitHub Project.

Essas automações devem ser tratadas em Issues próprias.
