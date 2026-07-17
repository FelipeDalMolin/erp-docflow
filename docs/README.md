# Portal da documentação

- **Classe:** índice canônico
- **Estado:** vigente
- **Audiência:** contribuidores, revisores, Codex e responsáveis por produto/arquitetura
- **Atualizar quando:** um documento canônico for criado, substituído, reclassificado ou movido

Este é o ponto de entrada para a documentação do `erp-docflow`. Ele organiza os artefatos por pergunta e autoridade, sem transformar índices, diagramas ou registros de descoberta em novas fontes de decisão.

O estado atual do projeto e o próximo gate estão em [Status do projeto](project/PROJECT_STATUS.md).

## Trilhas de leitura

### Começar ou executar uma Issue

1. [Status do projeto](project/PROJECT_STATUS.md)
2. [Modelo operacional](project/MODELO_OPERACIONAL_DO_PROJETO.md)
3. [Fluxo do GitHub Project](operations/FLUXO_GITHUB_PROJECT.md)
4. [Estratégia Git](operations/ESTRATEGIA_GIT.md)
5. [Runbook VS Code, WSL, Git e GitHub CLI](operations/FLUXO_VSCODE_GIT_GITHUB_CLI.md)
6. [`AGENTS.md`](../AGENTS.md), quando houver uso do Codex

### Entender produto e arquitetura planejada

1. [Roadmap](project/ROADMAP.md)
2. [Arquitetura de referência](architecture/ARCHITECTURE.md)
3. [Pipeline documental](architecture/DOCUMENT_PIPELINE.md)
4. [Baseline conceitual de dados](architecture/DATA_MODEL_BASELINE.md)
5. [Estratégia de providers](architecture/PROVIDER_STRATEGY.md)
6. [Glossário documental](architecture/GLOSSARIO_DOCUMENTAL.md)
7. [Catálogo UML](uml/README.md)

### Entender decisões e impacto

1. [Governança de ADRs](adr/README.md)
2. [Índice de ADRs](traceability/adr-index.md)
3. [Mapa de decisões](traceability/decision-map.md)
4. [Mapa de documentos](traceability/document-map.md)
5. [Matriz de impacto](traceability/impact-matrix.md)

### Entender ambiente e operação local

1. [Ambientes](operations/AMBIENTES.md)
2. [WSL multi-projetos](operations/WSL_MULTI_PROJETOS.md)
3. [Runbook VS Code, WSL, Git e GitHub CLI](operations/FLUXO_VSCODE_GIT_GITHUB_CLI.md)

## Matriz de autoridade

| Pergunta | Fonte primária | Papel das demais fontes |
| --- | --- | --- |
| Qual é o estado atual e o próximo gate? | [PROJECT_STATUS.md](project/PROJECT_STATUS.md) | Issues/PRs fornecem a evidência operacional. |
| Quais fases, resultados e gates existem? | [ROADMAP.md](project/ROADMAP.md) | O status registra a posição atual; Epics decompõem o trabalho. |
| Como o projeto governa Issues, PRs, decisões e rastreabilidade? | [MODELO_OPERACIONAL_DO_PROJETO.md](project/MODELO_OPERACIONAL_DO_PROJETO.md) | Documentos especializados detalham cada mecanismo. |
| Qual é o lifecycle de um item e quando ele está executável? | [FLUXO_GITHUB_PROJECT.md](operations/FLUXO_GITHUB_PROJECT.md) | Templates aplicam o vocabulário; o Project exibe o estado. |
| Quais são as regras de branch, commit, PR e merge? | [ESTRATEGIA_GIT.md](operations/ESTRATEGIA_GIT.md) | O runbook mostra comandos; `AGENTS.md` adiciona limites do Codex. |
| O que o Codex pode fazer? | [`AGENTS.md`](../AGENTS.md) | [`.codex/config.toml`](../.codex/config.toml) define capacidade técnica local; a Issue/envelope concede escopo. |
| Por que uma decisão arquitetural foi tomada? | ADR aplicável em [`docs/adr/`](adr/README.md) | Arquitetura, mapas e UML devem derivar da decisão e respeitar seu status. |
| Como o produto deverá funcionar? | [ARCHITECTURE.md](architecture/ARCHITECTURE.md) e documentos de domínio | Roadmap define ordem; UML representa visualmente; nenhum deles prova implementação. |
| O que está implementado? | Código, testes e contratos executáveis | Mapas registram a evidência da Issue/PR quando código existir. |

Quando duas fontes divergirem, não combinar regras silenciosamente. Usar a fonte primária da pergunta, verificar ADRs aplicáveis e abrir uma Issue para resolver a inconsistência.

## Classes documentais

| Classe | Finalidade | Pode criar decisão? | Exemplos |
| --- | --- | --- | --- |
| decisão | registrar contexto, decisão e consequências | sim, conforme status do ADR | `docs/adr/*.md` |
| normativo operacional | definir processo vigente e responsabilidades | não substitui ADR | modelo operacional, fluxo do Project, estratégia Git, `AGENTS.md` |
| baseline planejado | detalhar uma direção ainda não implementada | não | arquitetura, pipeline, modelo de dados, providers |
| status | registrar snapshot, evidências e gate ativo | não | `PROJECT_STATUS.md` |
| runbook | ensinar a executar um processo já definido | não | fluxo VS Code/WSL/Git/CLI, ambientes |
| índice derivado | conectar e localizar fontes | não | este portal, `docs/traceability/` e catálogos |
| evidência histórica | preservar origem, análise e perguntas | não | `docs/reviews/` |
| representação visual | explicar uma fonte em diagrama | não | `docs/uml/` |
| template de referência | padronizar corpo de Issue/PR | não | `docs/templates/` |

`docs/templates/` contém modelos de referência para copiar ou usar via CLI. Eles não são templates nativos do GitHub enquanto não existirem arquivos equivalentes em `.github/ISSUE_TEMPLATE/` ou `.github/PULL_REQUEST_TEMPLATE.md`.

A auditoria que fundamentou a organização física está em [Revisão de coerência documental](reviews/DOCUMENTATION_COHERENCE_2026-07.md).

## Estados e qualificadores

- `vigente`: processo ou índice atual;
- `aceito`: decisão ratificada;
- `aceito com revisão`: decisão válida até o gatilho registrado;
- `proposto`: hipótese ou decisão pendente, sem autorização de implementação;
- `planejado` / `não implementado`: desenho de destino sem evidência em código;
- `implementado`: comportamento com código, testes e Issue/PR rastreável;
- `histórico`: evidência preservada, não normativa;
- `substituído`: artefato sucedido por outro, mantido para rastreabilidade.

Qualificadores como `proposto` e `não implementado` devem acompanhar o conceito em índices e mapas; citar apenas o número do ADR não eleva seu status.

## Estrutura atual

```text
docs/
├── README.md                    # portal e matriz de autoridade
├── project/                     # status, roadmap e governança do projeto
├── architecture/                # arquitetura e baselines documentais planejados
├── operations/                  # ambiente, Git, GitHub Project e runbooks
├── adr/                         # decisões arquiteturais
├── reviews/                     # evidência de descoberta
├── templates/                   # modelos de referência
├── traceability/                # índices e mapas derivados
└── uml/                         # representações visuais
```

A organização física foi materializada pela Issue #69. Cada agrupamento possui um índice que delimita responsabilidade e reduz duplicação normativa. Movimentos futuros continuam exigindo Issue própria, atualização atômica de links e preservação do histórico.

## Regra de manutenção

Toda mudança documental deve verificar:

- fonte primária correta para a pergunta;
- status atual no [PROJECT_STATUS.md](project/PROJECT_STATUS.md);
- ADRs e respectivos status;
- links e mapas de rastreabilidade afetados;
- distinção entre planejado e implementado;
- Issue e PR que fornecem a evidência;
- remoção de duplicação normativa quando um link for suficiente.
