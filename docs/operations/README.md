# Operação e execução

Este diretório reúne regras e runbooks operacionais. As fontes se complementam, sem repetir autoridade:

| Documento | Responsabilidade exclusiva |
| --- | --- |
| [Ambientes](AMBIENTES.md) | tipos de ambiente e responsabilidades gerais |
| [WSL multi-projetos](WSL_MULTI_PROJETOS.md) | isolamento e preparação detalhada da WSL |
| [Estratégia Git](ESTRATEGIA_GIT.md) | regras de branch, commit, PR e merge |
| [Fluxo do GitHub Project](FLUXO_GITHUB_PROJECT.md) | lifecycle, campos, prontidão e continuidade |
| [Runbook VS Code/Git/CLI](FLUXO_VSCODE_GIT_GITHUB_CLI.md) | comandos para aplicar regras já definidas |

## Paths por ambiente

- WSL pessoal/genérica: `~/projetos/erp-docflow`.
- Host operacional `app-host`: `/srv/apps/erp-docflow`, conforme `/srv/ops/projects.yml`.

Não manter dois checkouts como se ambos fossem a fonte corrente da mesma máquina. O inventário local prevalece para operação do host; GitHub e a `main` permanecem a fonte do código versionado.

## Limites de duplicação

- O runbook referencia a Estratégia Git em vez de redefinir políticas.
- O fluxo do Project define estados e prontidão; o modelo operacional explica a governança mais ampla.
- Ambientes resume responsabilidades; WSL contém o procedimento detalhado.
