# Modelo Operacional do Projeto

Este projeto tem como objetivo construir uma plataforma ERP/GED **on-prem first**, com arquitetura **cloud-like**, focada em materialização documental, versionamento, revisão humana, aceite, auditoria e evolução futura para fluxos financeiros, contábeis, geração documental e integrações.

A proposta do projeto não é começar criando um ERP completo de uma vez. O objetivo inicial é construir uma base confiável para que documentos, arquivos, decisões, revisões, aceite humano, vínculos financeiros e histórico possam evoluir de forma rastreável.

## 1. Visão geral

O projeto será conduzido como um sistema de trabalho controlado, baseado em:

- GitHub Repository;
- GitHub Project;
- Issues;
- branches curtas;
- Pull Requests;
- CI/CD;
- ADRs;
- rastreabilidade;
- UMLs;
- revisão humana;
- uso controlado do Codex.

O fluxo padrão será:

```text
Issue → branch → commits → Pull Request → CI → review → squash merge
```

## 2. Fonte da verdade

A fonte da verdade do projeto será o repositório GitHub.

O repositório deve armazenar:

- código;
- documentação;
- ADRs;
- UMLs;
- mapas de rastreabilidade;
- templates;
- configuração de CI/CD;
- instruções para Codex;
- histórico de evolução via commits e Pull Requests.

O GitHub Project será usado como painel de acompanhamento, mas não substitui o repositório.

## 3. Organização do trabalho

O trabalho será dividido em fases e slices.

Uma fase representa uma etapa maior do projeto.

Um slice representa uma unidade pequena, revisável e executável.

Exemplo:

```text
Phase 0 — Sistema do Projeto
├── [S0.01] Criar documentação operacional inicial
├── [S0.02] Definir fluxo do GitHub Project
├── [S0.03] Definir fluxo VS Code, Git e GitHub CLI
├── [S0.04] Criar AGENTS.md e configuração Codex
└── ...
```

Cada slice deve preferencialmente gerar:

```text
1 Issue
1 branch
N commits
1 Pull Request
1 squash merge
```

## 4. Papel das Issues

Issues representam unidades de trabalho.

Uma Issue deve conter, sempre que possível:

- objetivo;
- contexto;
- escopo;
- fora de escopo;
- critérios de aceite;
- validação esperada;
- relação com ADRs;
- relação com documentação;
- impacto em módulos, rotas, entidades ou infraestrutura, quando aplicável.

Issues vagas devem permanecer em descoberta ou especificação. Elas não devem ser executadas diretamente.

## 5. Papel dos Pull Requests

Pull Requests representam propostas de mudança.

Um PR deve:

- referenciar a Issue correspondente;
- ter escopo pequeno;
- explicar o que foi alterado;
- informar o que ficou fora de escopo;
- indicar documentação afetada;
- indicar validações realizadas;
- passar por revisão antes do merge.

O padrão de merge será:

```text
squash merge
```

Isso permite que a branch possua vários commits durante o trabalho, mas que a `main` receba apenas um commit consolidado por slice.

## 6. Papel dos ADRs

ADRs são Architecture Decision Records.

Eles registram decisões arquiteturais importantes.

Exemplos de decisões que devem virar ADR:

- escolha de arquitetura on-prem first;
- uso de modular monolith;
- uso de MinIO como object storage;
- uso de PostgreSQL;
- uso de DocumentEnvelope como núcleo GED;
- estratégia de revisão humana e aceite;
- uso do Codex no fluxo de desenvolvimento;
- estratégia de CI/CD;
- estratégia de autenticação e permissões.

Regra geral:

- se a decisão mudar de forma relevante, criar novo ADR;
- não apagar o ADR antigo;
- marcar o ADR antigo como substituído, complementado ou obsoleto;
- manter rastreabilidade entre ADRs e artefatos afetados.

## 7. Papel da rastreabilidade

A rastreabilidade conecta decisões, documentos, módulos, rotas, entidades, diagramas e Issues.

A pasta `docs/traceability/` deve apoiar perguntas como:

- qual ADR justifica esta decisão?
- qual módulo implementa este conceito?
- quais rotas afetam esta entidade?
- quais diagramas representam este fluxo?
- qual documentação precisa ser atualizada se uma decisão mudar?
- qual o impacto de alterar o DocumentEnvelope?
- qual Issue ou PR introduziu determinado comportamento?

A rastreabilidade evita que o projeto se transforme em código e documentação soltos.

## 8. Papel das UMLs

A pasta `docs/uml/` armazenará diagramas estruturais e comportamentais.

Tipos previstos:

- contexto;
- deployment;
- casos de uso;
- atividades;
- componentes;
- classes de domínio;
- sequência;
- estados.

Os diagramas devem apoiar o entendimento do sistema e devem ser atualizados quando houver mudança relevante em fluxos, entidades, estados, módulos ou integrações.

## 9. Papel do Codex

O Codex será usado como apoio para execução e revisão, mas não será a fonte de decisão arquitetural.

O Codex poderá atuar em:

- criação de arquivos;
- implementação de slices;
- refatorações pequenas;
- revisão de PRs;
- atualização de documentação;
- geração de testes;
- apoio em CI/CD.

O Codex não deve decidir sozinho:

- mudança de arquitetura;
- troca de banco;
- troca de storage;
- mudança em fluxo de aceite;
- mudança em segurança;
- mudança em deploy;
- alteração de ADR aceito;
- implementação fora do escopo da Issue.

O uso do Codex deve respeitar:

- Issue clara;
- escopo definido;
- critérios de aceite;
- condição de execução verificada;
- modo de execução definido;
- revisão humana.

## 10. Condição de Execução

O campo `Condição de Execução` no GitHub Project indica se uma Issue está pronta para ser trabalhada.

Valores previstos:

```text
Não Verificado
Condições Verificadas
Precisa Especificação
Precisa ADR
Precisa Decisão Humana
Bloqueado
```

Uma Issue só deve ser executada quando:

```text
Condição de Execução = Condições Verificadas
```

## 11. Modo de Execução

O campo `Modo de Execução` indica como a Issue será trabalhada.

Valores previstos:

```text
Não Definido
Manual
Assistido por Codex
Somente Revisão Codex
Pareamento / Chat + Humano
```

O modo de execução não substitui a revisão humana. Mesmo tarefas assistidas por Codex devem passar por PR e revisão.

## 12. Fases do projeto

O projeto será conduzido por fases:

```text
Phase 0 — Sistema do Projeto
Phase 1 — Bootstrap App
Phase 2 — Núcleo GED
Phase 3 — OCR Extract Classify
Phase 4 — Review Acceptance
Phase 5 — Núcleo Financeiro
Phase 6 — Geração Documental
Phase 7 — Integrações
```

A Phase 0 deve ser concluída antes do início do código de produto.

## 13. Critério de maturidade para iniciar código

O código de produto só deve começar quando a Phase 0 tiver pelo menos:

- modelo operacional documentado;
- fluxo GitHub Project documentado;
- estratégia Git documentada;
- fluxo VS Code/GitHub CLI documentado;
- fluxo Codex documentado;
- ADR baseline criado;
- traceability baseline criado;
- UML baseline criado;
- templates de Issue e PR criados;
- CI estrutural inicial criado;
- branch protection planejada ou configurada.

## 14. O que evitar

Evitar:

- trabalhar direto na `main`;
- criar código antes da documentação mínima;
- executar tarefas grandes demais;
- misturar vários slices no mesmo PR;
- usar Codex sem Issue clara;
- alterar arquitetura sem ADR;
- deixar decisões importantes apenas no chat;
- criar documentação fora do repositório;
- tratar arquivos/documentos como anexos sem rastreabilidade;
- automatizar fluxos críticos sem revisão humana.

## 15. Diretriz final

O objetivo do projeto é construir uma solução ERP/GED confiável, auditável e evolutiva.

Para isso, o projeto deve evoluir com:

```text
clareza → rastreabilidade → revisão → versionamento → automação controlada
```

A agilidade desejada não virá de fazer tudo de uma vez, mas de criar um fluxo onde cada pequena entrega possa ser entendida, revisada, testada, rastreada e integrada com segurança.