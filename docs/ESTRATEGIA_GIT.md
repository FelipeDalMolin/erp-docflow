# Estratégia Git

Este projeto usará uma estratégia Git simples, com branches curtas, Pull Requests pequenos e squash merge.

O objetivo é manter a evolução rastreável, revisável e com baixo risco de conflito.

## 1. Branch principal

A branch principal será:

```text
main
```

A `main` deve representar o estado estável do projeto.

Ela não deve receber trabalho direto.

Mudanças devem entrar por Pull Request.

## 2. Fluxo padrão

O fluxo padrão do projeto será:

```text
Issue → branch → commits → Pull Request → CI → review → squash merge
```

## 3. Unidade de trabalho

A unidade de trabalho será a Issue.

Cada Issue executável deve preferencialmente gerar:

```text
1 branch
1 Pull Request
1 squash merge
```

Uma branch pode ter vários commits.

## 4. Nome de branches

Formato recomendado:

```text
<tipo>/<slice>-<descricao-curta>
```

Exemplos:

```text
docs/s0-01-documentacao-operacional-inicial
docs/s0-02-fluxo-github-project
chore/s0-10-ci-estrutural
feature/s1-01-bootstrap-api
fix/s1-02-healthcheck
```

Tipos comuns:

```text
docs
chore
feature
fix
refactor
test
infra
```

## 5. Commits

Commits devem ser pequenos e claros.

Exemplos:

```text
docs(project): add operational model
docs(roadmap): add phase overview
docs(git): add branch strategy
chore(ci): add structural checks
```

Português técnico também é aceitável, desde que consistente:

```text
docs(project): adiciona modelo operacional
docs(roadmap): adiciona visão das fases
```

## 6. Pull Requests

Um Pull Request deve:

- referenciar a Issue;
- ter escopo pequeno;
- explicar alterações;
- indicar fora de escopo;
- indicar validação realizada;
- atualizar documentação quando necessário;
- passar por revisão.

Exemplo de vínculo com Issue:

```text
Closes #2
```

Quando o PR for mergeado, a Issue vinculada poderá ser fechada automaticamente.

## 7. Squash merge

O padrão inicial será:

```text
squash merge
```

Isso permite vários commits na branch de trabalho, mas mantém a `main` limpa com um commit consolidado por Pull Request.

Exemplo:

```text
Branch:
docs/s0-01-documentacao-operacional-inicial

Commits:
docs(project): add operational model
docs(roadmap): add phase overview
docs(git): add branch strategy

Main após squash:
[S0.01] Criar documentação operacional inicial (#12)
```

## 8. Merge commits e rebase merge

No início, o projeto deve evitar merge commits e rebase merge como estratégia de merge na interface do GitHub.

Motivo:

- reduzir opções;
- manter histórico simples;
- evitar ruído na `main`;
- facilitar auditoria por slice.

## 9. Branch protection

Branch protection será configurada depois da criação do CI estrutural.

Configurações futuras previstas:

- exigir Pull Request antes de merge;
- exigir checks de CI;
- exigir resolução de conversas;
- impedir force push;
- impedir deleção da branch protegida;
- manter squash merge como padrão.

## 10. Trabalhando com VS Code

O VS Code será o ambiente principal de trabalho.

Fluxo local típico:

```powershell
git switch -c docs/s0-01-documentacao-operacional-inicial
# editar arquivos
git status
git diff
git add docs
git commit -m "docs(project): add initial operational documentation"
git push -u origin docs/s0-01-documentacao-operacional-inicial
gh pr create
```

## 11. Trabalhando com GitHub CLI

A GitHub CLI (`gh`) será usada para operações do dia a dia.

Comandos úteis:

```powershell
gh auth status
gh issue list
gh issue view 2
gh pr create
gh pr view --web
gh pr checks
gh pr merge --squash
```

## 12. O que evitar

Evitar:

- trabalhar direto na `main`;
- misturar várias Issues no mesmo PR;
- abrir PRs grandes demais;
- deixar branches longas;
- alterar arquitetura sem ADR;
- fazer force push sem necessidade;
- deixar decisões apenas no chat;
- aceitar mudanças do Codex sem revisão.

## 13. Critério para merge

Um PR só deve ser mergeado quando:

- escopo estiver correto;
- revisão humana estiver concluída;
- CI passar, quando existir;
- documentação estiver atualizada;
- ADR estiver atualizado, se aplicável;
- traceability estiver atualizada, se aplicável;
- não houver mudanças fora do escopo.

## 14. Diretriz final

A estratégia Git deve favorecer:

```text
pequenas mudanças
baixo risco
histórico limpo
revisão fácil
rastreabilidade
```