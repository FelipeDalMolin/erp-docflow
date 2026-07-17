# Revisão de coerência documental — julho de 2026

- **Classe:** evidência histórica
- **Estado:** concluída no escopo da Issue #69
- **Pode criar decisão:** não
- **Fonte vigente após a revisão:** [Portal da documentação](../README.md) e fontes indicadas em sua matriz de autoridade

## Objetivo

Registrar conflitos, redundâncias e lacunas encontrados durante a reorganização física de `docs/`, distinguindo correções objetivas de decisões que continuam exigindo trabalho próprio.

## Conflitos objetivos corrigidos

| Achado | Correção |
| --- | --- |
| O status ainda dizia que a #65 estava em andamento após o merge do PR #68. | O snapshot passou a registrar #65 integrada e #69 como hardening corrente. |
| `~/projetos/erp-docflow` aparecia como path universal, enquanto o `app-host` usa `/srv/apps/erp-docflow`. | Os runbooks agora separam WSL pessoal de host operacional e apontam o inventário local como autoridade da máquina. |
| O portal exibia a árvore plana e dizia que os documentos não seriam movidos. | A árvore, os links e a regra de manutenção foram atualizados para a estrutura materializada. |
| A CI exigia os paths antigos. | A lista de arquivos canônicos passou a exigir os três agrupamentos e seus índices. |

## Redundâncias delimitadas

| Sobreposição | Fronteira estabelecida |
| --- | --- |
| Modelo operacional × fluxo do GitHub Project | O modelo governa o ciclo amplo; o fluxo é a fonte dos estados, campos e prontidão. |
| Estratégia Git × runbook VS Code/Git/CLI | A estratégia define política; o runbook contém comandos e exemplos. |
| Ambientes × WSL multi-projetos | Ambientes resume responsabilidades; WSL detalha preparação e isolamento. |
| Arquitetura × pipeline × baseline de dados | Arquitetura define boundaries; pipeline define sequência/artefatos; baseline define conceitos e invariantes. |
| Roadmap × status | Roadmap mantém fases permanentes; status mantém o snapshot e o gate atual. |

Os índices em `project/`, `architecture/` e `operations/` tornam essas fronteiras explícitas. Não foi removido conteúdo apenas por repetição textual quando ele ainda fornece contexto local necessário.

## Lacunas que permanecem rastreadas

- A taxonomia real de labels e campos ainda deve ser materializada pela Issue #66.
- Outcomes e semântica durável do envelope do Codex continuam na Issue #67; o ADR-0017 não foi alterado.
- Runtimes, gerenciadores e layout do monorepo continuam decisão da #33 e do gate da Phase 1.
- Segurança e providers externos continuam bloqueados pelos ADR-0015 e ADR-0016 enquanto estiverem propostos.
- Os templates em `docs/templates/` continuam referências, não templates nativos do GitHub.

## Verificações de consistência

- Phase 0 encerrada e Phase 1 em refinamento aparecem de forma coerente nas fontes vigentes.
- A escolha do primeiro perfil documental permanece no gate da Phase 3/#43.
- Merge continua sendo ação humana nas fontes normativas.
- Baselines planejados não são descritos como implementação existente.
- Nenhum ADR aceito teve seu conteúdo decisório modificado nesta revisão.
