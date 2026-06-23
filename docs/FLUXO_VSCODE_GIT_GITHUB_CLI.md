# Fluxo VS Code, Git e GitHub CLI

Este documento define o procedimento operacional para trabalhar no `erp-docflow` usando VS Code remoto no WSL, Git e GitHub CLI.

Ele complementa `docs/FLUXO_GITHUB_PROJECT.md`: o Project define a governança dos itens; este documento define como executar o fluxo no ambiente local e no GitHub.

## 1. Ambiente oficial

Ambiente de trabalho principal:

```text
Windows host
Ubuntu WSL
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

## 2. Fonte da verdade

A fonte da verdade do trabalho é o GitHub:

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

### 5.1 Criar Epic

Exemplo:

```bash
gh issue create \
  --title "[E0] Sistema operacional do projeto" \
  --body-file docs/templates/epic.md \
  --label "type:epic" \
  --label "phase:0" \
  --label "status:needs-plan"
```

Se o template ainda não existir, criar a Issue manualmente com corpo contendo objetivo, escopo, fora de escopo e critério de conclusão.

### 5.2 Criar Issue/Slice

Exemplo:

```bash
gh issue create \
  --title "[S0.04] Criar templates de Issue e PR" \
  --body-file docs/templates/issue-slice.md \
  --label "type:slice" \
  --label "phase:0" \
  --label "area:docs" \
  --label "codex:plan-required"
```

### 5.3 Criar sub-issue

Exemplo:

```bash
gh issue create \
  --title "[S0.04.01] Criar template de Issue Slice" \
  --body-file docs/templates/sub-issue.md \
  --label "type:sub-issue" \
  --label "phase:0" \
  --label "area:docs" \
  --label "codex:eligible"
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

Uma Issue pode virar branch quando estiver `Ready for execution` ou equivalente.

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

Padrão de branch:

```text
phase0/<numero-issue>-<resumo-curto>
docs/<numero-issue>-<resumo-curto>
adr/<numero-issue>-<resumo-curto>
chore/<numero-issue>-<resumo-curto>
```

Exemplo:

```bash
git switch main
git pull --ff-only
git switch -c docs/s0-04-templates-issue-pr
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
- não criar código de produto na Phase 0;
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
  --title "[S0.02/S0.03] Documentar fluxos de Project e execução local" \
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

## 18. Relação com templates futuros

Este documento define o procedimento manual e assistido.

Automação real futura pode incluir:

- template de Epic;
- template de Issue/Slice;
- template de sub-issue;
- template de PR;
- script para criar labels;
- validação de título de Issue;
- validação de labels obrigatórias;
- automações do GitHub Project.

Essas automações devem ser tratadas em Issues próprias.
